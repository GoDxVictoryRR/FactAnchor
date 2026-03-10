import logging
from typing import List
from .pipeline import get_pipeline
from .models import ExtractedClaim, ExtractedEntity
from .classifiers import classify_claim

logger = logging.getLogger(__name__)

MAX_CLAIMS_PER_DOC = 200

class ClaimExtractionError(Exception):
    """Raised when claim extraction fails due to model or pipeline issues."""
    pass

def extract_claims(text: str) -> List[ExtractedClaim]:
    """
    Main pipeline for extracting factual claims from a document.
    
    Steps:
    1. Sentence segmentation via spaCy.
    2. NER and dependency parsing for each sentence.
    3. Filter and classify claims.
    4. Return sorted and enriched claim list.
    """
    try:
        nlp = get_pipeline()
    except Exception as e:
        logger.error(f"Failed to load spaCy pipeline: {e}")
        raise ClaimExtractionError(f"Pipeline loading failed: {e}")

    doc = nlp(text)
    extracted_claims: List[ExtractedClaim] = []
    
    for i, sent in enumerate(doc.sents):
        # Stop if we hit the max claims cap
        if len(extracted_claims) >= MAX_CLAIMS_PER_DOC:
            logger.warning(f"Max claims limit ({MAX_CLAIMS_PER_DOC}) reached. Truncating.")
            break

        # Filter: Ignore very short sentences (likely not meaningful claims)
        if len(sent) < 5:
            continue

        entities = [
            ExtractedEntity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char
            )
            for ent in sent.ents
        ]

        # Create candidate claim
        claim = ExtractedClaim(
            claim_text=sent.text.strip(),
            claim_type="qualitative", # Placeholder, updated by classifier
            entities=entities,
            char_start=sent.start_char,
            char_end=sent.end_char,
            confidence=1.0, # Default, can be refined based on model scores
            sequence_num=len(extracted_claims) + 1
        )

        # Classify as SQL vs Vector
        claim.claim_type = classify_claim(claim)
        extracted_claims.append(claim)

    logger.info(
        f"Extraction complete: {len(extracted_claims)} claims found "
        f"({sum(1 for c in extracted_claims if c.claim_type == 'quantitative')} quant, "
        f"{sum(1 for c in extracted_claims if c.claim_type == 'qualitative')} qual)"
    )

    return extracted_claims
