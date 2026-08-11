"""SN-001 typed errors. Stable error codes; no path, secret, or payload
content in messages."""


class StructuralEvidenceError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class StructuralEvidenceConfigurationError(StructuralEvidenceError):
    """Invalid construction input to an SN-001 facade or builder."""
