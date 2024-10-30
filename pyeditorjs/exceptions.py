__all__ = [
    "EditorJsException",
    "EditorJsParseError",
    "EditorJSUnsupportedBlock",
]


class EditorJsException(Exception):
    """
    Base exception
    """


class EditorJsParseError(EditorJsException):
    """Raised when a parse error occurs (example: the JSON data has invalid or malformed content)."""


class EditorJSUnsupportedBlock(EditorJsException):
    """Raised when strict=True and using an unknown block type."""
