"""
mdast to editorjs
"""

import abc
import re
import typing as t
from html.parser import HTMLParser
from urllib.parse import urlparse

import humanize
import markdown2

from .exceptions import TODO, Unreachable
from .types import EditorChildData, MDChildNode


class EditorJSBlock(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def to_markdown(cls, data: EditorChildData) -> str: ...

    @classmethod
    @abc.abstractmethod
    def to_json(cls, node: MDChildNode) -> list[dict]: ...

    @classmethod
    @abc.abstractmethod
    def to_text(cls, node: MDChildNode) -> str: ...


BLOCKS: dict[str, EditorJSBlock] = {}


def block(*names: str):
    def wrapper(cls):
        for name in names:
            BLOCKS[name] = cls
        return cls

    return wrapper


def process_styled_content(item: MDChildNode, strict: bool = True) -> str:
    """
    Processes styled content (e.g., bold, italic) within a list item.

    Args:
        item: A ChildNode dictionary representing an inline element or text.
        strict: Raise if 'type' is not one defined in 'html_wrappers'

    Returns:
        A formatted HTML string based on the item type.
    """
    _type = item.get("type")
    html_wrappers = {
        "text": "{value}",
        "html": "{value}",
        "emphasis": "<i>{value}</i>",
        "strong": "<b>{value}</b>",
        "strongEmphasis": "<b><i>{value}</i></b>",
        "link": '<a href="{url}">{value}</a>',
        "inlineCode": '<code class="inline-code">{value}</code>',
    }

    if _type in BLOCKS:
        return BLOCKS[_type].to_text(item)

    if strict and _type not in html_wrappers:
        raise ValueError(f"Unsupported type {_type} in paragraph")

    # Process children recursively if they exist, otherwise use the direct value
    if children := item.get("children"):
        value = "".join(process_styled_content(child) for child in children)
    else:
        value = item.get("value", "")

    template = html_wrappers.get(_type, "{value}")
    return template.format(
        value=value, url=item.get("url", ""), caption=item.get("caption", "")
    )


def default_to_text(node: MDChildNode):
    return "".join(
        process_styled_content(child) for child in node.get("children", [])
    ) or process_styled_content(node)


@block("heading", "header")
class HeadingBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        level = data.get("level", 1)
        text = data.get("text", "")
        tunes = data.get("tunes", {})

        if not (1 <= level <= 6):
            raise ValueError("Header level must be between 1 and 6.")

        if (
            tunes.get("alignmentTune")
            and (alignment := tunes["alignmentTune"].get("alignment"))
            and (alignment != "left")
        ):
            # can't just return regular HTML because then it will turn into a raw block
            return AlignmentBlock.to_markdown(
                {
                    "text": text,
                    "tag": f"h{level}",
                    "alignment": alignment,
                }
            )

        return f"{'#' * level} {text}\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        """
        Converts a Markdown header block into structured block data.

        Args:
            node: A RootNode dictionary with 'depth' and 'children'.

        Returns:
            A ChildNode dictionary representing the header data, or None if no children exist.

        Raises:
            ValueError: If an unsupported heading depth is provided.
        """

        depth = node.get("depth")

        if depth is None or not (1 <= depth <= 6):
            raise ValueError("Heading depth must be between 1 and 6.")

        return [{"data": {"level": depth, "text": cls.to_text(node)}, "type": "header"}]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        children = node.get("children", [])
        if children is None or not len(children) == 1:
            raise ValueError("Header block must have exactly one child element")
        child = children[0]
        return child.get("value", "")


def paragraph_block(text: str):
    return {"type": "paragraph", "data": {"text": text}}


def raw_block(html: str):
    return {"type": "raw", "data": {"html": html}}


@block("paragraph")
class ParagraphBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        text = data.get("text", "")
        tunes = data.get("tunes", {})

        if (
            tunes.get("alignmentTune")
            and (alignment := tunes["alignmentTune"].get("alignment"))
            and (alignment != "left")
        ):
            return AlignmentBlock.to_markdown(
                {
                    "text": text,
                    "tag": "p",
                    "alignment": alignment,
                }
            )

        return f"{text}\n\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        result = []
        current_text = ""

        skip = 0
        nodes = node.get("children", [])
        any_html = False

        for idx, child in enumerate(nodes):
            if skip:
                skip -= 1
                continue

            _type = child.get("type")
            any_html |= _type == "html"

            # deal with custom types
            if _type == "html" and child.get("value", "").startswith("<editorjs"):
                # special type, e.g. <editorjs type="linkTool" href=...>...</editorjs>

                if child.get("value", "").endswith("/>"):
                    # self-closing
                    result.append(EditorJSCustom.to_json(node))
                else:
                    # <editorjs>something</editorjs> = 3 children
                    result.extend(
                        EditorJSCustom.to_json({"children": nodes[idx : idx + 2]})
                    )

                    skip = 2

                continue

            elif _type == "image":
                if current_text:
                    # {"id":"zksvpxQTDD","type":"raw","data":{"html":"<marquee> raw </marquee>"}}
                    result.append(
                        raw_block(current_text)
                        if any_html
                        else paragraph_block(current_text)
                    )
                    current_text = ""
                    any_html = False  # reset

                result.extend(ImageBlock.to_json(child))
            else:
                child_text = cls.to_text(child)
                _child_text = child_text.strip()
                if _child_text.startswith("|") and _child_text.endswith("|"):
                    # note: this just supports text-only tables.
                    # tables with more complex elements break into multiple children.
                    # and mdast DOES support converting into a Table/TableCell structure
                    # via the GFM exttension
                    # but their default mdast->md converter does NOT implement these functionalities.
                    result.extend(TableBlock.to_json(child))
                    continue

                current_text += child_text

        # final text after image:
        if current_text:
            result.append(
                raw_block(current_text) if any_html else paragraph_block(current_text)
            )

        return result

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        return default_to_text(node)


@block("list")
class ListBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        style = data.get("style", "unordered")
        items = data.get("items", [])

        def parse_items(subitems: list[dict[str, t.Any]], depth: int = 0) -> str:
            markdown_items = []
            for index, item in enumerate(subitems):
                prefix = f"{index + 1}." if style == "ordered" else "-"
                line = f"{'\t' * depth}{prefix} {item['content']}"
                markdown_items.append(line)

                # Recurse if there are nested items
                if item.get("items"):
                    markdown_items.append(parse_items(item["items"], depth + 1))

            return "\n".join(markdown_items)

        return "\n" + parse_items(items) + "\n\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        """
        Converts a Markdown list block with nested items and styling into structured block data.

        Args:
            node: A RootNode dictionary with 'ordered' and 'children'.

        Returns:
            A dictionary representing the structured list data with 'items' and 'style'.
        """
        items = []
        # checklists are not supported (well) by mdast
        # so we detect it ourselves:
        could_be_checklist = True

        def is_checklist(value: str) -> bool:
            return value.strip().startswith(("[ ]", "[x]"))

        for child in node["children"]:
            content = ""
            subitems = []
            # child can have content and/or items
            for grandchild in child["children"]:
                _type = grandchild.get("type", "")
                if _type == "paragraph":
                    subcontent = ParagraphBlock.to_text(grandchild)
                    could_be_checklist = could_be_checklist and is_checklist(subcontent)
                    content += "" + subcontent
                elif _type == "list":
                    could_be_checklist = False
                    subitems.extend(ListBlock.to_json(grandchild)[0]["data"]["items"])
                else:
                    raise ValueError(f"Unsupported type {_type} in list")

            items.append(
                {
                    "content": content,
                    "items": subitems,
                }
            )

        if could_be_checklist:
            return [
                {
                    "type": "checklist",
                    "data": {
                        "items": [
                            {
                                "text": x["content"]
                                .removeprefix("[ ] ")
                                .removeprefix("[x] "),
                                "checked": x["content"].startswith("[x]"),
                            }
                            for x in items
                        ]
                    },
                }
            ]
        else:
            return [
                {
                    "data": {
                        "items": items,
                        "style": "ordered" if node.get("ordered") else "unordered",
                    },
                    "type": "list",
                }
            ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        return ""


@block("checklist")
class ChecklistBlock(ListBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        markdown_items = []

        for item in data.get("items", []):
            text = item.get("text", "").strip()
            char = "x" if item.get("checked", False) else " "
            markdown_items.append(f"- [{char}] {text}")

        return "\n" + "\n".join(markdown_items) + "\n\n"


@block("thematicBreak", "delimiter")
class DelimiterBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        return "***\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        return [
            {
                "type": "delimiter",
                "data": {},
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        return ""


@block("code")
class CodeBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        code = data.get("code", "")
        return f"```\n" f"{code}" f"\n```\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        return [
            {
                "data": {"code": cls.to_text(node)},
                "type": "code",
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        return node.get("value", "")


@block("image")
class ImageBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        url = data.get("url", "") or data.get("file", {}).get("url", "")
        caption = data.get("caption", "")

        with_border = "1" if data.get("withBorder") else ""
        with_background = "1" if data.get("withBackground") else ""
        stretched = "1" if data.get("stretched") else ""

        if any((with_border, with_background, stretched)):
            # custom type to support custom options:
            return f"""<editorjs type="image" caption="{caption}" border="{with_border}" background="{with_background}" stretched="{stretched}" url="{url}" />\n\n"""
        else:
            return f"""![{caption}]({url} "{caption}")\n\n"""

    @classmethod
    def _caption(cls, node: MDChildNode):
        return node.get("alt") or node.get("caption") or ""

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        return [
            {
                "type": "image",
                "data": {
                    "file": {"url": node.get("url")},
                    "caption": cls._caption(node),
                    "withBorder": bool(node.get("border", False)),
                    "stretched": bool(node.get("stretched", False)),
                    "withBackground": bool(node.get("background", False)),
                },
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        caption = cls._caption(node)
        url = node.get("url")

        background = node.get("background") or ""
        stretched = node.get("stretched") or ""
        border = node.get("border") or ""

        return f"""
        <div class="ce-block {stretched and 'ce-block--stretched'}">
            <div class="ce-block__content">
            <div class="cdx-block image-tool image-tool--filled {background and 'image-tool--withBackground'} {stretched and 'image-tool--stretched'} {border and 'image-tool--withBorder'}">
                <div class="image-tool__image">
                    <img class="image-tool__image-picture" src="{url}" title="{caption}" alt="{caption}">
                </div>
            </div>
        </div>
        """


@block("blockquote", "quote")
class QuoteBlock(EditorJSBlock):
    re_cite = re.compile(r"<cite>(.+?)<\/cite>")

    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        text = data.get("text", "")
        result = f"> {text}\n"
        if caption := data.get("caption", ""):
            result += f"> <cite>{caption}</cite>\n"
        return result

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        caption = ""
        text = cls.to_text(node).replace("\n", "<br/>\n")

        if cite := re.search(cls.re_cite, text):
            # Capture the value of the first group
            caption = cite.group(1)
            # Remove the <cite>...</cite> tags from the text
            text = re.sub(cls.re_cite, "", text)

        return [
            {
                "data": {
                    "alignment": "left",
                    "caption": caption,
                    "text": text,
                },
                "type": "quote",
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        return default_to_text(node)


@block("raw", "html")
class RawBlock(EditorJSBlock):

    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        text = data.get("html", "")
        return f"{text}\n\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        raw = cls.to_text(node)

        if raw.startswith("<editorjs"):
            # not a raw block but (probably) a self-closing editorjs block
            return EditorJSCustom.to_json({"children": [node]})
        else:
            return [raw_block(raw)]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        return node.get("value", "")


@block("table")
class TableBlock(EditorJSBlock):

    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        """
        | Script | Interpreter | User | System |   |
        |--------|-------------|------|--------|---|
        |        |             |      |        |   |
        |        |             |      |        |   |
        |        |             |      |        |   |
        """

        table = ""
        rows = data.get("content", [])

        # Add an empty header row if no headings are provided
        if not data.get("withHeadings", False) and rows:
            table += "| " + " | ".join([""] * len(rows[0])) + " |\n"
            table += "|" + " - |" * len(rows[0]) + "\n"

        # Populate rows
        for idx, tr in enumerate(rows):
            table += "| " + " | ".join(tr) + " |\n"

            # Add separator if headings are enabled and it's the first row
            if not idx and data.get("withHeadings", False):
                table += "|" + " - |" * len(tr) + "\n"

        return f"\n{table}\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        # content":[["Yeah","Okay"],["<i>1</i>","<code class=\"inline-code\">2</code>"]]}}]
        table = []
        with_headings = False

        # first row is headings or empty. If not empty, withHeadings is True
        # second row must be ignored
        for idx, row in enumerate(node.get("value", "").strip().split("\n")):
            tr = [_.strip() for _ in row.split("|")[1:-1]]
            if not idx:
                # first
                if any(tr):
                    with_headings = True
                    table.append(tr)

            elif idx == 1:
                continue
            else:
                table.append(tr)

        return [
            {
                "type": "table",
                "data": {
                    "content": table,
                    "withHeadings": with_headings,
                },
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        # I think this might be triggered if there is a table (deeply) within a paragraph block?
        raise TODO(["TableBlock.to_text", node])


@block("linkTool")
class LinkBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        link = data.get("link", "")
        meta = data.get("meta", {})
        title = meta.get("title", "")
        description = meta.get("description", "")
        image = meta.get("image", {}).get("url", "")
        return f"""<editorjs type="linkTool" href="{link}" title="{title}" image="{image}">{description}</editorjs>\n\n"""

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        return [
            {
                "type": "linkTool",
                "data": {
                    "link": node.get("href", ""),
                    "meta": {
                        "title": node.get("title", ""),
                        "description": node.get("body", ""),
                        "image": {
                            "url": node.get("image", ""),
                        },
                    },
                },
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        url = node.get("href", "")
        image = node.get("image", "")
        title = node.get("title", "")
        body = node.get("body", "")
        domain = urlparse(url).netloc

        return f"""
        <div class="link-tool">
            <a class="link-tool__content link-tool__content--rendered" target="_blank"
               rel="nofollow noindex noreferrer" href="{url}">
                <div class="link-tool__image"
                     style="background-image: url(&quot;{image}&quot;);"></div>
                <div class="link-tool__title">{title}</div>
                <p class="link-tool__description">{body}</p>
                <span class="link-tool__anchor">{domain}</span>
            </a>
        </div>
        """


@block("attaches")
class AttachmentBlock(EditorJSBlock):

    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        title = data.get("title", "")
        file = data.get("file", {})
        url = file.get("url", "")
        name = file.get("name", "")
        extension = file.get("extension", "")
        size = file.get("size", "")

        return f"""<editorjs type="attaches" file="{url}" name="{name}" extension="{extension}" size="{size}">{title}</editorjs>\n\n"""

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        return [
            {
                "type": "attaches",
                "data": {
                    "file": {
                        "url": node.get("file", ""),
                        "name": node.get("name", ""),
                        "extension": node.get("extension", ""),
                        "size": node.get("size", ""),
                    },
                    "title": node.get("body", ""),
                },
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        # {'type': 'attaches', 'file': 'https://py4web.leiden.dockers.local/img/upload/8.deb?hash=778760cf05483147b2ff0fa0ddeab2b22d9343e8', 'name': 'gemistdownloadermd5-08d0e3cdb4f7e81986bdd0c60294dec03.0.0.5-1.deb', 'extension': 'deb', 'size': '1613660', 'body': 'gemistdownloader...

        extension = node.get("extension", "")

        file_icon = (
            f"""
            <div class="cdx-attaches__file-icon-background"></div>
            <div class="cdx-attaches__file-icon-label" title="{extension}">{extension}</div>
            """
            if extension
            else """
            <div class="cdx-attaches__file-icon-background">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.3236 8.43554L9.49533 12.1908C9.13119 12.5505 8.93118 13.043 8.9393 13.5598C8.94741 14.0767 9.163 14.5757 9.53862 14.947C9.91424 15.3182 10.4191 15.5314 10.9422 15.5397C11.4653 15.5479 11.9637 15.3504 12.3279 14.9908L16.1562 11.2355C16.8845 10.5161 17.2845 9.53123 17.2682 8.4975C17.252 7.46376 16.8208 6.46583 16.0696 5.72324C15.3184 4.98066 14.3086 4.55425 13.2624 4.53782C12.2162 4.52138 11.2193 4.91627 10.4911 5.63562L6.66277 9.39093C5.57035 10.4699 4.97032 11.9473 4.99467 13.4979C5.01903 15.0485 5.66578 16.5454 6.79264 17.6592C7.9195 18.7731 9.43417 19.4127 11.0034 19.4374C12.5727 19.462 14.068 18.8697 15.1604 17.7907L18.9887 14.0354"></path></svg>
            </div>
            """
        )

        file_size = (
            f"""<div class="cdx-attaches__size">{humanize.naturalsize(int(size))}</div>"""
            if (size := node.get("size", ""))
            else ""
        )

        return f"""
        <div class="cdx-attaches cdx-attaches--with-file">
            <div class="cdx-attaches__file-icon">
                {file_icon}
            </div>
            <div class="cdx-attaches__file-info">
                <div class="cdx-attaches__title" data-placeholder="File title" data-empty="false">
                    {node.get("body", "")}
                </div>
                {file_size}
            </div>
            <a class="cdx-attaches__download-button" href="{node.get('file', '')}" target="_blank" rel="nofollow noindex noreferrer" title="{node.get('name', '')}">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M7 10L11.8586 14.8586C11.9367 14.9367 12.0633 14.9367 12.1414 14.8586L17 10"></path></svg>
            </a>
        </div>
        """


@block("alignment")
class AlignmentBlock(EditorJSBlock):
    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        tag = data["tag"]
        alignment = data["alignment"]
        content = data["text"]

        return f"<editorjs type='alignment' tag='{tag}' alignment='{alignment}'>{content}</editorjs>\n\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        # only paragraph and headers can be aligned
        tag: str = node["tag"]
        text: str = node["body"]
        alignment = node["alignment"]
        data = {"text": text}

        if tag == "p":
            _type = "paragraph"
        elif tag.startswith("h"):
            _type = "header"
            data["level"] = int(tag.removeprefix("h"))
        else:
            # doesn't support alignment
            raise NotImplementedError(f"Unsupported tag for alignment: {tag}")

        return [
            {
                "type": _type,
                "data": data,
                "tunes": {"alignmentTune": {"alignment": alignment}},
            }
        ]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        tag = node["tag"]
        body = node["body"]
        alignment = node["alignment"]
        return f"<{tag} style='text-align: {alignment}'>{body}</{tag}>"


@block("embed")
class EmbedBlock(EditorJSBlock):

    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        service = data.get("service", "")
        source = data.get("source", "")
        embed = data.get("embed", "")
        caption = data.get("caption", "")

        return f"<editorjs type='embed' service='{service}' source='{source}' embed='{embed}' caption='{caption}'/>\n\n"

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        return [{"type": "embed", "data": node}]

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        source = node.get("source", "")
        embed = node.get("embed", "")
        caption = node.get("caption", "")
        return f"""
        <div class="cdx-block embed-tool">
            <iframe title='{caption}' style="width:100%;" height="320" frameborder="0" allowfullscreen="" src="{embed}" class="embed-tool__content"></iframe>
        </div>
        """


### end blocks


class AttributeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = {}
        self.data = None

    def handle_starttag(self, tag, attrs):
        # Collect attributes when the tag is encountered
        self.attributes = dict(attrs)

    def handle_data(self, data):
        self.data = data


class EditorJSCustom(EditorJSBlock, markdown2.Extra):
    """
    Special type of block to deal with custom attributes.

    This is both a special editorjs block as well as a markdown2 plugin!
    """

    name = "editorjs"
    order = (), (markdown2.Stage.POSTPROCESS,)

    @classmethod
    def parse_html(cls, html: str):
        parser = AttributeParser()
        parser.feed(html)

        return parser.attributes, parser.data

    @classmethod
    def to_markdown(cls, data: EditorChildData) -> str:
        raise Unreachable("Custom Blocks have their own to_markdown logic.")

    @classmethod
    def _find_right_block(cls, html: str) -> tuple[EditorJSBlock, dict]:
        attrs, body = cls.parse_html(html)
        _type = attrs.get("type", "")
        attrs.setdefault("body", body)  # only if there is no such attribute yet

        handler = BLOCKS.get(_type)

        if not handler:
            raise ValueError(f"Unknown custom type {_type}")

        return handler, attrs

    @classmethod
    def to_json(cls, node: MDChildNode) -> list[dict]:
        html = "".join(_["value"] for _ in node.get("children", []))
        handler, attrs = cls._find_right_block(html)
        return handler.to_json(attrs)

    @classmethod
    def to_text(cls, node: MDChildNode) -> str:
        handler, attrs = cls._find_right_block(node.get("value", ""))
        return handler.to_text(attrs)

    # markdown2:
    re_short = re.compile(r"<editorjs.*?/>")
    re_long = re.compile(r"<editorjs.*?>.*?</editorjs>")

    def run(self, text: str) -> str:
        def replace_html(match):
            handler, attrs = self._find_right_block(match.group())
            return handler.to_text(attrs)

        # Substitute using the replacement functions
        text = self.re_long.sub(replace_html, text)
        text = self.re_short.sub(replace_html, text)

        return text


EditorJSCustom.register()
