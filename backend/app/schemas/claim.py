import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ClaimDetail(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    sequence_num: int
    claim_text: str
    claim_type: str
    entities: Optional[dict] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    status: str
    db_expected_value: Optional[str] = None
    llm_generated_sql: Optional[str] = None
    similarity_score: Optional[float] = None
    error_message: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
