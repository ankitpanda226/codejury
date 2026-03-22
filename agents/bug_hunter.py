from typing import List, Optional

from agents.base import BaseJuror
from models.schemas import JurorOpinion


class BugHunterJuror(BaseJuror):
    def evaluate(self, problem: str, code: str, category: str, verifier_findings, execution_findings, prior_opinions: Optional[List[JurorOpinion]] = None) -> JurorOpinion:
        text = code.lower()
        score = 64
        points = ["No immediate syntax-level red flag is inferred from plain text scan."]
        risks = []
        agreements = []
        disagreements = []

        suspicious_patterns = [
            ("/ 0", "Possible division-by-zero issue."),
            ("[i+1]", "Potential out-of-range access near the end of iteration."),
            ("while true", "Potential infinite loop risk."),
            ("== none", "Language-style mismatch may indicate bug risk."),
        ]

        for token, msg in suspicious_patterns:
            if token in text:
                score -= 12
                risks.append(msg)

        if category == "binary_search":
            if "while low < high" in text and "low = mid" in text:
                risks.append("Binary search may fail to progress because low is updated to mid instead of mid + 1.")
                score -= 20
            if "while low < high" in text and "high = mid" in text:
                risks.append("Binary search may fail to shrink correctly because high is updated to mid instead of mid - 1 in some variants.")
                score -= 12
            if "while low < high" in text and "mid = (low + high) // 2" in text and "low = mid" in text and "high = mid" in text:
                risks.append("Both bounds can get stuck at mid, creating a non-progressing binary search loop.")
                score -= 18

        if category == "two_sum":
            if "for j in range(len(nums))" in text:
                risks.append("Two-sum may reuse the same index because the inner loop does not enforce j > i.")
                score -= 18
            if "return [0, 1]" in text.replace(" ", ""):
                risks.append("This solution returns a constant answer without using the input.")
                score -= 20

        for item in verifier_findings + execution_findings:
            low = item.lower()
            if any(k in low for k in ["fail", "loop", "bug", "incorrect", "timed out", "stuck"]):
                risks.append(item)
                score -= 10

        if prior_opinions:
            for op in prior_opinions:
                if op.specialty == "Edge Cases" and op.verdict in ("revise", "reject"):
                    score -= 3
                    agreements.append("I agree with Edge Cases that unusual inputs are where bugs often appear.")
                if op.specialty == "Correctness" and op.verdict == "accept":
                    disagreements.append("A correct high-level idea can still hide implementation bugs.")
                if op.specialty == "Complexity" and op.verdict in ("revise", "reject"):
                    agreements.append("Complex control flow often correlates with higher bug risk.")

        verdict = "accept" if score >= 72 else "revise" if score >= 52 else "reject"
        confidence = min(87, max(38, score))

        return JurorOpinion(
            juror_name=self.name,
            specialty=self.specialty,
            verdict=verdict,
            confidence=confidence,
            key_points=points,
            risks=list(dict.fromkeys(risks))[:4] or ["No obvious bug signature found, but runtime testing is still needed."],
            score=score,
            agreements=list(dict.fromkeys(agreements))[:3],
            disagreements=list(dict.fromkeys(disagreements))[:3],
        )