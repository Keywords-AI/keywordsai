"""
Utility functions for dynamic imports.
"""

import importlib
import logging
from typing import Any, Type

logger = logging.getLogger(__name__)


def import_from_string(import_string: str) -> Any:
    """
    Import a class or function from a string path.
    
    Args:
        import_string: Import path in format "module.path.ClassName"
        
    Returns:
        The imported class or function
        
    Raises:
        ImportError: If the module or attribute cannot be imported
        
    Example:
        >>> MyClass = import_from_string("my.module.MyClass")
        >>> instance = MyClass()
    """
    try:
        # Split the import string into module and attribute
        module_path, class_name = import_string.rsplit('.', 1)
        
        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the class/function from the module
        imported_item = getattr(module, class_name)
        
        logger.debug(f"Successfully imported {class_name} from {module_path}")
        return imported_item
        
    except ValueError as e:
        raise ImportError(
            f"Invalid import string format '{import_string}'. "
            f"Expected format: 'module.path.ClassName'"
        ) from e
    except ModuleNotFoundError as e:
        raise ImportError(
            f"Module '{module_path}' not found for import string '{import_string}'"
        ) from e
    except AttributeError as e:
        raise ImportError(
            f"'{class_name}' not found in module '{module_path}' "
            f"for import string '{import_string}'"
        ) from e
    except Exception as e:
        raise ImportError(
            f"Failed to import '{import_string}': {str(e)}"
        ) from e


def safe_import_from_string(import_string: str, fallback: Any = None) -> Any:
    """
    Safely import a class or function from a string path with fallback.
    
    Args:
        import_string: Import path in format "module.path.ClassName"
        fallback: Value to return if import fails
        
    Returns:
        The imported class/function, or fallback if import fails
        
    Example:
        >>> MyClass = safe_import_from_string("my.module.MyClass", fallback=DefaultClass)
    """
    try:
        return import_from_string(import_string)
    except ImportError as e:
        logger.warning(f"Failed to import '{import_string}': {e}")
        return fallback


def validate_import_string(import_string: str) -> bool:
    """
    Validate that an import string has the correct format.
    
    Args:
        import_string: Import path to validate
        
    Returns:
        True if format is valid, False otherwise
        
    Example:
        >>> validate_import_string("my.module.MyClass")  # True
        >>> validate_import_string("invalid")  # False
    """
    try:
        parts = import_string.split('.')
        return len(parts) >= 2 and all(part.isidentifier() for part in parts)
    except (AttributeError, TypeError):
        return False
