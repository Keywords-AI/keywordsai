"""
Reusable retry handler for sync operations (e.g. HTTP export calls).

Shared by respan exporters. Use this instead of inline while loops with time.sleep.

Usage:
    from respan_sdk.utils.retry_handler import RetryHandler

    handler = RetryHandler(max_retries=3, retry_delay=1.0, backoff_multiplier=2.0)
    result = handler.execute(lambda: http_post(url, data), context="export ingest")
"""

import logging
import random
import time
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Sync retry with exponential backoff and optional jitter.

    Attributes:
        max_retries: Maximum number of attempts (default: 3).
        retry_delay: Base delay in seconds between retries (default: 1.0).
        backoff_multiplier: Exponential backoff multiplier (default: 2.0).
        max_delay: Cap delay in seconds (default: None).
        jitter_fraction: Fraction of delay added as random jitter 0–1 (default: 0.1).
        log_retries: Whether to log retry attempts (default: True).
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: Optional[float] = None,
        jitter_fraction: float = 0.1,
        log_retries: bool = True,
    ) -> None:
        self.max_retries = max(1, max_retries)
        self.retry_delay = max(0.0, retry_delay)
        self.backoff_multiplier = max(1.0, backoff_multiplier)
        self.max_delay = max(0.0, max_delay) if max_delay is not None else None
        self.jitter_fraction = max(0.0, min(1.0, jitter_fraction))
        self.log_retries = log_retries

    def execute(
        self,
        func: Callable[[], T],
        context: str = "operation",
    ) -> T:
        """
        Execute func with retries. Raises the last exception if all attempts fail.
        """
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                result = func()
                if attempt > 0 and self.log_retries:
                    logger.warning(
                        "Success on retry %s/%s for %s",
                        attempt,
                        self.max_retries - 1,
                        context,
                    )
                return result
            except Exception as e:
                last_error = e
                is_last = attempt == self.max_retries - 1
                if self.log_retries:
                    if is_last:
                        logger.error(
                            "All %s retries exhausted for %s: %s",
                            self.max_retries,
                            context,
                            e,
                        )
                    else:
                        logger.warning(
                            "Retry %s/%s for %s: %s",
                            attempt + 1,
                            self.max_retries,
                            context,
                            e,
                        )
                if is_last:
                    raise last_error
                delay = self.retry_delay * (self.backoff_multiplier ** attempt)
                if self.jitter_fraction > 0:
                    delay += delay * self.jitter_fraction * random.random()
                if self.max_delay is not None:
                    delay = min(delay, self.max_delay)
                if delay > 0:
                    time.sleep(delay)
