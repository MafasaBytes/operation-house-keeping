"""Typed public failures for the source-interpretation ledger."""


class SourceInterpretationError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class InterpretationConfigurationError(SourceInterpretationError):
    """Invalid interpretation-set root, id, or record location."""


class InterpretationIntegrityError(SourceInterpretationError):
    """An interpretation set violates an all-or-nothing invariant."""


class InterpretationResolutionError(SourceInterpretationError):
    """Invalid input to source-property interpretation resolution."""

