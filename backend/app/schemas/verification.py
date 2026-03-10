from pydantic import BaseModel
from typing import Optional


class VerificationUpdate(BaseModel):
    """WebSocket message for a single claim update."""
    type: str = "claim_update"
    claim_id: str
    status: str
    sequence_num: int


class ReportComplete(BaseModel):
    """WebSocket message when all claims are verified."""
    type: str = "report_complete"
    confidence_score: float
    anchor: str


class WSError(BaseModel):
    """WebSocket error message."""
    type: str = "error"
    code: str
    message: str
