from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class GenericVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        return VerifierReport(
            category="generic",
            verdict="revise",
            confidence=50,
            findings=["No category-specific verifier matched; relying on generic jurors and any runtime support."],
            hard_failures=[],
        )