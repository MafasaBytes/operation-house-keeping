"""Public ST-001 state-classification errors."""


class StateClassificationError(Exception):
    """Base error for facade configuration and structural input misuse."""

    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class StateClassificationConfigurationError(StateClassificationError):
    """Invalid read-only facade construction."""


class StateClassificationInputError(StateClassificationError):
    """Structurally invalid classification request or condition-source set."""
