import textwrap

from editorjs import EditorJS

EXAMPLE_MD = textwrap.dedent("""
    # Heading

    Paragraph with *special* content __yeah__ such as *[links](https://g.co)!*

    - list (unordered)
    - with
        - *nested* lvl 1.0
        - __nested__ lvl 1.1
            - nested lvl 2.0
    - [items](https://g.co)

    1. another
    2. list (ordered)
        1. with 
        2. nesting
    3. *and styling*

    ***

    Checkbox:
    - [ ] unchecked
    - [ ] *unchecked*
    - [x] checked
    - [x] *checked*

    Inline `code`

    ```python
    def real_code(example: str): 
        pass
    ```

    Image: ![Caption](https://py4web.leiden.dockers.local/img/upload/16.txt?hash=3f4b66f9be3306fa7f42c0bcf6238d1101d9c75f "Caption"); post image


    > The secret to creativity is knowing how to hide your sources.
    > Regel 2
    > <cite>Albert Einstein</cite>
    """)

EXAMPLE_JSON = r"""{"time":1730905327104,"blocks":[{"id":"1pY2hYfB1A","type":"header","data":{"text":"Heading","level":1}},{"id":"akvQa8k7ne","type":"paragraph","data":{"text":"Paragraph with special content yeah such as <a href=\"https://g.co\">links</a>!"}},{"id":"mtXTKYuP8k","type":"list","data":{"style":"unordered","items":[{"content":"list (unordered)","items":[]},{"content":"with","items":[{"content":"<i>nested</i> lvl 1.0","items":[]},{"content":"<b>nested</b> lvl 1.1","items":[{"content":"nested lvl 2.0","items":[]}]}]},{"content":"<a href=\"https://g.co\">items</a>","items":[]}]}},{"id":"CwdqcNPGp2","type":"list","data":{"style":"ordered","items":[{"content":"another","items":[]},{"content":"list (ordered)\n2.1. with\n2.2. nesting","items":[]},{"content":"<i>and styling</i>","items":[]}]}},{"id":"4aavopqblu","type":"delimiter","data":{}},{"id":"GgTUixlCYO","type":"paragraph","data":{"text":"Checkbox:"}},{"id":"E12TkYu5E_","type":"checklist","data":{"items":[{"text":"unchecked","checked":false},{"text":"<i>unchecked</i>","checked":false},{"text":"checked","checked":true},{"text":"<i>checked</i>","checked":true}]}},{"id":"I-HNbkhXE-","type":"paragraph","data":{"text":"Inline <code class=\"inline-code\">code</code>"}},{"id":"fNKmTrZvXn","type":"code","data":{"code":"def real_code(example: str): \n    pass"}},{"id":"bfHSwu6hjy","type":"paragraph","data":{"text":"Image: "}},{"id":"gClWIHSnxn","type":"image","data":{"caption":"Caption","withBorder":false,"withBackground":false,"stretched":false,"file":{"url":"https://py4web.leiden.dockers.local/img/upload/16.txt?hash=3f4b66f9be3306fa7f42c0bcf6238d1101d9c75f"}}},{"id":"NZ_ruz2mXL","type":"paragraph","data":{"text":"; post image"}},{"id":"Nn7p_3Whpy","type":"quote","data":{"text":"The secret to creativity is knowing how to hide your sources.<br>\nRegel 2<br>\n","caption":"Albert Einstein","alignment":"left"}}],"version":"2.30.6"}"""

def test_md():
    e = EditorJS.from_markdown(EXAMPLE_MD)

    print(e.to_mdast())
    print(e.to_markdown())
    print(e.to_json())
    print(e.to_html())


def test_json():
    e = EditorJS.from_json(EXAMPLE_JSON)

    print(e.to_mdast())
    print(e.to_json())
    print(e.to_markdown())
    print(e.to_html())

# def test_lossless():
#     e = EditorJS.from_markdown(EXAMPLE_MD)
#     assert e == EditorJS.from_mdast(e.to_mdast())
#     assert e == EditorJS.from_json(e.to_json())
#     assert e == EditorJS.from_markdown(e.to_markdown())
#
#     e = EditorJS.from_json(EXAMPLE_JSON)
#     assert e == EditorJS.from_mdast(e.to_mdast())
#     assert e == EditorJS.from_json(e.to_json())
#     assert e == EditorJS.from_markdown(e.to_markdown())