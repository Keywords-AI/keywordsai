def is_notebook() -> bool:
    """
    Detect if we're running in a Jupyter notebook environment.
    In notebooks, we prefer SimpleSpanProcessor over BatchSpanProcessor
    for immediate feedback.
    """
    try:
        # Check for IPython kernel
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    
    return False 