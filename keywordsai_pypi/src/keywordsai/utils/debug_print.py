from .bgcolors import BgColors

def print_color(color: str, text:str, *args, **kwargs):
    print(f"{color}{text}{BgColors.ENDC}", *args, **kwargs)
    
def print_error(text, *args, **kwargs):
    print_color(color=BgColors.FAIL, text=text, *args, **kwargs)
    
def print_warning(text, *args, **kwargs):
    print_color(color=BgColors.WARNING, text=text, *args, **kwargs)
    
def print_info(text, *args, **kwargs):
    print_color(color=BgColors.OKBLUE, text=text, *args, **kwargs)
    
def print_success(text, *args, **kwargs):
    """
    print_success: Print success message in green color
    """
    print_color(color=BgColors.OKGREEN, text=text, *args, **kwargs)
    
def print_bold(text, *args, **kwargs):
    print_color(color=BgColors.BOLD, text=text, *args, **kwargs)
    
def print_underline(text, *args, **kwargs):
    print_color(color=BgColors.UNDERLINE, text=text, *args, **kwargs)
     