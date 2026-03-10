import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.verification.vector_verifier import verify_vector_claim


class TestVectorVerifier:
    """Tests for the Vector (Pinecone) verification engine."""

    def test_returns_result_with_status(self):
        """verify_vector_claim should return a result with a status field."""
        result = verify_vector_claim(
            claim_text="The company expanded into the European market",
            claim_type="qualitative",
        )
        assert result is not None
        assert hasattr(result, "status")
        assert result.status in ("verified", "flagged", "uncertain", "error")

    def test_high_similarity_returns_verified(self):
        """Scores above the threshold should return verified."""
        result = verify_vector_claim(
            claim_text="The company expanded into the European market",
            claim_type="qualitative",
        )
        # The mock returns 0.92 by default, which should be verified
        assert result.status == "verified"

    def test_result_contains_similarity_score(self):
        """The result must include the similarity score for audit trail."""
        result = verify_vector_claim(
            claim_text="Net income increased by 15% compared to last year",
            claim_type="qualitative",
        )
        assert hasattr(result, "similarity_score")
        assert isinstance(result.similarity_score, float)
        assert 0.0 <= result.similarity_score <= 1.0
