from abc import ABC, abstractmethod

from models.schemas import VerifierReport


class BaseVerifier(ABC):
    @abstractmethod
    def verify(self, problem: str, code: str) -> VerifierReport:
        raise NotImplementedError