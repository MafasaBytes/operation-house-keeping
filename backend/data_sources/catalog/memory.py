"""In-memory source catalog for DS-001."""

from backend.data_sources.contracts import SourceDefinition


class UnknownSourceError(KeyError):
    pass


class InMemorySourceCatalog:
    def __init__(self) -> None:
        self._sources: dict[str, SourceDefinition] = {}

    def register(self, source: SourceDefinition) -> None:
        existing = self._sources.get(source.source_id)
        if existing is not None and existing != source:
            raise ValueError(
                f"source {source.source_id!r} is already registered with a "
                "different definition; source ids are stable identities"
            )
        self._sources[source.source_id] = source

    def get(self, source_id: str) -> SourceDefinition:
        try:
            return self._sources[source_id]
        except KeyError:
            raise UnknownSourceError(source_id) from None

    def list_sources(self, enabled_only: bool = False) -> list[SourceDefinition]:
        sources = self._sources.values()
        return [s for s in sources if s.enabled or not enabled_only]
