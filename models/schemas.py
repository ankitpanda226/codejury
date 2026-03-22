from dataclasses import dataclass
from typing import Dict, List


@dataclass
class JurorOpinion:
    juror_name: str
    specialty: str
    verdict: str
    confidence: int
    key_points: List[str]
    risks: List[str]
    score: int
    agreements: List[str]
    disagreements: List[str]


@dataclass
class VerifierReport:
    category: str
    verdict: str
    confidence: int
    findings: List[str]
    hard_failures: List[str]


@dataclass
class ExecutionReport:
    supported: bool
    verdict: str
    confidence: int
    findings: List[str]
    passed: int
    total: int


@dataclass
class FinalVerdict:
    outcome: str
    confidence: float
    summary: str
    majority_reasons: List[str]
    minority_reasons: List[str]
    improvements: List[str]
    vote_tally: Dict[str, float]
    raw_vote_counts: Dict[str, int]
    category: str
    verifier_findings: List[str]
    execution_findings: List[str]