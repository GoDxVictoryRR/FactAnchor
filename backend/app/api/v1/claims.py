import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_async_session
from ...db.models import User
from ...db.repositories import ClaimRepository
from ...auth.middleware import get_current_user
from ...schemas.claim import ClaimDetail

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports/{report_id}/claims", tags=["claims"])


@router.get("", response_model=List[ClaimDetail])
async def get_claims(
    report_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get all claims for a report."""
    claims = await ClaimRepository.get_by_report(session, report_id)
    return [ClaimDetail.model_validate(c) for c in claims]
