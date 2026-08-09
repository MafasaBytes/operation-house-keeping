"""Typed error tree for the model kernel.

Kept in its own module so every layer — including ``canonical``, which
``contracts`` imports — can raise through the public contract without an
import cycle. Every OPERATIONAL public entry point of the kernel
(stores, queries, ``build_record``, collection validation) fails through
this tree: raw ``ValidationError``, ``KeyError``, ``AttributeError``,
``TypeError``, ``OSError``, ``UnicodeError``, serializer errors, and
warnings never escape as the public outcome. Direct construction of the
pydantic contract models is the deliberate carve-out and follows
pydantic's normal ``ValidationError`` contract. Messages carry model ids,
record ids, and file names — never absolute paths.
"""


class ModelKernelError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message


class ModelConfigurationError(ModelKernelError):
    """Invalid model-set root or model id."""


class ModelIntegrityError(ModelKernelError):
    """The model set violates an integrity invariant, a supplied record is
    not structurally valid, or the store could not be read or written.
    Validation is all-or-nothing: an invalid set resolves nothing."""


class ModelQueryError(ModelKernelError):
    """Contract misuse at the query boundary. Absence and disagreement are
    statuses, never exceptions."""
