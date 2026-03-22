from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class TwoSumVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        hard_failures = []
        verdict = "accept"
        confidence = 75

        if "return [0, 1]" in text.replace(" ", ""):
            hard_failures.append("This solution returns a constant answer without using the input.")
        if "for j in range(len(nums))" in text and "for i in range(len(nums))" in text:
            hard_failures.append("Two-sum may reuse the same index because the inner loop does not enforce j > i.")
        if "return []" not in text and "return [seen[need], i]" not in text and "return [i, j]" in text:
            findings.append("No explicit fallback is visible when no valid pair exists.")
            verdict = "revise"
            confidence -= 10
        if "seen = {}" in text or "seen={}" in text:
            findings.append("Hash-map style approach detected.")
        if "for i in range(len(nums))" in text and "for j in range(i + 1, len(nums))" in text:
            findings.append("Brute-force pair scan detected.")

        if hard_failures:
            verdict = "reject"
            confidence = 92

        if not findings and not hard_failures:
            findings.append("No obvious two-sum-specific hard failure detected.")

        return VerifierReport(
            category="two_sum",
            verdict=verdict,
            confidence=confidence,
            findings=findings,
            hard_failures=hard_failures,
        )