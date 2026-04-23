# utils.py

import logging
import sys
from django.conf import settings

# ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"

COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

def color_text(text, color=None, bold=False):
    c = COLORS.get(color, "")
    b = BOLD if bold else ""
    return f"{b}{c}{text}{RESET}"

class ColorFormatter(logging.Formatter):
    """Custom formatter to colorize log messages based on log level and content."""

    def format(self, record):
        level_color = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "magenta",
        }.get(record.levelname, "white")

        msg = super().format(record)
        msg = msg.replace("[TOOL_CALL]", color_text("[TOOL_CALL]", "yellow", True))
        msg = msg.replace("[TOOL_OUTPUT]", color_text("[TOOL_OUTPUT]", "green", True))
        msg = msg.replace("[PROMPT_PREVIEW]", color_text("[PROMPT_PREVIEW]", "magenta", True))
        msg = msg.replace("[FAISS]", color_text("[FAISS]", "cyan", True))
        msg = msg.replace("[EXECUTAR_INTENCAO]", color_text("[EXECUTAR_INTENCAO]", "blue", True))

        return color_text(msg, level_color)
    

def configurar_logger_colorido():
    """Aplica o formato colorido globalmente."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = ColorFormatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG)


def get_db_from_slug(slug: str | None, default: str = "default") -> str:
    """
    Resolve o alias do banco a partir de um slug.
    Se o slug não existir na configuração, retorna `default`.
    """
    if not slug:
        return default

    slug_normalizado = str(slug).strip().lower()
    dbs = getattr(settings, "DATABASES", {})
    return slug_normalizado if slug_normalizado in dbs else default
