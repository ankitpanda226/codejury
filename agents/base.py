from abc import ABC, abstractmethod
from typing import List, Optional

from models.schemas import JurorOpinion


class BaseJuror(ABC):
    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty

    @abstractmethod
    def evaluate(
        self,
        problem: str,
        code: str,
        category: str,
        verifier_findings: List[str],
        execution_findings: List[str],
        prior_opinions: Optional[List[JurorOpinion]] = None,
    ) -> JurorOpinion:
        raise NotImplementedError