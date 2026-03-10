import logging
from typing import List
from .sql_verifier import VerificationResult as SQLResult
from .vector_verifier import VectorResult

logger = logging.getLogger(__name__)


def reconcile_result(
    claim_type: str,
    sql_result: SQLResult = None,
    vector_result: VectorResult = None,
) -> str:
    """
    Merges verification results into a final status.
    
    Rules:
    - If SQL verifier returns 'verified' → verified
    - If Vector verifier returns 'verified' → verified
    - If either returns 'flagged' → flagged
    - Otherwise → uncertain
    """
    if claim_type == "quantitative" and sql_result:
        return sql_result.status
    elif claim_type == "qualitative" and vector_result:
        return vector_result.status
    
    return "uncertain"
