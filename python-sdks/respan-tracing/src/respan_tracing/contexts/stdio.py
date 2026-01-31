import sys
import os
from contextlib import contextmanager
from typing import TextIO


@contextmanager
def suppress_stdout():
    """
    Context manager to suppress stdout output.
    Useful for hiding verbose initialization messages from libraries.
    """
    original_stdout = sys.stdout
    try:
        # Redirect stdout to devnull
        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            yield
    finally:
        # Restore original stdout
        sys.stdout = original_stdout


@contextmanager
def suppress_stderr():
    """
    Context manager to suppress stderr output.
    """
    original_stderr = sys.stderr
    try:
        # Redirect stderr to devnull
        with open(os.devnull, 'w') as devnull:
            sys.stderr = devnull
            yield
    finally:
        # Restore original stderr
        sys.stderr = original_stderr


@contextmanager
def suppress_all_output():
    """
    Context manager to suppress both stdout and stderr output.
    """
    with suppress_stdout():
        with suppress_stderr():
            yield