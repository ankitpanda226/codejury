from typing import List, Optional

from agents.base import BaseJuror
from models.schemas import JurorOpinion
from utils.signals import extract_code_signals


class CodeQualityJuror(BaseJuror):
    def evaluate(self, problem: str, code: str, category: str, verifier_findings, execution_findings, prior_opinions: Optional[List[JurorOpinion]] = None) -> JurorOpinion:
        s = extract_code_signals(code)
        score = 66
        points = []
        risks = []
        agreements = []
        disagreements = []

        if s["comments"] > 0:
            score += 8
            points.append("Comments improve readability.")
        if s["avg_line_length"] > 90 or s["long_lines"] > 3:
            score -= 15
            risks.append("Readability is reduced by long lines.")
        if s["line_count"] < 8:
            score -= 8
            risks.append("Solution may be too terse to be maintainable.")
        if "temp" in code.lower() or "abc" in code.lower() or " x " in code.lower():
            risks.append("Naming could be improved.")

        if prior_opinions:
            for op in prior_opinions:
                if op.specialty == "Correctness" and op.verdict == "accept":
                    agreements.append("I agree the core idea may work, but maintainability still matters.")
                if op.specialty == "Complexity" and op.verdict in ("revise", "reject"):
                    agreements.append("A more efficient approach is often also cleaner to explain.")

        verdict = "accept" if score >= 78 else "revise"
        confidence = min(88, max(40, score))

        return JurorOpinion(
            juror_name=self.name,
            specialty=self.specialty,
            verdict=verdict,
            confidence=confidence,
            key_points=points or ["Overall structure is readable at a glance."],
            risks=risks or ["Naming and modularity could still be improved."],
            score=score,
            agreements=list(dict.fromkeys(agreements))[:3],
            disagreements=list(dict.fromkeys(disagreements))[:3],
        )