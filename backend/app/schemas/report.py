import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReportSubmitRequest(BaseModel):
    title: Optional[str] = None
    text: str = Field(..., max_length=100000)


class ReportSubmitResponse(BaseModel):
    report_id: uuid.UUID
    total_claims: int
    ws_url: str


class ClaimSummary(BaseModel):
    id: uuid.UUID
    sequence_num: int
    claim_text: str
    claim_type: str
    status: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    db_expected_value: Optional[str] = None
    similarity_score: Optional[float] = None

    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    raw_text: str
    status: str
    confidence_score: Optional[float] = None
    confidence_hash: Optional[str] = None
    total_claims: int
    verified_count: int
    flagged_count: int
    uncertain_count: int
    claims: List[ClaimSummary] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    status: str
    total_claims: int
    confidence_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedReports(BaseModel):
    reports: List[ReportListItem]
    page: int
    per_page: int
