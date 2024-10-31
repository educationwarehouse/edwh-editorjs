# edwh-editorjs

A minimal, fast Python 3.10+ package for parsing [Editor.js](https://editorjs.io) content.
This package is a fork of [pyEditorJS by SKevo](https://github.com/SKevo18/pyEditorJS) with additional capabilities.

## New Features

- Expanded support for additional block types: Quote, Table, Code, Warning, and Raw blocks
- Issues a warning if an unknown block type is encountered, rather than ignoring it
- Adds a `strict` mode, raising an `EditorJSUnsupportedBlock` exception for unknown block types when `strict=True`
- Allows adding new blocks by decorating a subclass of `EditorJsParser` with `@block("name")`

## Installation

```bash
pip install edwh-editorjs
```

## Usage

### Quickstart

```python
from pyeditorjs import EditorJsParser

editor_js_data = ...  # your Editor.js JSON data
parser = EditorJsParser(editor_js_data)  # initialize the parser

html = parser.html(sanitize=True)  # `sanitize=True` uses the included `bleach` dependency
print(html)  # your clean HTML
```

### Enforcing Strict Block Types

```python
from pyeditorjs import EditorJsParser, EditorJSUnsupportedBlock

editor_js_data: dict = ...
parser = EditorJsParser(editor_js_data)

try:
    html = parser.html(strict=True)
except EditorJSUnsupportedBlock as e:
    print(f"Unsupported block type encountered: {e}")
```

### Adding a Custom Block

To add a custom block type, create a new class that subclasses `EditorJsBlock` and decorates it with `@block("name")`,
where `"name"` is the custom block type. Implement an `html` method to define how the block’s content should be
rendered. This method should accept a `sanitize` parameter and can access block data via `self.data`.

```python
from pyeditorjs import EditorJsParser, EditorJsBlock, block

@block("custom")
class CustomBlock(EditorJsBlock):
    def html(self, sanitize: bool = False) -> str:
        # Access data with self.data and return the rendered HTML
        content = self.data.get("something", "")
        if sanitize:
            content = self.sanitize(content)
        
        return f"<div class='custom-block'>{content}</div>"

# Usage
class CustomEditorJsParser(EditorJsParser):
    pass  # Custom blocks are automatically detected

editor_js_data = ...  # Editor.js JSON data with a "customBlock" type
parser = CustomEditorJsParser(editor_js_data)
html = parser.html()
print(html)  # Includes rendered custom blocks
```

## Disclaimer

This is a community-provided project and is not affiliated with the Editor.js team. 
Contributions, bug reports, and suggestions are welcome!