from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypeVar, Generic

T = TypeVar("T")

class ResultStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class Result(Generic[T]):
    status: ResultStatus
    value: T
    msg: Optional[str] = None

    def __post_init__(self):
        if self.status != ResultStatus.SUCCESS:
            assert self.msg is not None, "Error message is required for failed results"

    def is_success(self) -> bool:
        assert self.value is not None
        return self.status == ResultStatus.SUCCESS


@dataclass
class EvaluationValue:
    is_correct: bool
    confidence_score: int
