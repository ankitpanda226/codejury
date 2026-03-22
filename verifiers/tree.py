from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class TreeVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        verdict = "revise"
        confidence = 65

        if ".left" in text or ".right" in text:
            findings.append("Tree-child access detected.")
            verdict = "accept"
            confidence += 10
        if "dfs" in text or "bfs" in text or "queue" in text or "stack" in text:
            findings.append("Tree traversal strategy detected.")
            confidence += 5

        return VerifierReport(
            category="tree",
            verdict=verdict,
            confidence=confidence,
            findings=findings or ["No obvious tree-specific structure detected."],
            hard_failures=[],
        )