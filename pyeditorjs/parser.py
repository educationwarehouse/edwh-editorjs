import typing as t
import warnings
from dataclasses import dataclass

from .blocks import BLOCKS_MAP, EditorJsBlock
from .exceptions import EditorJsParseError, EditorJSUnsupportedBlock


@dataclass
class EditorJsParser:
    """
    An Editor.js parser.
    """

    content: dict
    """The JSON data of Editor.js content."""

    def __post_init__(self) -> None:
        if not isinstance(self.content, dict):
            raise EditorJsParseError(
                f"Content must be `dict`, not {type(self.content).__name__}"
            )

    @staticmethod
    def _get_block(data: dict, strict: bool = False) -> t.Optional[EditorJsBlock]:
        """
        Obtains block instance from block data.
        """

        _type = data.get("type", None)

        if _type not in BLOCKS_MAP:
            if strict:
                raise EditorJSUnsupportedBlock(_type)
            else:
                warnings.warn(f"Unsupported block: {_type}", category=RuntimeWarning)
                return None

        return BLOCKS_MAP[_type](_data=data)

    def blocks(self, strict: bool = False) -> list[EditorJsBlock]:
        """
        Obtains a list of all available blocks from the editor's JSON data.
        """

        all_blocks: list[EditorJsBlock] = []
        blocks = self.content.get("blocks", [])

        if not isinstance(blocks, list):
            raise EditorJsParseError(
                f"Blocks is not `list`, but `{type(blocks).__name__}`"
            )

        for block_data in blocks:
            if block := self._get_block(data=block_data, strict=strict):
                all_blocks.append(block)

        return all_blocks

    def __iter__(self) -> t.Iterator[EditorJsBlock]:
        """Returns `iter(self.blocks())`"""

        return iter(self.blocks())

    def html(self, sanitize: bool = False, strict: bool = False) -> str:
        """
        Renders the editor's JSON content as HTML.

        ### Parameters:
        - `sanitize` - whether to also sanitize the blocks' texts/contents.
        """

        return "\n".join(
            [block.html(sanitize=sanitize) for block in self.blocks(strict=strict)]
        )
