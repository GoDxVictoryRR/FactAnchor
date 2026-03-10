import uuid
import logging
from typing import List, Optional
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Report, Claim, User

logger = logging.getLogger(__name__)


class ReportRepository:
    """Data access layer for Report operations."""

    @staticmethod
    async def create(session: AsyncSession, raw_text: str, submitted_by: uuid.UUID, title: Optional[str] = None) -> Report:
        report = Report(raw_text=raw_text, submitted_by=submitted_by, title=title)
        session.add(report)
        await session.flush()
        return report

    @staticmethod
    async def get_by_id(session: AsyncSession, report_id: uuid.UUID) -> Optional[Report]:
        result = await session.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_user(
        session: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
        status_filter: Optional[str] = None,
    ) -> List[Report]:
        query = select(Report).where(Report.submitted_by == user_id)
        if status_filter:
            query = query.where(Report.status == status_filter)
        query = query.order_by(Report.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_status(session: AsyncSession, report_id: uuid.UUID, status: str) -> None:
        await session.execute(update(Report).where(Report.id == report_id).values(status=status))

    @staticmethod
    async def is_all_claims_terminal(session: AsyncSession, report_id: uuid.UUID) -> bool:
        terminal_states = {"verified", "flagged", "uncertain", "error"}
        result = await session.execute(
            select(func.count()).select_from(Claim).where(
                Claim.report_id == report_id,
                Claim.status.notin_(terminal_states)
            )
        )
        non_terminal = result.scalar()
        return non_terminal == 0


class ClaimRepository:
    """Data access layer for Claim operations."""

    @staticmethod
    async def bulk_create(session: AsyncSession, claims: List[dict]) -> List[Claim]:
        claim_objects = [Claim(**c) for c in claims]
        session.add_all(claim_objects)
        await session.flush()
        return claim_objects

    @staticmethod
    async def get_by_id(session: AsyncSession, claim_id: uuid.UUID) -> Optional[Claim]:
        result = await session.execute(select(Claim).where(Claim.id == claim_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_report(session: AsyncSession, report_id: uuid.UUID) -> List[Claim]:
        result = await session.execute(
            select(Claim).where(Claim.report_id == report_id).order_by(Claim.sequence_num)
        )
        return list(result.scalars().all())
