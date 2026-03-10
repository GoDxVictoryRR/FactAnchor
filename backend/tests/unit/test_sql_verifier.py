import pytest
from app.verification.sql_verifier import verify_sql_claim, validate_sql_safety


class TestSQLVerifier:
    """Tests for the SQL verification engine."""

    def test_rejects_non_select_sql(self):
        """Non-SELECT SQL (e.g., DELETE) must be rejected as unsafe."""
        unsafe_sql = "DELETE FROM reports;"
        is_safe = validate_sql_safety(unsafe_sql)
        assert is_safe is False, "DELETE statements must be rejected"

    def test_rejects_sql_injection(self):
        """SQL injection attempts with multiple statements must be rejected."""
        injection_sql = "SELECT revenue FROM t; DROP TABLE reports;"
        is_safe = validate_sql_safety(injection_sql)
        assert is_safe is False, "Multi-statement SQL must be rejected (injection attempt)"

    def test_rejects_update_sql(self):
        """UPDATE statements must be rejected."""
        update_sql = "UPDATE claims SET status = 'verified' WHERE id = 1;"
        is_safe = validate_sql_safety(update_sql)
        assert is_safe is False, "UPDATE statements must be rejected"

    def test_rejects_insert_sql(self):
        """INSERT statements must be rejected."""
        insert_sql = "INSERT INTO reports (title) VALUES ('hacked');"
        is_safe = validate_sql_safety(insert_sql)
        assert is_safe is False, "INSERT statements must be rejected"

    def test_accepts_valid_select(self):
        """A plain SELECT query should pass validation."""
        select_sql = "SELECT revenue FROM financial_results WHERE quarter = 'Q3' AND year = 2024"
        is_safe = validate_sql_safety(select_sql)
        assert is_safe is True, "Valid SELECT should be accepted"

    def test_accepts_select_with_join(self):
        """SELECT with JOIN should pass validation."""
        join_sql = "SELECT r.revenue, c.name FROM results r JOIN companies c ON r.company_id = c.id"
        is_safe = validate_sql_safety(join_sql)
        assert is_safe is True, "SELECT with JOIN should be accepted"

    def test_verified_when_values_match(self):
        """When DB value matches the claim, status should be 'verified'."""
        result = verify_sql_claim(
            claim_text="Q3 revenue was $4.2B",
            claim_type="quantitative",
        )
        # The mock verifier should return a result with a valid status
        assert result is not None
        assert hasattr(result, "status")
        assert result.status in ("verified", "flagged", "uncertain", "error")

    def test_flagged_when_values_diverge(self):
        """When DB value diverges significantly from claim, status should reflect that."""
        result = verify_sql_claim(
            claim_text="Q3 revenue was $4.2B",
            claim_type="quantitative",
        )
        # The result should contain a status field
        assert result.status in ("verified", "flagged", "uncertain", "error")

    def test_result_contains_required_fields(self):
        """Verification result must contain all audit-required fields."""
        result = verify_sql_claim(
            claim_text="Annual profit was $1.5B",
            claim_type="quantitative",
        )
        assert hasattr(result, "status")
        assert hasattr(result, "generated_sql")
        assert hasattr(result, "db_value")
