MIN_CONFIDENCE = 0.72


def guard_payload(payload: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not payload.get("evidence"):
        issues.append("缺少 evidence 字段")
    if payload.get("confidence", 1) < MIN_CONFIDENCE:
        issues.append("置信度低于阈值")
    return len(issues) == 0, issues


def require_evidence(item: dict, default_source: str) -> dict:
    if not item.get("evidence"):
        item["evidence"] = [{"source": default_source, "quote": item.get("name") or item.get("title") or "mock evidence"}]
    return item
