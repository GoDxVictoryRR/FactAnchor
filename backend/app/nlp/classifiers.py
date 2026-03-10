from typing import Literal
from .models import ExtractedClaim

# Quantitative signals: Entities and keywords that suggest numeric/arithmetic claims
QUANTITATIVE_ENTITIES = {"MONEY", "PERCENT", "CARDINAL", "QUANTITY", "DATE"}
QUANTITATIVE_VERBS = {"increased", "decreased", "grew", "fell", "improved", "declined", "rose", "dropped"}
ARITHMETIC_MARKERS = {"%", "YoY", "from", "to", "up", "down", "by", "compared"}

def classify_claim(claim: ExtractedClaim) -> Literal["quantitative", "qualitative"]:
    """
    Routes an extracted claim to either SQL or Vector verification.
    
    Logic:
    - If it contains specific quantitative entities (MONEY, PERCENT, etc.) AND
      either a quantitative verb or arithmetic marker -> quantitative (SQL).
    - Otherwise -> qualitative (Vector).
    
    Examples:
    1. "Revenue grew by 15% YoY" -> quantitative
    2. "The company expanded into Europe" -> qualitative
    3. "Operating margin improved to 23.4%" -> quantitative
    4. "We partnered with Google in 2023" -> qualitative (DATE alone isn't enough)
    """
    text_lower = claim.claim_text.lower()
    
    # Check for quantitative entities
    entity_labels = {e.label for e in claim.entities}
    has_quant_entities = any(label in QUANTITATIVE_ENTITIES for label in entity_labels)
    
    # Check for quantitative verbs or markers
    words = set(text_lower.split())
    has_quant_signal = any(verb in words for verb in QUANTITATIVE_VERBS) or \
                       any(marker in words for marker in ARITHMETIC_MARKERS)

    # MONEY and PERCENT are very strong signals for SQL verification
    strong_signals = {"MONEY", "PERCENT"}
    if any(label in strong_signals for label in entity_labels):
        return "quantitative"

    if has_quant_entities and has_quant_signal:
        return "quantitative"
        
    return "qualitative"
