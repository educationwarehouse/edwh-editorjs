import abc
import typing as t
from dataclasses import dataclass

import bleach

from .exceptions import EditorJsParseError

__all__ = [
    "block",
    "BLOCKS_MAP",
    "EditorJsBlock",
]


def _sanitize(html: str) -> str:
    return bleach.clean(
        html,
        tags=["b", "i", "u", "a", "mark", "code"],
        attributes=["class", "data-placeholder", "href"],
    )


BLOCKS_MAP: t.Dict[str, t.Type["EditorJsBlock"]] = {
    # 'header': HeaderBlock,
    # 'paragraph': ParagraphBlock,
    # 'list': ListBlock,
    # 'delimiter': DelimiterBlock,
    # 'image': ImageBlock,
}


def block(_type: str):
    def wrapper(cls: t.Type["EditorJsBlock"]):
        BLOCKS_MAP[_type] = cls
        return cls

    return wrapper


@dataclass
class EditorJsBlock(abc.ABC):
    """
    A generic parsed Editor.js block
    """

    _data: dict
    """The raw JSON data of the entire block"""

    @property
    def id(self) -> t.Optional[str]:
        """
        Returns ID of the block, generated client-side.
        """

        return self._data.get("id", None)

    @property
    def type(self) -> t.Optional[str]:
        """
        Returns the type of the block.
        """

        return self._data.get("type", None)

    @property
    def data(self) -> dict:
        """
        Returns the actual block data.
        """

        return self._data.get("data", {})

    @abc.abstractmethod
    def html(self, sanitize: bool = False) -> str:
        """
        Returns the HTML representation of the block.

        ### Parameters:
        - `sanitize` - if `True`, then the block's text/contents will be sanitized.
        """

        raise NotImplementedError()


@block("header")
class HeaderBlock(EditorJsBlock):
    VALID_HEADER_LEVEL_RANGE = range(1, 7)
    """Valid range for header levels. Default is `range(1, 7)` - so, `0` - `6`."""

    @property
    def text(self) -> str:
        """
        Returns the header's text.
        """

        return self.data.get("text", "")

    @property
    def level(self) -> int:
        """
        Returns the header's level (`0` - `6`).
        """

        _level = self.data.get("level", 1)

        if not isinstance(_level, int) or _level not in self.VALID_HEADER_LEVEL_RANGE:
            raise EditorJsParseError(f"`{_level}` is not a valid header level.")

        return _level

    def html(self, sanitize: bool = False) -> str:
        text = self.text
        if sanitize:
            text = _sanitize(text)
        return rf'<h{self.level} class="cdx-block ce-header">{text}</h{self.level}>'


@block("paragraph")
class ParagraphBlock(EditorJsBlock):
    @property
    def text(self) -> str:
        """
        The text content of the paragraph.
        """

        return self.data.get("text", "")

    def html(self, sanitize: bool = False) -> str:
        return rf'<p class="cdx-block ce-paragraph">{_sanitize(self.text) if sanitize else self.text}</p>'


@block("list")
class ListBlock(EditorJsBlock):
    VALID_STYLES = ("unordered", "ordered")
    """Valid list order styles."""

    @property
    def style(self) -> t.Optional[str]:
        """
        The style of the list. Can be `ordered` or `unordered`.
        """

        return self.data.get("style", None)

    @property
    def items(self) -> t.List[str]:
        """
        Returns the list's items, in raw format.
        """

        return self.data.get("items", [])

    def html(self, sanitize: bool = False) -> str:
        if self.style not in self.VALID_STYLES:
            raise EditorJsParseError(f"`{self.style}` is not a valid list style.")

        _items = [
            f"<li>{_sanitize(item) if sanitize else item}</li>" for item in self.items
        ]
        _type = "ul" if self.style == "unordered" else "ol"
        _items_html = "".join(_items)

        return rf'<{_type} class="cdx-block cdx-list cdx-list--{self.style}">{_items_html}</{_type}>'


@block("delimiter")
class DelimiterBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        return r'<div class="cdx-block ce-delimiter"></div>'


@block("image")
class ImageBlock(EditorJsBlock):
    @property
    def file_url(self) -> str:
        """
        URL of the image file.
        """

        return self.data.get("file", {}).get("url", "")

    @property
    def caption(self) -> str:
        """
        The image's caption.
        """

        return self.data.get("caption", "")

    @property
    def with_border(self) -> bool:
        """
        Whether the image has a border.
        """

        return self.data.get("withBorder", False)

    @property
    def stretched(self) -> bool:
        """
        Whether the image is stretched.
        """

        return self.data.get("stretched", False)

    @property
    def with_background(self) -> bool:
        """
        Whether the image has a background.
        """

        return self.data.get("withBackground", False)

    def html(self, sanitize: bool = False) -> str:
        if self.file_url.startswith("data:image/"):
            _img = self.file_url
        else:
            _img = _sanitize(self.file_url) if sanitize else self.file_url

        parts = [
            rf'<div class="cdx-block image-tool image-tool--filled {"image-tool--stretched" if self.stretched else ""} {"image-tool--withBorder" if self.with_border else ""} {"image-tool--withBackground" if self.with_background else ""}">'
            r'<div class="image-tool__image">',
            r'<div class="image-tool__image-preloader"></div>',
            rf'<img class="image-tool__image-picture" src="{_img}"/>',
            r"</div>"
            rf'<div class="image-tool__caption" data-placeholder="{_sanitize(self.caption) if sanitize else self.caption}"></div>'
            r"</div>"
            r"</div>",
        ]

        return "".join(parts)


@block("quote")
class QuoteBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        quote = self.data.get("text", "")
        caption = self.data.get("caption", "")
        if sanitize:
            quote = _sanitize(quote)
            caption = _sanitize(caption)
        _alignment = self.data.get("alignment", "left")  # todo
        return f"""
        <blockquote class="cdx-block cdx-quote">
            <div class="cdx-input cdx-quote__text">{quote}</div>
            <cite class="cdx-input cdx-quote__caption">{caption}</cite>
        </blockquote>
        """


@block("table")
class TableBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        content = self.data.get("content", [])
        _stretched = self.data.get("stretched", False)  # todo
        _with_headings = self.data.get("withHeadings", False)  # todo

        html_table = '<table class="tc-table">'

        # Add content rows
        for row in content:
            html_table += '<tr class="tc-row">'
            for cell in row:
                html_table += (
                    f'<td class="tc-cell">{_sanitize(cell) if sanitize else cell}</td>'
                )
            html_table += "</tr>"

        html_table += "</table>"
        return html_table


@block("code")
class CodeBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        code = self.data.get("code", "")
        if sanitize:
            code = _sanitize(code)
        return f"""
        <code class="ce-code__textarea cdx-input" data-empty="false">{code}</code>
        """


@block("warning")
class WarningBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        title = self.data.get("title", "")
        message = self.data.get("message", "")

        if sanitize:
            title = _sanitize(title)
            message = _sanitize(message)

        return f"""
            <div class="cdx-block cdx-warning">
                <div class="cdx-input cdx-warning__title">{title}</div>
                <div class="cdx-input cdx-warning__message">{message}</div>
            </div>
        """


@block("raw")
class RawBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        html = self.data.get("html", "")
        if sanitize:
            html = _sanitize(html)
        return html
