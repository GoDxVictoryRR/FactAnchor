import uuid
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_async_session
from ...db.models import User, Report, Claim
from ...db.repositories import ReportRepository, ClaimRepository
from ...auth.middleware import get_current_user
from ...config import settings
from ...schemas.report import (
    ReportSubmitRequest, ReportSubmitResponse, ReportDetail, ClaimSummary,
    PaginatedReports, ReportListItem,
)
from ...nlp.extractor import extract_claims

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportSubmitResponse, status_code=202)
async def submit_report(
    body: ReportSubmitRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Submit a document for factual verification."""
    # 1. Create report record
    report = await ReportRepository.create(
        session, raw_text=body.text, submitted_by=user.id, title=body.title
    )

    # 2. Extract claims (synchronous — fast, <500ms for typical docs)
    claims = extract_claims(body.text)

    # 3. Bulk-insert claims
    claim_dicts = [
        {
            "report_id": report.id,
            "sequence_num": c.sequence_num,
            "claim_text": c.claim_text,
            "claim_type": c.claim_type,
            "entities": [e.model_dump() for e in c.entities],
            "char_start": c.char_start,
            "char_end": c.char_end,
        }
        for c in claims
    ]
    await ClaimRepository.bulk_create(session, claim_dicts)

    # 4. Update report
    report.total_claims = len(claims)
    report.status = "verifying"
    await session.commit()

    # 5. Dispatch Celery tasks
    from ...workers.tasks import verify_claim as verify_claim_task
    # We submit ONE task per report; the worker now handles iterating through claims
    verify_claim_task.delay(str(report.id), str(report.id))

    # 6. Return with WS URL
    ws_base = settings.BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{ws_base}/ws/reports/{report.id}/stream"
    return ReportSubmitResponse(
        report_id=report.id,
        total_claims=len(claims),
        ws_url=ws_url,
    )


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get full report with all claims."""
    report = await ReportRepository.get_by_id(session, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.submitted_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    claims = await ClaimRepository.get_by_report(session, report_id)
    return ReportDetail(
        id=report.id,
        title=report.title,
        raw_text=report.raw_text,
        status=report.status,
        confidence_score=float(report.confidence_score) if report.confidence_score is not None else None,
        confidence_hash=report.confidence_hash,
        total_claims=report.total_claims,
        verified_count=report.verified_count,
        flagged_count=report.flagged_count,
        uncertain_count=report.uncertain_count,
        claims=[ClaimSummary.model_validate(c) for c in claims],
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get("", response_model=PaginatedReports)
async def list_reports(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List reports for the authenticated user."""
    reports = await ReportRepository.list_by_user(session, user.id, page, per_page, status)
    return PaginatedReports(
        reports=[ReportListItem.model_validate(r) for r in reports],
        page=page,
        per_page=per_page,
    )
