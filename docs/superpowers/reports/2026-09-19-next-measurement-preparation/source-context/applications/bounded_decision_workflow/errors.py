"""Bounded, typed S1 refusal diagnostics."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkflowDiagnostic:
    code: str
    stage: str
    target: str
    message_key: str
    retry_class: str
    exit_code: int = 3
    bundle_state: str = "optional_refusal"


class WorkflowInputError(ValueError):
    """A request/snapshot pair was refused before any workflow arithmetic."""

    def __init__(self, diagnostic: WorkflowDiagnostic, *, cause: Exception | None = None):
        super().__init__(diagnostic.code)
        self.diagnostic = diagnostic
        self.__cause__ = cause


def refusal(code: str, *, stage: str, target: str, retry: str,
            exit_code: int = 3) -> WorkflowInputError:
    return WorkflowInputError(WorkflowDiagnostic(
        code=code,
        stage=stage,
        target=target,
        message_key=code.lower(),
        retry_class=retry,
        exit_code=exit_code,
    ))
