from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class IntervalVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 66

        if "sort(" in text or "sorted(" in text:
            findings.append("Interval sorting detected.")
            verdict = "accept"
            confidence += 10
        if "merge" in text or "overlap" in text:
            findings.append("Interval overlap handling keywords detected.")

        return VerifierReport(
            category="interval",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious interval-specific structure detected."],
            hard_failures=[],
        )