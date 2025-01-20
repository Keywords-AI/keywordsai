from .bgcolors import BgColors
from keywordsai_sdk.keywordsai_config import DEBUG

def print_color(color: str, text: str, *args, **kwargs):
    print_function = kwargs.pop("print_func", print) or print
    print_function(f"{color}{text}{BgColors.ENDC}", *args, **kwargs)


def print_error(text, print_func=None, *args, **kwargs):
    print_color(color=BgColors.FAIL, text=text, print_func=print_func, *args, **kwargs)


def print_warning(text, *args, **kwargs):
    print_color(color=BgColors.WARNING, text=text, *args, **kwargs)


def print_info(text, print_func=None, *args, **kwargs):
    print_color(
        color=BgColors.OKBLUE, text=text, print_func=print_func, *args, **kwargs
    )


def print_success(text, *args, **kwargs):
    """
    print_success: Print success message in green color
    """
    print_color(color=BgColors.OKGREEN, text=text, *args, **kwargs)


def print_bold(text, *args, **kwargs):
    print_color(color=BgColors.BOLD, text=text, *args, **kwargs)


def print_underline(text, *args, **kwargs):
    print_color(color=BgColors.UNDERLINE, text=text, *args, **kwargs)

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def debug(func):
    def wrapper(*args, **kwargs):
        if DEBUG:
            return func(*args, **kwargs)
        else:
            return lambda *args, **kwargs: None

    return wrapper
