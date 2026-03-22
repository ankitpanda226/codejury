from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class LinkedListVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 65

        if "head" in text and ".next" in text:
            findings.append("Linked-list traversal detected.")
            verdict = "accept"
            confidence += 10

        if "slow" in text and "fast" in text:
            findings.append("Fast/slow pointer pattern detected.")

        return VerifierReport(
            category="linked_list",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious linked-list-specific structure detected."],
            hard_failures=[],
        )