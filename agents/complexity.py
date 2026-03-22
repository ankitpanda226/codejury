from typing import List, Optional

from agents.base import BaseJuror
from models.schemas import JurorOpinion
from utils.signals import extract_code_signals


class ComplexityJuror(BaseJuror):
    def evaluate(self, problem: str, code: str, category: str, verifier_findings, execution_findings, prior_opinions: Optional[List[JurorOpinion]] = None) -> JurorOpinion:
        s = extract_code_signals(code)
        score = 68
        points = []
        risks = []
        agreements = []
        disagreements = []

        if category == "binary_search":
            points.append("Binary-search-like structure detected.")
            score += 10
        elif category == "two_sum" and s["hashmap_usage"]:
            points.append("Hash-based structure detected; likely near-linear lookup behavior.")
            score += 10
        elif category == "two_sum" and s["loops"] >= 2:
            risks.append("Nested iteration may be present depending on structure.")
            score -= 12
        else:
            if s["loops"] >= 3:
                risks.append("Multiple loop constructs suggest possible high time complexity.")
                score -= 25
            elif s["loops"] == 2:
                risks.append("Nested iteration may be present depending on structure.")
                score -= 12
            else:
                points.append("No obvious heavy nesting from surface-level signals.")

        if s["line_count"] > 120:
            risks.append("Large solution size may hide redundant work.")
            score -= 10

        if prior_opinions:
            for op in prior_opinions:
                if op.specialty == "Correctness" and op.verdict == "accept":
                    disagreements.append("A solution can be correct and still inefficient.")
                if op.specialty == "Code Quality" and op.verdict in ("accept", "revise"):
                    agreements.append("Readable code does not remove the need for better asymptotic performance.")

        verdict = "accept" if score >= 75 else "revise" if score >= 52 else "reject"
        confidence = min(92, max(40, score))

        return JurorOpinion(
            juror_name=self.name,
            specialty=self.specialty,
            verdict=verdict,
            confidence=confidence,
            key_points=points or ["Exact asymptotic complexity still needs semantic analysis."],
            risks=risks or ["Exact asymptotic complexity still needs semantic analysis."],
            score=score,
            agreements=list(dict.fromkeys(agreements))[:3],
            disagreements=list(dict.fromkeys(disagreements))[:3],
        )