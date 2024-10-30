from pathlib import Path

__all__ = [
    "EditorJsParser",
    "EditorJsParseError",
    "EditorJsBlock",
    "block",
    "BLOCKS_MAP",
]


# Overwrite __doc__ with README, so that pdoc can render it:
README_PATH = Path(__file__).parent.parent.absolute() / Path("README.md")
try:
    with open(README_PATH, "r", encoding="UTF-8") as readme:
        __readme__ = readme.read()
except Exception:
    __readme__ = "Failed to read README.md!"  # fallback message, for example when there's no README

__doc__ = __readme__


from .blocks import *
from .exceptions import EditorJsParseError
from .parser import EditorJsParser

if __name__ == "__main__":
    _ = [EditorJsParser]
