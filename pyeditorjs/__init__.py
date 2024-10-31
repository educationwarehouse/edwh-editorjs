from pathlib import Path

from .blocks import BLOCKS_MAP, EditorJsBlock, block
from .exceptions import EditorJsException, EditorJsParseError, EditorJSUnsupportedBlock
from .parser import EditorJsParser

__all__ = [
    "EditorJsParser",
    "EditorJsParseError",
    "EditorJsException",
    "EditorJSUnsupportedBlock",
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


if __name__ == "__main__":
    _ = [EditorJsParser]
