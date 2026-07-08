import hashlib
from difflib import SequenceMatcher

from app.services.mock_llm import mock_extract_jd


def text_hash(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def parse_jd_text(text: str) -> dict:
    result = mock_extract_jd(text)
    result["evidence_sources"] = result.pop("evidence")
    return result


def calculate_duplicate_rate(texts: list[str]) -> float:
    if not texts:
        return 0
    hashes = {text_hash(text) for text in texts}
    duplicated = len(texts) - len(hashes)
    fuzzy_hits = 0
    for idx, text in enumerate(texts):
        for other in texts[idx + 1: idx + 4]:
            if similarity(text, other) > 0.86:
                fuzzy_hits += 1
    return round(min(0.45, (duplicated + fuzzy_hits) / max(len(texts), 1)), 3)
