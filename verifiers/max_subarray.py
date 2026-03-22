from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class MaxSubarrayVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        hard_failures = []
        verdict = "revise"
        confidence = 70

        if "current" in text or "max_sum" in text or "best" in text:
            findings.append("Kadane-like running maximum variables detected.")
            verdict = "accept"
            confidence += 10

        if "sum(" in text and "for" in text and "for" in text[text.find("for") + 1:]:
            findings.append("Possible quadratic subarray enumeration detected.")
            verdict = "revise"

        return VerifierReport(
            category="max_subarray",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious max-subarray-specific structure detected."],
            hard_failures=hard_failures,
        )