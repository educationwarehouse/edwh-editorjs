import json
import typing as t
import warnings

import markdown2
import mdast
from typing_extensions import Self

from .blocks import BLOCKS
from .exceptions import TODO
from .helpers import unix_timestamp
from .types import MDRootNode

EDITORJS_VERSION = "2.30.6"


class EditorJS:
    # internal representation is mdast, because we can convert to other types
    _mdast: MDRootNode

    def __init__(
        self,
        _mdast: str | dict,
        extras: list = ("task_list", "fenced-code-blocks", "tables", "editorjs"),
    ):
        if not isinstance(_mdast, str | dict):
            raise TypeError("Only `str` or `dict` is supported!")

        self._mdast = t.cast(
            MDRootNode, json.loads(_mdast) if isinstance(_mdast, str) else _mdast
        )

        self._md = markdown2.Markdown(extras=extras)  # todo: striketrough, ?

    @classmethod
    def from_json(cls, data: str | dict | list) -> Self:
        """
        Load from EditorJS JSON Blocks
        """
        data = data if isinstance(data, (dict, list)) else json.loads(data)
        blocks = data["blocks"] if isinstance(data, dict) else data
        markdown_items = []
        for child in blocks:
            _type = child["type"]
            if not (block := BLOCKS.get(_type)):
                warnings.warn(
                    f"from_json: Unsupported block type `{_type}`",
                    category=RuntimeWarning,
                )
                continue

            try:
                data = child.get("data", {})
                # forward any 'tunes' via data:
                data["tunes"] = data.get("tunes") or child.get("tunes") or {}

                markdown_items.append(block.to_markdown(data))
            except Exception as e:
                warnings.warn(
                    "from_json: Oh oh, unexpected block failure!",
                    category=RuntimeWarning,
                    source=e,
                )
                # if isinstance(e, TODO):
                #     raise e

        markdown = "".join(markdown_items)
        return cls.from_markdown(markdown)

    @classmethod
    def from_markdown(cls, data: str) -> Self:
        """
        Load from markdown string
        """

        return cls(mdast.md_to_json(data))

    @classmethod
    def from_mdast(cls, data: str | dict) -> Self:
        """
        Existing mdast representation
        """
        return cls(data)

    def to_json(self) -> str:
        """
        Export EditorJS JSON Blocks
        """
        # logic based on https://github.com/carrara88/editorjs-md-parser/blob/main/src/MarkdownImporter.js
        blocks = []
        for child in self._mdast["children"]:
            _type = child["type"]
            if not (block := BLOCKS.get(_type)):
                warnings.warn(
                    f"to_json: Unsupported block type `{_type}`",
                    category=RuntimeWarning,
                )
                continue

            try:
                blocks.extend(block.to_json(child))
            except Exception as e:
                warnings.warn(
                    "to_json: Oh oh, unexpected block failure!",
                    category=RuntimeWarning,
                    source=e,
                )
                # if isinstance(e, TODO):
                #     raise e

        data = {"time": unix_timestamp(), "blocks": blocks, "version": EDITORJS_VERSION}

        return json.dumps(data)

    def to_markdown(self) -> str:
        """
        Export Markdown string
        """
        md = mdast.json_to_md(self.to_mdast())
        # idk why this happens:
        md = md.replace(r"\[ ]", "[ ]")
        md = md.replace(r"\[x]", "[x]")
        return md.replace(
            "  <", " <"
        )  # replace double space (added by mdast) with single one

    def to_mdast(self) -> str:
        """
        Export mdast representation
        """
        return json.dumps(self._mdast)

    def to_html(self) -> str:
        """
        Export HTML string
        """
        md = self.to_markdown()
        # todo: deal with custom elements like linktool, attaches
        return self._md.convert(md)

    def __repr__(self):
        md = self.to_markdown()
        md = md.replace("\n", "\\n")
        return f"EditorJS({md})"

    def __str__(self):
        return self.to_markdown()

    # def __eq__(self, other: Self) -> bool:
    #     a = self.to_markdown()
    #     b = other.to_markdown()
    #
    #     remove = string.punctuation + string.whitespace
    #     return a.translate(remove) == b.translate(remove)
