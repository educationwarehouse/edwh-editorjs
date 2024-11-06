import typing as t


class MDPosition(t.TypedDict):
    line: int
    column: int
    offset: int


class MDPositionRange(t.TypedDict):
    start: MDPosition
    end: MDPosition


class MDChildNode(t.TypedDict, total=False):
    type: str  # General identifier for node types
    children: list["MDChildNode"]  # Recursive children of any node type
    position: MDPositionRange
    value: str  # Optional, for nodes like text that hold a value
    depth: int  # Optional, for nodes like headings that have a depth
    url: t.NotRequired[str]


class MDRootNode(t.TypedDict):
    type: t.Literal["root"]  # Constrains to 'root' for the root node
    children: list[MDChildNode]  # Allows any ChildNode type in children
    position: MDPositionRange


class EditorChildData(t.TypedDict, total=False):
    text: str
    items: list["EditorChildNode"]


class EditorChildNode(t.TypedDict):
    type: str
    data: EditorChildData


class EditorRootNode(t.TypedDict):
    time: int
    blocks: list[EditorChildNode]
    version: str
