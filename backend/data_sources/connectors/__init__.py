"""Connector implementations (acquisition only, no format extraction)."""

from backend.data_sources.connectors.local_file import Acquisition, LocalFileConnector

__all__ = ["Acquisition", "LocalFileConnector"]
