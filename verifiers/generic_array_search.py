from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class GenericArraySearchVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 60

        if "for i in range" in text or "enumerate" in text:
            findings.append("Linear search structure detected.")
            verdict = "accept"
            confidence += 10

        if "return -1" in text:
            findings.append("Explicit not-found fallback detected.")
            confidence += 5

        return VerifierReport(
            category="generic_array_search",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious search-specific structure detected."],
            hard_failures=[],
        )