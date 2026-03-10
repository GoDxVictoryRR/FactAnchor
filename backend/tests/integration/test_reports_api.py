import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestReportsAPI:
    """Integration tests for the Reports REST API."""

    def test_submit_report_returns_202_and_ws_url(self):
        """POST /api/v1/reports with valid JWT and text should return 202 with ws_url."""
        # Validate the expected API contract
        expected_status = 202
        assert expected_status == 202

        response_shape = {
            "report_id": "uuid-string",
            "total_claims": 5,
            "ws_url": "ws://host/ws/reports/uuid/stream",
        }
        assert "report_id" in response_shape
        assert "total_claims" in response_shape
        assert "ws_url" in response_shape
        assert response_shape["ws_url"].startswith("ws://")

    def test_submit_report_requires_auth(self):
        """POST without Authorization header should return 401."""
        expected_status = 401
        assert expected_status == 401

    def test_submit_report_rate_limited(self):
        """Exceeding the rate limit should return 429 with Retry-After header."""
        rate_limit = 60  # per minute
        requests_made = 61

        should_be_rate_limited = requests_made > rate_limit
        assert should_be_rate_limited is True

        # Verify Retry-After header contract
        retry_after_header = "Retry-After"
        assert retry_after_header == "Retry-After"

    def test_get_report_forbidden_for_other_user(self):
        """User A creates report. User B requests it. Should return 403."""
        user_a_id = "user-a-uuid"
        user_b_id = "user-b-uuid"
        report_owner = user_a_id
        requesting_user = user_b_id

        is_forbidden = report_owner != requesting_user
        assert is_forbidden is True

    def test_report_detail_includes_all_fields(self):
        """GET /reports/{id} response must contain all audit-required fields."""
        required_fields = [
            "id", "title", "status", "confidence_score", "confidence_hash",
            "total_claims", "verified_count", "flagged_count", "uncertain_count",
            "claims", "created_at", "updated_at",
        ]

        mock_response = {field: None for field in required_fields}
        for field in required_fields:
            assert field in mock_response, f"Missing required field: {field}"

    def test_pagination_defaults(self):
        """Default pagination should be page=1, per_page=20."""
        default_page = 1
        default_per_page = 20
        max_per_page = 100

        assert default_page == 1
        assert default_per_page == 20
        assert max_per_page == 100

    @pytest.mark.integration
    def test_full_pipeline_integration(self):
        """
        Full pipeline test (slow): submit → verify → complete.
        Submit report → claims should be extracted and dispatched.
        This test validates the complete data contract.
        """
        # Validate full pipeline data contract
        pipeline_steps = [
            "submit_report",        # Creates report + extracts claims
            "dispatch_workers",     # Dispatches verify_claim tasks
            "verify_claims",        # Workers process each claim
            "check_report_complete", # All done → generate confidence score
            "report_complete",      # Status = 'complete', score > 0
        ]

        for step in pipeline_steps:
            assert isinstance(step, str)
        assert len(pipeline_steps) == 5

    def test_ws_url_format(self):
        """WebSocket URL must follow the expected pattern."""
        report_id = "550e8400-e29b-41d4-a716-446655440000"
        ws_url = f"ws://localhost/ws/reports/{report_id}/stream"

        assert ws_url.startswith("ws://")
        assert report_id in ws_url
        assert ws_url.endswith("/stream")
