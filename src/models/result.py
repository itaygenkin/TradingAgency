from dataclasses import dataclass
from typing import Optional, TypeVar, Generic
from src.models.result_status import ResultStatus

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    status: ResultStatus
    value: T
    msg: Optional[str] = None

    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS


@dataclass
class EvaluationValue:
    is_correct: bool
    confidence_score: int
