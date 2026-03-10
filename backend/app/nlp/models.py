from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ExtractedEntity(BaseModel):
    """Represents an entity extracted by spaCy NER (e.g., MONEY, PERCENT, DATE)."""
    text: str
    label: str          # spaCy entity label: MONEY, PERCENT, DATE, ORG, etc.
    start_char: int
    end_char: int

class ExtractedClaim(BaseModel):
    """Represents a factual claim extracted from the document."""
    claim_text: str
    claim_type: Literal["quantitative", "qualitative"]
    entities: List[ExtractedEntity] = Field(default_factory=list)
    char_start: int         # position in original document
    char_end: int
    confidence: float       # NLP extraction confidence (0.0 - 1.0)
    sequence_num: int
