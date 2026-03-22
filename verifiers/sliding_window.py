from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class SlidingWindowVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        hard_failures = []
        verdict = "revise"
        confidence = 68

        if "left" in text or "l =" in text or "window" in text:
            findings.append("Sliding-window-like control variables detected.")
            verdict = "accept"
            confidence += 8
        if "while" in text and "for" in text:
            findings.append("Nested loop structure may still be valid for sliding window, but needs careful invariant handling.")
        if "left" in text and "right" in text and "left += 1" not in text and "left = left + 1" not in text:
            findings.append("No visible left-pointer movement detected; window contraction may be missing.")
            verdict = "revise"

        return VerifierReport(
            category="sliding_window",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["General sliding-window pattern detected."],
            hard_failures=hard_failures,
        )