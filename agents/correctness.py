from typing import List, Optional

from agents.base import BaseJuror
from models.schemas import JurorOpinion
from utils.ollama_client import ask_ollama_json


class CorrectnessJuror(BaseJuror):
    def __init__(self, name: str, specialty: str, model: str = "llama3.2"):
        super().__init__(name, specialty)
        self.model = model

    def _fallback(self, verifier_findings: List[str], execution_findings: List[str]) -> JurorOpinion:
        strong_negatives = [
            x for x in verifier_findings + execution_findings
            if any(k in x.lower() for k in ["fail", "loop", "bug", "incorrect", "timed out", "stuck"])
        ]
        if strong_negatives:
            return JurorOpinion(
                juror_name=self.name,
                specialty=self.specialty,
                verdict="revise",
                confidence=80,
                key_points=["Verifier/runtime evidence suggests correctness concerns."],
                risks=strong_negatives[:4],
                score=80,
                agreements=[],
                disagreements=[],
            )

        return JurorOpinion(
            juror_name=self.name,
            specialty=self.specialty,
            verdict="accept",
            confidence=85,
            key_points=["Verifier and runtime checks support the correctness of the solution."],
            risks=["No major correctness risks identified."],
            score=85,
            agreements=[],
            disagreements=[],
        )

    def evaluate(
        self,
        problem: str,
        code: str,
        category: str,
        verifier_findings: List[str],
        execution_findings: List[str],
        prior_opinions: Optional[List[JurorOpinion]] = None,
    ) -> JurorOpinion:
        prior_text = "None"
        if prior_opinions:
            prior_text = "\n".join(
                f"{op.juror_name} ({op.specialty}) | verdict={op.verdict} | risks={'; '.join(op.risks[:2])}"
                for op in prior_opinions
            )

        schema = {
            "type": "object",
            "properties": {
                "verdict": {"type": "string"},
                "confidence": {"type": "integer"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "risks": {"type": "array", "items": {"type": "string"}},
                "score": {"type": "integer"},
                "agreements": {"type": "array", "items": {"type": "string"}},
                "disagreements": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["verdict", "confidence", "key_points", "risks", "score", "agreements", "disagreements"]
        }

        system_prompt = """
You are the Correctness Juror in a jury-style code review system.

Evaluate ONLY algorithmic correctness.
Use verifier findings and runtime findings as strong evidence.
Do not discuss style, readability, maintainability, or time complexity.
Do not speculate about NaNs, non-integer inputs, unrelated contracts, or impossible input types unless the problem explicitly requires them.
Return valid JSON only.
""".strip()

        user_prompt = f"""
Problem:
{problem}

Detected category:
{category}

Candidate code:
{code}

Verifier findings:
{verifier_findings}

Execution findings:
{execution_findings}

Prior juror opinions:
{prior_text}

Judge only algorithmic correctness.
Focus on: whether the implementation returns the right result for valid inputs, whether it handles the expected fallback case, and whether verifier/runtime evidence reveals a real bug.
""".strip()

        try:
            result = ask_ollama_json(self.model, system_prompt, user_prompt, schema)
        except Exception:
            return self._fallback(verifier_findings, execution_findings)

        verdict = str(result.get("verdict", "revise")).strip().lower()
        if verdict not in {"accept", "revise", "reject"}:
            verdict = "revise"

        confidence = max(0, min(100, int(result.get("confidence", 60))))
        score = max(0, min(100, int(result.get("score", confidence))))

        raw_key_points = result.get("key_points", []) or ["The overall logic appears plausible."]
        cleaned_key_points = []
        for point in raw_key_points:
            text = str(point).lower().strip()
            if "time complexity" in text or "o(" in text or "performance" in text:
                continue
            if "nan" in text or "non-integer" in text:
                continue
            if "duplicate target values" in text:
                continue
            cleaned_key_points.append(point)
        key_points = cleaned_key_points[:4] or ["The overall logic appears plausible."]

        raw_risks = result.get("risks", []) or []
        cleaned_risks = []
        for risk in raw_risks:
            text = str(risk).lower().strip()

            if text in {"none", "no risk", "no risks"}:
                continue
            if "no major correctness risks identified" in text:
                continue
            if "nan" in text or "non-integer" in text:
                continue
            if "duplicate target values" in text:
                continue
            if "error handling" in text:
                continue
            if "performance" in text or "time complexity" in text or "o(" in text:
                continue
            if "duplicate values do not break" in text:
                continue
            if "there are no risks identified" in text:
                continue

            cleaned_risks.append(risk)

        merged_risks = cleaned_risks[:]
        for item in verifier_findings + execution_findings:
            low = item.lower()
            if any(k in low for k in ["fail", "loop", "bug", "incorrect", "timed out", "stuck"]):
                merged_risks.append(item)

        risks = list(dict.fromkeys(merged_risks))[:4] or ["No major correctness risks identified."]

        raw_agreements = result.get("agreements", []) or []
        agreements = []
        for a in raw_agreements:
            text = str(a).lower().strip()
            if "juror" in text:
                continue
            if "time complexity" in text or "performance" in text:
                continue
            if "nan" in text or "non-integer" in text:
                continue
            agreements.append(a)
        agreements = agreements[:3]

        raw_disagreements = result.get("disagreements", []) or []
        disagreements = []
        for d in raw_disagreements:
            text = str(d).lower().strip()
            if "juror" in text:
                continue
            disagreements.append(d)
        disagreements = disagreements[:3]

        verifier_accept = not any(
            any(k in x.lower() for k in ["fail", "loop", "bug", "incorrect", "timed out", "stuck"])
            for x in verifier_findings
        )
        execution_accept = not any(
            any(k in x.lower() for k in ["fail", "loop", "bug", "incorrect", "timed out", "stuck"])
            for x in execution_findings
        )

        if verifier_accept and execution_accept:
            verdict = "accept"
            confidence = max(confidence, 85)
            score = max(score, 85)
            risks = ["No major correctness risks identified."]

        if any(any(k in r.lower() for k in ["fail", "loop", "bug", "incorrect", "timed out", "stuck"]) for r in risks):
            verdict = "revise"

        return JurorOpinion(
            juror_name=self.name,
            specialty=self.specialty,
            verdict=verdict,
            confidence=confidence,
            key_points=key_points,
            risks=risks[:4],
            score=score,
            agreements=agreements,
            disagreements=disagreements,
        )