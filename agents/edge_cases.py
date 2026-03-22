from typing import List, Optional

from agents.base import BaseJuror
from models.schemas import JurorOpinion
from utils.ollama_client import ask_ollama_json


class EdgeCaseJuror(BaseJuror):
    def __init__(self, name: str, specialty: str, model: str = "llama3.2"):
        super().__init__(name, specialty)
        self.model = model

    def _fallback(self, verifier_findings: List[str], execution_findings: List[str]) -> JurorOpinion:
        strong_negatives = [
            x for x in verifier_findings + execution_findings
            if any(k in x.lower() for k in ["fail", "loop", "incorrect", "timed out", "stuck"])
        ]
        if strong_negatives:
            return JurorOpinion(
                juror_name=self.name,
                specialty=self.specialty,
                verdict="revise",
                confidence=78,
                key_points=["Verifier/runtime evidence suggests robustness concerns."],
                risks=strong_negatives[:4],
                score=78,
                agreements=[],
                disagreements=[],
            )

        return JurorOpinion(
            juror_name=self.name,
            specialty=self.specialty,
            verdict="accept",
            confidence=82,
            key_points=["Verifier and runtime checks suggest the common edge cases are handled."],
            risks=["No major edge-case risks identified."],
            score=82,
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
You are the Edge Cases Juror in a jury-style code review system.

Evaluate ONLY edge cases and robustness.
Use verifier findings and runtime findings as strong evidence.
Do not speculate about NaNs, non-integer values, unrelated contracts, or impossible input types unless the problem explicitly requires them.
Do not discuss time complexity or style.
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

Judge only edge-case robustness.
Focus on: empty input, no-solution input, size-1 input, boundary cases, duplicates, and common special cases implied by the prompt.
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

        raw_key_points = result.get("key_points", []) or ["Some common edge cases may be handled."]
        cleaned_key_points = []
        for point in raw_key_points:
            text = str(point).lower().strip()
            if "no error handling" in text:
                continue
            if "duplicate pairs" in text:
                continue
            if "nan" in text or "non-integer" in text:
                continue
            if "overflow" in text or "maximum limit of the data type" in text:
                continue
            if "duplicate indices" in text:
                continue
            cleaned_key_points.append(point)
        key_points = cleaned_key_points[:4] or ["Some common edge cases may be handled."]

        raw_risks = result.get("risks", []) or []
        cleaned_risks = []
        for risk in raw_risks:
            text = str(risk).lower().strip()

            if text in {"none", "no risk", "no risks"}:
                continue
            if "no major edge-case risks identified" in text:
                continue
            if "nan" in text or "non-integer" in text:
                continue
            if "duplicate target values" in text:
                continue
            if "error handling" in text:
                continue
            if "performance" in text or "inefficient" in text:
                continue
            if "overflow" in text or "maximum limit of the data type" in text:
                continue
            if "duplicate indices" in text:
                continue
            if "potential edge case" in text and "duplicate" in text:
                continue
            if "robustness" == text:
                continue

            cleaned_risks.append(risk)

        merged_risks = cleaned_risks[:]
        for item in verifier_findings + execution_findings:
            low = item.lower()
            if any(k in low for k in ["fail", "loop", "incorrect", "timed out", "stuck"]):
                merged_risks.append(item)

        risks = list(dict.fromkeys(merged_risks))[:4] or ["No major edge-case risks identified."]

        raw_agreements = result.get("agreements", []) or []
        agreements = []
        for a in raw_agreements:
            text = str(a).lower().strip()
            if "juror" in text:
                continue
            if "aligns with juror" in text:
                continue
            if "no major edge-case risks identified" in text:
                continue
            if "nan" in text or "non-integer" in text:
                continue
            if "duplicate target values" in text:
                continue
            agreements.append(a)
        agreements = agreements[:3]

        raw_disagreements = result.get("disagreements", []) or []
        disagreements = []
        for d in raw_disagreements:
            text = str(d).lower().strip()
            if "candidate code seems to be correct" in text:
                continue
            if "verifier findings do not provide sufficient evidence" in text:
                continue
            if "juror" in text:
                continue
            disagreements.append(d)
        disagreements = disagreements[:3]

        verifier_accept = not any(
            any(k in x.lower() for k in ["fail", "loop", "incorrect", "timed out", "stuck"])
            for x in verifier_findings
        )
        execution_accept = not any(
            any(k in x.lower() for k in ["fail", "loop", "incorrect", "timed out", "stuck"])
            for x in execution_findings
        )

        if verifier_accept and execution_accept:
            verdict = "accept"
            confidence = max(confidence, 82)
            score = max(score, 82)
            risks = ["No major edge-case risks identified."]

        if any(any(k in r.lower() for k in ["fail", "loop", "incorrect", "timed out", "stuck"]) for r in risks):
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