# Changelog

<!--next-version-placeholder-->

## v2.4.0 (2024-12-02)

### Feature

* **image:** Support more options for the image block ([`c74dcce`](https://github.com/educationwarehouse/edwh-editorjs/commit/c74dccef5c1115038f6de0f08250dfa6cff18796))

### Fix

* Less exceptions, more warnings for better ease-of-use ([`891fca1`](https://github.com/educationwarehouse/edwh-editorjs/commit/891fca198e774c53a8b6365b927a080f61c0b2c8))

## v2.3.2 (2024-11-27)

### Fix

* (refactor) clean up todo's, add `Unreachable` for when some branch/function should never be used ([`3226642`](https://github.com/educationwarehouse/edwh-editorjs/commit/3226642cfc8adb9a3cad6052d02ea6fc6c048058))

## v2.3.1 (2024-11-27)

### Fix

* **embed:** Simplify embed to just the iframe without most editorjs boilerplate ([`4cfa4e6`](https://github.com/educationwarehouse/edwh-editorjs/commit/4cfa4e6c05fc0d3d39f50b2ccb60c41d42c1b506))

## v2.3.0 (2024-11-27)

### Feature

* **attachment:** Support more optional fields such as extension, size ([`212cf7e`](https://github.com/educationwarehouse/edwh-editorjs/commit/212cf7e871f3b9b5137234fea050e24b268229f5))
* Support `embed` block ([`99f0ffe`](https://github.com/educationwarehouse/edwh-editorjs/commit/99f0ffe257efb11eab76f266cf86e72c2f9df2eb))

## v2.2.2 (2024-11-26)

### Fix

* Support 'html' as alias for 'raw' block ([`4627f90`](https://github.com/educationwarehouse/edwh-editorjs/commit/4627f900a30bf6d6b202790958a78d4ef745ee11))

## v2.2.1 (2024-11-26)

### Fix

* Quick fix to prevent unlimited spaces being added by mdast ([`a196a22`](https://github.com/educationwarehouse/edwh-editorjs/commit/a196a221b623f7d4808aec64ef455197bdcfacaf))

## v2.2.0 (2024-11-26)

### Feature

* Support the alignment tune plugin ([`652cb58`](https://github.com/educationwarehouse/edwh-editorjs/commit/652cb58920b35fbb36c56d665e52e69a40811258))

## v2.1.1 (2024-11-26)

### Fix

* More newlines for better block separation ([`11574df`](https://github.com/educationwarehouse/edwh-editorjs/commit/11574df641ed9c7b4da11a0ee8c102b737c3cf66))

## v2.1.0 (2024-11-26)

### Feature

* `EditorJS.from_json` now also accepts a (json) list of blocks instead of the full object (dictionary with time, version, blocks) ([`9f24c15`](https://github.com/educationwarehouse/edwh-editorjs/commit/9f24c15983948db96153901e804b9a2b11029f49))

### Fix

* Better separation between raw and paragraph blocks ([`f7620cf`](https://github.com/educationwarehouse/edwh-editorjs/commit/f7620cf6f34a0a9b9a218fb1c78a67a04f15b78e))

## v2.0.2 (2024-11-26)

### Fix

* Raw block pt2 ([`37ee6bc`](https://github.com/educationwarehouse/edwh-editorjs/commit/37ee6bc09dd8f54ca22f2652be1c5920d74779d1))

## v2.0.1 (2024-11-26)

### Fix

* Table block, raw html block ([`849aeee`](https://github.com/educationwarehouse/edwh-editorjs/commit/849aeee9fcafd51cb71416edeb127820ee3fc89f))

## v2.0.0 (2024-11-18)

### Features

* Rebuilt the editor logic based on MDAST for improved extensibility and maintainability ([`28c12f1`](https://github.com/educationwarehouse/edwh-editorjs/commit/28c12f1f74c71a995f9f8097f1b26be45f835ad4))
* Added support for (basic) tables and custom Editor.js blocks, such as `linkTool` and `<editorjs>` ([`a6dfadf`](https://github.com/educationwarehouse/edwh-editorjs/commit/a6dfadf21ec008fe714704a056b9ffec751d731c))
* Integrated `markdown2` extras to handle custom `<editorjs>` blocks ([`31d8647`](https://github.com/educationwarehouse/edwh-editorjs/commit/31d8647b7275e245dabf27a99c43d400217705be))

### Fixes

* Corrected behavior for nested lists ([`52a7773`](https://github.com/educationwarehouse/edwh-editorjs/commit/52a7773470dce3eee6a2d17d46b594551ed043a5))
* Resolved an issue where rendered attachments were incorrectly marked as content-editable ([`58ab562`](https://github.com/educationwarehouse/edwh-editorjs/commit/58ab562daaca233455b3fe66b773af61f1abb0ad))


## v1.1.0 (2024-10-31)

### Feature

* Expose _sanitize via EditorJSBlock.sanitize for external usage ([`7daa67c`](https://github.com/educationwarehouse/edwh-editorjs/commit/7daa67c90440510c83b573c22edf377cc2fd801f))

### Documentation

* Added section on defining new custom blocks ([`51d7720`](https://github.com/educationwarehouse/edwh-editorjs/commit/51d77208d4f8156e895de914f41bdeb882a508c0))

## v1.0.1 (2024-10-31)

### Documentation

* Updated README ([`18d0216`](https://github.com/educationwarehouse/edwh-editorjs/commit/18d021629bcb223b89a9731e9ad8c574248f75c7))

## v1.0.0 (2024-10-31)

### Feature

* Implemented more blocks (raw, warning, code, table, quote) ([`fb93bd9`](https://github.com/educationwarehouse/edwh-editorjs/commit/fb93bd959f06fa86bc23c9bfc51a8b7fddfc65f2))
* Refactor to Registry Pattern so new block can be easily added ([`b06c86d`](https://github.com/educationwarehouse/edwh-editorjs/commit/b06c86da623dd2a2d92f7c48353a1f3208fb5749))
