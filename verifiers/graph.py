from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class GraphVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 66

        if "visited" in text:
            findings.append("Visited tracking detected.")
            verdict = "accept"
            confidence += 10
        if "queue" in text or "deque" in text:
            findings.append("BFS-like traversal detected.")
        if "dfs" in text or "stack" in text:
            findings.append("DFS-like traversal detected.")

        return VerifierReport(
            category="graph",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious graph-specific structure detected."],
            hard_failures=[],
        )