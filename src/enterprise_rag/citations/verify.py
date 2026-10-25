"""Citation integrity checks: bracketed IDs must originate from this turn's evidence."""
import re

def verify_citations(answer: str, evidence: list[dict]) -> dict:
    valid_ids = {str(e.get("source_id", "")) for e in evidence}
    referenced = set(re.findall(r"\[([^\]]+)\]", answer))
    invalid = sorted(referenced - valid_ids)
    return {"valid": not invalid, "referenced_ids": sorted(referenced), "invalid_ids": invalid,
            "has_source_reference": bool(referenced & valid_ids)}
