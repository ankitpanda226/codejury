from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class BinarySearchVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        hard_failures = []
        verdict = "accept"
        confidence = 80

        if "while low < high" in text and "low = mid" in text:
            hard_failures.append("Binary search may fail to progress because low is updated to mid instead of mid + 1.")
        if "while low < high" in text and "high = mid" in text:
            hard_failures.append("Binary search may fail to shrink correctly because high is updated to mid instead of mid - 1 in common variants.")
        if "while low < high" in text and "low = mid" in text and "high = mid" in text:
            hard_failures.append("Both bounds can get stuck at mid, creating a non-progressing loop.")
        if "return -1" not in text:
            findings.append("No explicit not-found fallback is visible.")
            verdict = "revise"
            confidence -= 10
        if "mid = low + (high - low) // 2" in text or "mid = (low + high) // 2" in text or "mid=(low+high)//2" in text:
            findings.append("Binary-search midpoint computation detected.")

        if hard_failures:
            verdict = "reject"
            confidence = 94

        if not findings and not hard_failures:
            findings.append("No obvious binary-search-specific hard failure detected.")

        return VerifierReport(
            category="binary_search",
            verdict=verdict,
            confidence=confidence,
            findings=findings,
            hard_failures=hard_failures,
        )