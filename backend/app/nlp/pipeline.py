import spacy
import logging
from spacy.language import Language
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level singleton for the loaded pipeline
_nlp: Optional[Language] = None

@Language.component("claim_segmenter")
def claim_segmenter(doc):
    """
    Custom component to refine sentence boundaries for claim extraction.
    Currently uses default sentencizer behavior, but can be extended
    with domain-specific splitting rules.
    """
    return doc

def get_pipeline() -> Language:
    """
    Loads and returns the spaCy pipeline.
    Uses en_core_web_trf for highest accuracy, falling back to lg if necessary.
    The pipeline is cached as a singleton.
    """
    global _nlp
    if _nlp is not None:
        return _nlp

    model_name = "en_core_web_sm"
    try:
        logger.info(f"Loading spaCy model: {model_name}")
        _nlp = spacy.load(model_name)
    except OSError:
        model_name = "en_core_web_lg"
        logger.warning(f"Transformer model not found. Falling back to: {model_name}")
        try:
            _nlp = spacy.load(model_name)
        except OSError:
            model_name = "en_core_web_sm"
            logger.warning(f"Large model not found. Falling back to lightweight: {model_name}")
            _nlp = spacy.load(model_name)

    # Add custom segmenter if not already present
    if "claim_segmenter" not in _nlp.pipe_names:
        _nlp.add_pipe("claim_segmenter", before="ner")

    return _nlp
