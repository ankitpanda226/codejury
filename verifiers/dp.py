from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class DPVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 64

        if "dp" in text:
            findings.append("DP table or variable detected.")
            verdict = "accept"
            confidence += 8
        if "memo" in text or "cache" in text:
            findings.append("Memoization detected.")
            confidence += 6
        if "base case" in text or "if n ==" in text or "if i ==" in text:
            findings.append("Possible base-case handling detected.")

        return VerifierReport(
            category="dp",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious DP-specific structure detected."],
            hard_failures=[],
        )