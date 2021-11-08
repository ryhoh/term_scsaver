class Color:
    BLACK   = "\u001b[00;30m"
    RED     = "\u001b[00;31m"
    GREEN   = "\u001b[00;32m"
    YELLOW  = "\u001b[00;33m"
    BLUE    = "\u001b[00;34m"
    MAGENTA = "\u001b[00;35m"
    CYAN    = "\u001b[00;36m"
    WHITE   = "\u001b[00;37m"
    END     = "\u001b[00m"

    @staticmethod
    def ansi_colored(text: str, color: str) -> str:
        return "%s%s%s" % (color, text, Color.END)
