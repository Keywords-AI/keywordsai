"""Respan Haystack integration package.

Public API (re-exported for backward compatibility):
    from respan_exporter_haystack import RespanConnector, RespanGenerator, RespanChatGenerator, RespanTracer

Or import from submodules:
    from respan_exporter_haystack.connector import RespanConnector
    from respan_exporter_haystack.gateway import RespanGenerator, RespanChatGenerator
    from respan_exporter_haystack.tracer import RespanTracer
"""

from importlib.metadata import PackageNotFoundError, version

from respan_exporter_haystack.connector import RespanConnector
from respan_exporter_haystack.gateway import RespanChatGenerator, RespanGenerator
from respan_exporter_haystack.tracer import RespanTracer

try:
    __version__ = version("respan-exporter-haystack")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["RespanConnector", "RespanGenerator", "RespanChatGenerator", "RespanTracer"]
