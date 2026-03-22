from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class BacktrackingVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 64

        if "backtrack" in text or "dfs" in text:
            findings.append("Backtracking-style recursive search detected.")
            verdict = "accept"
            confidence += 10
        if "append(" in text and "pop(" in text:
            findings.append("Choice / undo pattern detected.")
            confidence += 5

        return VerifierReport(
            category="backtracking",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious backtracking-specific structure detected."],
            hard_failures=[],
        )