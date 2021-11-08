# c.f. https://misc.flogisoft.com/bash/tip_colors_and_formatting

class Color:
    BLACK   = "\u001b[00;30m"
    RED     = "\u001b[00;31m"
    GREEN   = "\u001b[00;32m"
    YELLOW  = "\u001b[00;33m"
    BLUE    = "\u001b[00;34m"
    MAGENTA = "\u001b[00;35m"
    CYAN    = "\u001b[00;36m"
    WHITE   = "\u001b[00;37m"
    
    # CHAR_256_BEGIN = "\u001b[38;5;%dm"
    # BG_256_BEGIN   = "\u001b[48;5;%dm"
    END            = "\u001b[00m"

    @staticmethod
    def ansi_colored(text: str, color: str) -> str:
        return "%s%s%s" % (color, text, Color.END)

    @staticmethod
    def char_256_colored(text: str, color_number: int, bg_color_number: int = None) -> str:
        # begin = Color.CHAR_256_BEGIN % color_number
        if bg_color_number is None:
            return "\u001b[38;5;%dm%s%s" % (color_number, text, Color.END)
        return "\u001b[38;5;%dm\u001b[48;5;%dm%s%s" % (color_number, bg_color_number, text, Color.END)
