"""Respan Braintrust Exporter.

This package provides a Braintrust exporter that sends traces to Respan.

Usage:
    from respan_exporter_braintrust import RespanBraintrustExporter

    with RespanBraintrustExporter(api_key="...") as exporter:
        logger = braintrust.init_logger(project="My Project")
        # ... log spans ...
        logger.flush()
"""

from respan_exporter_braintrust.exporter import RespanBraintrustExporter

__all__ = ["RespanBraintrustExporter"]
