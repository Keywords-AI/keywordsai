"""
Logging utilities for KeywordsAI tracing.

This module provides a consistent way to create child loggers that properly
inherit from the main KeywordsAI logger, avoiding the confusing dependency
on __name__ matching the logger prefix.
"""

import logging
from keywordsai_tracing.constants.generic import LOGGER_NAME


def get_keywordsai_logger(name: str) -> logging.Logger:
    """
    Create a child logger under the KeywordsAI logger hierarchy.
    
    This ensures proper inheritance regardless of the LOGGER_NAME value
    and makes the hierarchy explicit and intentional.
    
    Args:
        name: The child logger name (e.g., 'core.exporter', 'core.client')
        
    Returns:
        A logger that inherits from the main KeywordsAI logger
        
    Example:
        # In exporter.py
        from keywordsai_tracing.utils.logging import get_keywordsai_logger
        logger = get_keywordsai_logger('core.exporter')
        
        # In client.py  
        logger = get_keywordsai_logger('core.client')
    """
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def get_main_logger() -> logging.Logger:
    """
    Get the main KeywordsAI logger.
    
    Returns:
        The main KeywordsAI logger instance
    """
    return logging.getLogger(LOGGER_NAME) 