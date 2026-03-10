import json
import hashlib
from typing import List, NamedTuple

class ConfidenceScore(NamedTuple):
    score: float
    hash: str
    anchor: str

def generate_confidence_score(claims: List[dict]) -> ConfidenceScore:
    """
    Generates a deterministic cryptographic confidence score based on verification results.
    
    Algorithm:
    1. Sort results by claim ID for determinism.
    2. JSON serialize (status, value, score) tuples.
    3. Hash with SHA-256.
    """
    # Canonical tuple list for hashing
    result_data = []
    verified_count = 0
    
    for c in sorted(claims, key=lambda x: x['id']):
        result_data.append((
            c['id'],
            c['status'],
            str(c.get('db_expected_value', '')),
            float(c.get('similarity_score', 0.0))
        ))
        if c['status'] == 'verified':
            verified_count += 1
            
    payload = json.dumps(result_data, sort_keys=True)
    full_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    score = (verified_count / len(claims)) * 100 if claims else 0
    short_hash = full_hash[:16]
    anchor = f"{score:.1f}#{short_hash}"
    
    return ConfidenceScore(
        score=score,
        hash=full_hash,
        anchor=anchor
    )
