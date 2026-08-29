"""Public BH-001 evaluator errors."""


class BehaviorEvaluationError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class BehaviorEvaluationConfigurationError(BehaviorEvaluationError):
    """Invalid read-only facade construction."""


class BehaviorEvaluationInputError(BehaviorEvaluationError):
    """Structurally invalid evaluation request or participant set."""
