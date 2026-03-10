import pytest
from app.verification.confidence import generate_confidence_score


class TestConfidenceScore:
    """Tests for the cryptographic confidence score generator."""

    def test_score_is_deterministic(self):
        """The same input must always produce the same hash."""
        results = [
            {"claim_id": "c1", "status": "verified"},
            {"claim_id": "c2", "status": "flagged"},
            {"claim_id": "c3", "status": "verified"},
        ]
        first = generate_confidence_score(results)
        second = generate_confidence_score(results)

        assert first["hash"] == second["hash"], "Same input must produce identical hash"
        assert first["score"] == second["score"], "Same input must produce identical score"

    def test_score_changes_when_single_result_changes(self):
        """Mutating one claim's status must produce a different hash."""
        results_a = [
            {"claim_id": "c1", "status": "verified"},
            {"claim_id": "c2", "status": "verified"},
            {"claim_id": "c3", "status": "verified"},
        ]
        results_b = [
            {"claim_id": "c1", "status": "verified"},
            {"claim_id": "c2", "status": "flagged"},  # Changed
            {"claim_id": "c3", "status": "verified"},
        ]

        hash_a = generate_confidence_score(results_a)["hash"]
        hash_b = generate_confidence_score(results_b)["hash"]

        assert hash_a != hash_b, "Different inputs must produce different hashes"

    def test_score_calculation_correctness(self):
        """10 claims: 8 verified, 1 flagged, 1 uncertain → score == 80.0"""
        results = [
            {"claim_id": f"c{i}", "status": "verified"} for i in range(8)
        ] + [
            {"claim_id": "c8", "status": "flagged"},
            {"claim_id": "c9", "status": "uncertain"},
        ]

        output = generate_confidence_score(results)
        assert output["score"] == 80.0, f"Expected 80.0, got {output['score']}"

    def test_all_verified_gives_100(self):
        """All verified claims should produce a score of 100.0."""
        results = [
            {"claim_id": f"c{i}", "status": "verified"} for i in range(5)
        ]
        output = generate_confidence_score(results)
        assert output["score"] == 100.0

    def test_all_flagged_gives_0(self):
        """All flagged claims should produce a score of 0.0."""
        results = [
            {"claim_id": f"c{i}", "status": "flagged"} for i in range(5)
        ]
        output = generate_confidence_score(results)
        assert output["score"] == 0.0

    def test_hash_is_valid_hex_string(self):
        """The hash must be a valid hexadecimal string."""
        results = [{"claim_id": "c1", "status": "verified"}]
        output = generate_confidence_score(results)

        assert isinstance(output["hash"], str)
        assert len(output["hash"]) == 64, "SHA-256 hash should be 64 hex characters"
        # Validate it's valid hex
        int(output["hash"], 16)

    def test_anchor_format(self):
        """The anchor string should be in 'score#short_hash' format."""
        results = [
            {"claim_id": "c1", "status": "verified"},
            {"claim_id": "c2", "status": "verified"},
        ]
        output = generate_confidence_score(results)
        assert "anchor" in output
        anchor = output["anchor"]
        assert "#" in anchor, "Anchor should contain '#' separator"

    def test_empty_results_handled(self):
        """Empty results list should not crash."""
        output = generate_confidence_score([])
        assert output["score"] == 0.0
        assert isinstance(output["hash"], str)

    def test_order_independent(self):
        """Hash should be the same regardless of insertion order (sorted internally)."""
        results_a = [
            {"claim_id": "c1", "status": "verified"},
            {"claim_id": "c2", "status": "flagged"},
        ]
        results_b = [
            {"claim_id": "c2", "status": "flagged"},
            {"claim_id": "c1", "status": "verified"},
        ]
        hash_a = generate_confidence_score(results_a)["hash"]
        hash_b = generate_confidence_score(results_b)["hash"]

        assert hash_a == hash_b, "Hash must be order-independent (sorted internally)"
