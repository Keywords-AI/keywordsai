"""Respan Haystack integration package.

Import components directly from implementation modules:
    from respan_exporter_haystack.connector import RespanConnector
    from respan_exporter_haystack.gateway import RespanGenerator, RespanChatGenerator
    from respan_exporter_haystack.tracer import RespanTracer
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("respan-exporter-haystack")
except PackageNotFoundError:
    __version__ = "0.0.0"
