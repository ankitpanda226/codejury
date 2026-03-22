import re
from typing import Any, Dict


def extract_code_signals(code: str) -> Dict[str, Any]:
    lines = [line for line in code.splitlines() if line.strip()]
    text = code.lower()

    loops = len(re.findall(r"\b(for|while)\b", text))
    conditionals = len(re.findall(r"\b(if|elif|else|switch|case)\b", text))
    recursion = bool(re.search(r"def\s+(\w+)\(.*\):[\s\S]*?\1\(", code))
    sort_usage = any(token in text for token in ["sort(", ".sort(", "sorted(", "arrays.sort", "collections.sort"])
    hashmap_usage = any(token in text for token in ["hashmap", "dict(", "unordered_map", "map<", "{}"])
    try_catch = "try:" in text or "except:" in text or "catch(" in text
    comments = len([l for l in lines if l.strip().startswith("#") or l.strip().startswith("//")])
    long_lines = sum(1 for l in lines if len(l) > 100)
    avg_line_length = sum(len(l) for l in lines) / max(1, len(lines))
    empty_input_handling = any(token in text for token in ["if not", "len(", "size() == 0", "null", "none"])
    boundary_mentions = any(token in text for token in ["<=", ">=", "== 0", "==1", "== 1", "< high", "<= high"])

    return {
        "line_count": len(lines),
        "loops": loops,
        "conditionals": conditionals,
        "recursion": recursion,
        "sort_usage": sort_usage,
        "hashmap_usage": hashmap_usage,
        "try_catch": try_catch,
        "comments": comments,
        "long_lines": long_lines,
        "avg_line_length": avg_line_length,
        "empty_input_handling": empty_input_handling,
        "boundary_mentions": boundary_mentions,
    }