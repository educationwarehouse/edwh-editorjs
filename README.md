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
from edwh_editorjs import EditorJsParser

editor_js_data = ...  # your Editor.js JSON data
parser = EditorJsParser(editor_js_data)  # initialize the parser

html = parser.html(sanitize=True)  # `sanitize=True` uses the included `bleach` dependency
print(html)  # your clean HTML
```

### Enforcing Strict Block Types

```python
from edwh_editorjs import EditorJsParser, EditorJSUnsupportedBlock

try:
    parser = EditorJsParser(editor_js_data, strict=True)
    html = parser.html()
except EditorJSUnsupportedBlock as e:
    print(f"Unsupported block type encountered: {e}")
```

## Disclaimer

This is a community-provided project and is not affiliated with the Editor.js team. 
Contributions, bug reports, and suggestions are welcome!