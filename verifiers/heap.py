from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class HeapVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 66

        if "heapq" in text:
            findings.append("Python heapq usage detected.")
            verdict = "accept"
            confidence += 12
        if "heappush" in text or "heappop" in text:
            findings.append("Heap push/pop operations detected.")

        return VerifierReport(
            category="heap",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious heap-specific structure detected."],
            hard_failures=[],
        )