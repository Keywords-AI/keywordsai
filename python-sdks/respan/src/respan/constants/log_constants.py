"""
Log API constants for Keywords AI SDK

This module defines constants for log-related API endpoints and status codes.
"""

# Log API endpoints
LOG_BASE_PATH = "request-logs"
LOG_CREATION_PATH = f"{LOG_BASE_PATH}/create"
LOG_LIST_PATH = f"{LOG_BASE_PATH}/list"
LOG_GET_PATH = f"{LOG_BASE_PATH}"

__all__ = [
    "LOG_BASE_PATH",
    "LOG_CREATION_PATH", 
    "LOG_LIST_PATH",
    "LOG_GET_PATH",
]