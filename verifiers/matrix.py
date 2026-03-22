from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class MatrixVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 65

        if "len(matrix)" in text or "len(grid)" in text:
            findings.append("Matrix/grid dimension handling detected.")
            verdict = "accept"
            confidence += 8
        if "directions" in text or "dr" in text or "dc" in text:
            findings.append("Neighbor traversal pattern detected.")
            confidence += 5

        return VerifierReport(
            category="matrix",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious matrix-specific structure detected."],
            hard_failures=[],
        )