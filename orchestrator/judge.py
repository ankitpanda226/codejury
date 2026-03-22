from dataclasses import asdict
from typing import Any, Dict, List

from models.schemas import ExecutionReport, FinalVerdict, JurorOpinion, VerifierReport


class JudgeAgent:
    def __init__(self, jurors: List[Any]):
        self.jurors = jurors
        self.juror_weights = {
            "Correctness": 0.30,
            "Edge Cases": 0.25,
            "Bug Hunting": 0.20,
            "Complexity": 0.15,
            "Code Quality": 0.10,
        }

    def deliberate(
        self,
        problem: str,
        code: str,
        category: str,
        verifier_report: VerifierReport,
        execution_report: ExecutionReport,
        rounds: int = 2
    ) -> Dict[str, Any]:
        history = []
        opinions: List[JurorOpinion] = []

        verifier_findings = verifier_report.findings + verifier_report.hard_failures
        execution_findings = execution_report.findings

        for round_idx in range(1, rounds + 1):
            round_opinions = [
                juror.evaluate(
                    problem=problem,
                    code=code,
                    category=category,
                    verifier_findings=verifier_findings,
                    execution_findings=execution_findings,
                    prior_opinions=opinions,
                )
                for juror in self.jurors
            ]
            opinions = round_opinions
            history.append({"round": round_idx, "opinions": [asdict(op) for op in round_opinions]})

        final = self._finalize(opinions, category, verifier_report, execution_report)
        return {
            "history": history,
            "final_verdict": asdict(final),
            "verifier_report": asdict(verifier_report),
            "execution_report": asdict(execution_report),
        }

    def _finalize(
        self,
        opinions: List[JurorOpinion],
        category: str,
        verifier_report: VerifierReport,
        execution_report: ExecutionReport,
    ) -> FinalVerdict:
        raw_counts = {"accept": 0, "revise": 0, "reject": 0}
        weighted_votes = {"accept": 0.0, "revise": 0.0, "reject": 0.0}
        weighted_sum = 0.0
        majority_reasons = []
        minority_reasons = []
        improvements = []

        for op in opinions:
            raw_counts[op.verdict] += 1
            weight = self.juror_weights.get(op.specialty, 0.1)
            weighted_votes[op.verdict] += weight
            weighted_sum += op.confidence

            if op.verdict in ("accept", "revise"):
                majority_reasons.extend(op.key_points[:2])
                majority_reasons.extend(op.agreements[:1])
            else:
                minority_reasons.extend(op.risks[:2])
                minority_reasons.extend(op.disagreements[:1])

            for risk in op.risks[:2]:
                text = str(risk).lower().strip()
                if text in {"none", "no risk", "no risks"}:
                    continue
                if "no major" in text:
                    continue
                if "there are no risks identified" in text:
                    continue
                if "no obvious" in text:
                    continue
                if "do not break" in text:
                    continue
                if "handled correctly" in text:
                    continue
                if "returns an empty list" in text and "no pair exists" in text:
                    continue
                if "duplicate-index risk" in text:
                    continue
                if "risk is mitigated" in text:
                    continue
                if "risk is not applicable" in text:
                    continue
                improvements.append(risk)

        minority_reasons.extend(verifier_report.hard_failures[:2])
        for item in verifier_report.findings[:2]:
            if "no obvious" not in item.lower():
                majority_reasons.append(item)
        for item in execution_report.findings[:2]:
            if execution_report.verdict == "accept":
                majority_reasons.append(item)
            else:
                minority_reasons.append(item)

        outcome = max(weighted_votes, key=weighted_votes.get)
        confidence = round(weighted_sum / max(1, len(opinions)), 1)

        high_conf_reject_by_critical = any(
            op.verdict == "reject"
            and op.confidence >= 35
            and op.specialty in {"Bug Hunting", "Correctness"}
            for op in opinions
        )

        correctness_bug_conflict = any(
            op.specialty == "Bug Hunting" and op.verdict == "reject" and op.confidence >= 35
            for op in opinions
        ) and any(
            op.specialty == "Correctness" and op.verdict == "accept"
            for op in opinions
        )

        if verifier_report.verdict == "reject" or execution_report.verdict == "reject":
            outcome = "revise"

        if high_conf_reject_by_critical:
            outcome = "revise"

        if correctness_bug_conflict:
            outcome = "revise"
            minority_reasons.insert(0, "A critical juror found a likely implementation bug, so acceptance is unsafe without revision.")

        if outcome == "accept":
            summary = "After deliberation, the jury believes the solution is mostly sound, with some room for refinement."
        elif outcome == "revise":
            summary = "After deliberation, the jury sees promise but recommends revision before acceptance."
        else:
            summary = "After deliberation, the jury does not consider the current solution reliable enough to approve."

        return FinalVerdict(
            outcome=outcome,
            confidence=confidence,
            summary=summary,
            majority_reasons=list(dict.fromkeys(majority_reasons))[:6],
            minority_reasons=list(dict.fromkeys(minority_reasons))[:6],
            improvements=list(dict.fromkeys(improvements))[:6],
            vote_tally={k: round(v, 2) for k, v in weighted_votes.items()},
            raw_vote_counts=raw_counts,
            category=category,
            verifier_findings=verifier_report.findings + verifier_report.hard_failures,
            execution_findings=execution_report.findings,
        )