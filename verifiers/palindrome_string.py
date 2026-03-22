from models.schemas import VerifierReport
from verifiers.base import BaseVerifier


class PalindromeStringVerifier(BaseVerifier):
    def verify(self, problem: str, code: str) -> VerifierReport:
        text = code.lower()
        findings = []
        hard_failures = []
        verdict = "accept"
        confidence = 78

        if "isalnum" in text or ".lower()" in text or "lower()" in text:
            findings.append("String normalization logic detected.")
        else:
            findings.append("No obvious lowercase/alphanumeric normalization detected; may miss problem requirements.")
            verdict = "revise"
            confidence -= 10

        if "left" in text and "right" in text:
            findings.append("Two-pointer palindrome scan detected.")
        elif "[::-1]" in text:
            findings.append("Reverse-string palindrome check detected.")
        else:
            findings.append("No obvious palindrome comparison strategy detected.")
            verdict = "revise"
            confidence -= 10

        return VerifierReport(
            category="palindrome_string",
            verdict=verdict,
            confidence=confidence,
            findings=findings,
            hard_failures=hard_failures,
        )