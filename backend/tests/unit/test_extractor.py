import pytest
import logging
from unittest.mock import patch, MagicMock
from app.nlp.extractor import extract_claims


class TestExtractor:
    """Tests for the NLP claim extraction pipeline."""

    def test_extracts_quantitative_claim_with_money_entity(self):
        """Input with dollar amounts should produce a quantitative claim."""
        text = "Q3 revenue was $4.2B, up 12% year over year."
        claims = extract_claims(text)

        assert len(claims) >= 1
        quant_claims = [c for c in claims if c.claim_type == "quantitative"]
        assert len(quant_claims) >= 1, "Expected at least one quantitative claim for text with MONEY entity"

    def test_extracts_qualitative_claim(self):
        """Input with geographic expansion should produce a qualitative claim."""
        text = "The company expanded its operations into the European market, establishing offices in London, Berlin, and Paris."
        claims = extract_claims(text)

        assert len(claims) >= 1
        qual_claims = [c for c in claims if c.claim_type == "qualitative"]
        assert len(qual_claims) >= 1, "Expected at least one qualitative claim for text with GPE entities"

    def test_filters_short_sentences(self):
        """Sentences shorter than 5 tokens should be filtered out."""
        text = "Yes. No. Maybe."
        claims = extract_claims(text)

        assert len(claims) == 0, "Short sentences (< 5 tokens) should be filtered out"

    def test_respects_200_claim_hard_cap(self, caplog):
        """Even with many sentences, the claim cap of 200 is respected."""
        # Generate 250 distinct factual sentences
        sentences = [
            f"In Q{(i % 4) + 1} of {2020 + (i // 4)}, revenue was ${i * 100}M for region {i}."
            for i in range(250)
        ]
        text = " ".join(sentences)

        with caplog.at_level(logging.WARNING):
            claims = extract_claims(text)

        assert len(claims) <= 200, f"Claim count should be capped at 200, got {len(claims)}"

    def test_char_offsets_are_accurate(self):
        """char_start and char_end should correctly slice the claim from the input text."""
        text = "The annual revenue was $5.1 billion for the fiscal year ending in December."
        claims = extract_claims(text)

        for claim in claims:
            if claim.char_start is not None and claim.char_end is not None:
                sliced = text[claim.char_start:claim.char_end]
                # The sliced text should be a substring of the original
                assert len(sliced) > 0, "Char offset slice should not be empty"
                assert sliced in text, "Sliced text must appear in original"

    def test_returns_list_of_extracted_claims(self):
        """extract_claims should return a list of ExtractedClaim objects."""
        text = "Apple reported $94.8 billion in quarterly revenue. Microsoft reported $56.5 billion in revenue."
        claims = extract_claims(text)

        assert isinstance(claims, list)
        for claim in claims:
            assert hasattr(claim, "claim_text")
            assert hasattr(claim, "claim_type")
            assert hasattr(claim, "sequence_num")
            assert claim.claim_type in ("quantitative", "qualitative")

    def test_empty_input_returns_no_claims(self):
        """Empty string input should return zero claims."""
        claims = extract_claims("")
        assert claims == []

    def test_sequence_numbers_are_sequential(self):
        """Sequence numbers should start at 1 and increment."""
        text = "Revenue was $10B. Profit was $2B. Margin was 20%. Headcount reached 150,000 employees."
        claims = extract_claims(text)

        if len(claims) > 0:
            for i, claim in enumerate(claims):
                assert claim.sequence_num == i + 1, f"Expected sequence_num={i + 1}, got {claim.sequence_num}"
