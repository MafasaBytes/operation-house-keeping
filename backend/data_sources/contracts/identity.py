"""Extractor identity: which tool, version, and configuration produced an
extraction output."""

from typing import Annotated

from pydantic import StringConstraints

from backend.data_sources.contracts.models import _FrozenModel

NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]

class ExtractorIdentity(_FrozenModel):
    name: NonEmptyStr
    version: NonEmptyStr
    toolchain: NonEmptyStr
    config_fingerprint: NonEmptyStr
