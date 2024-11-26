import json
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

LINKTOOL_JSON = r"""{"time":1730911265307,"blocks":[{"id":"A07WMZn2iv","type":"linkTool","data":{"link":"https://fb.me","meta":{"title":"","description":"Meld je aan bij Facebook om te delen en contact te maken met je vrienden, familie en mensen die je kent.","image":{"url":"https://www.facebook.com/images/fb_icon_325x325.png"}}}}],"version":"2.30.6"}"""


def test_linktool():
    e = EditorJS.from_json(LINKTOOL_JSON)
    print(e.to_html())
    print(e.to_json())
    print(e.to_markdown())
    print(e.to_html())


TABLE1_JSON = r"""{"time":1730984047714,"blocks":[{"id":"SNXL5vru_a","type":"table","data":{"withHeadings":false,"stretched":false,"content":[["1.1","2.1"],["1.2","2.2"]]}},{"id":"q0IC_sL8P5","type":"paragraph","data":{"text":"<mark class=\"cdx-marker\">marked</mark>"}}],"version":"2.30.6"}"""
TABLE2_JSON = r"""{"time":1730984305796,"blocks":[{"id":"vBf5hT3jeR","type":"linkTool","data":{"link":"https://fb.me","meta":{"title":"","description":"Meld je aan bij Facebook om te delen en contact te maken met je vrienden, familie en mensen die je kent.","image":{"url":"https://www.facebook.com/images/fb_icon_325x325.png"}}}},{"id":"7bP-0bw1OT","type":"table","data":{"withHeadings":true,"stretched":false,"content":[["Yeah","Okay"],["<i>1</i>","<code class=\"inline-code\">2</code>"]]}}],"version":"2.30.6"}"""


def test_table():
    e = EditorJS.from_json(TABLE1_JSON)
    print(e.to_markdown())
    print(e.to_json())
    print(e.to_html())

    e = EditorJS.from_json(TABLE2_JSON)
    print(e.to_markdown())
    print(e.to_json())
    print(e.to_html())


ATTACHMENT_JSON = r"""{"time":1730989152705,"blocks":[{"id":"s3k3WCp1da","type":"header","data":{"text":"Hi","level":2}},{"id":"EehvyuBEKx","type":"paragraph","data":{"text":"<b>Paragraph</b> <i>met</i> <a href=\"http://g.co\">mooie</a> <code class=\"inline-code\">markup </code><mark class=\"cdx-marker\">asdf</mark>"}},{"id":"S1ENjQ6XEw","type":"list","data":{"style":"unordered","items":[{"content":"u","items":[]},{"content":"l","items":[]}]}},{"id":"ezy6f8-7gj","type":"list","data":{"style":"ordered","items":[{"content":"o","items":[]},{"content":"l","items":[]}]}},{"id":"DsHJI0tccS","type":"image","data":{"caption":"streamers","withBorder":false,"withBackground":false,"stretched":false,"file":{"url":"https://py4web.leiden.dockers.local/img/upload/17.txt?hash=3ef2d77e2f4f493651119f65d1657b01de939adb"}}},{"id":"VhvLUtaKcB","type":"quote","data":{"text":"ik ben een streamer","caption":"Frank Lammers","alignment":"left"}},{"id":"yrQLgdrYWC","type":"delimiter","data":{}},{"id":"88cMVCXNZF","type":"table","data":{"withHeadings":true,"stretched":false,"content":[["Tafels","Deuren"],["1 * 1","1"],["2 * 2","4"]]}},{"id":"vlSOey3tKF","type":"code","data":{"code":"if crash: don't"}},{"id":"zPzINXsico","type":"raw","data":{"html":"<marquee>Wheeeee</marquee>"}},{"id":"rbc6buobti","type":"checklist","data":{"items":[{"text":"check","checked":false},{"text":"one","checked":true},{"text":"two","checked":false}]}},{"id":"0JGAjTs_77","type":"linkTool","data":{"link":"https://trialandsuccess.nl","meta":{"title":"Trial and Success","description":"Welkom op de website van Trial and Success! Ik, Robin van der Noord, ontwerp en bouw websites en webapplicaties, helemaal toegespitst op de wensen van de klant. Ook kan ik de hosting en het onderhoud van uw website verzorgen.","image":{"url":"https://trialandsuccess.nl/static/images/og.png"}}}},{"id":"h8Zt0aKD5p","type":"attaches","data":{"file":{"url":"https://py4web.leiden.dockers.local/img/upload/18.txt?hash=f114bad0e27c84eb1f70ba2d6168d2a76b9efca9"},"title":"Attachment, Download nu!"}}],"version":"2.30.6"}"""


def test_attachment():
    e = EditorJS.from_json(ATTACHMENT_JSON)
    print(e.to_markdown())
    print(e.to_json())
    print(e.to_html())


def test_raw_html():
    # e = EditorJS.from_markdown(textwrap.dedent("""
    # # Raw  HTML
    #
    # <marquee>This ain't no paragraph</marquee>
    #
    # This is a paragraph
    # """))
    #
    # blocks = json.loads(e.to_json())
    #
    # print(blocks)
    #
    # assert blocks["blocks"][1]["type"] == "raw", blocks["blocks"][1]["type"]
    # assert blocks["blocks"][2]["type"] == "paragraph", blocks["blocks"][2]["type"]
    #

    raw_html_json = r"""{"time":1730989152705,"blocks":[{"id":"DGQwRibbof","type":"paragraph","data":{"text":"The Start"}},{"id":"NrvWoJ2bVI","type":"raw","data":{"html":" <marquee>    <kaas>mannetje    </kaas>    </marquee>Einde!"}},{"id":"DGQwRibbof","type":"paragraph","data":{"text":"The End!"}}],"version":"2.30.6"}"""

    e = EditorJS.from_json(raw_html_json)
    blocks = json.loads(e.to_json())

    print(blocks)

    assert blocks["blocks"][0]["type"] == "paragraph", blocks["blocks"][0]["type"]
    assert blocks["blocks"][1]["type"] == "raw", blocks["blocks"][1]["type"]
    assert blocks["blocks"][2]["type"] == "paragraph", blocks["blocks"][2]["type"]


def test_code():
    e = EditorJS.from_markdown(textwrap.dedent("""
    Read code:
    
    ```
    <marquee> code </marquee>
    ```
    
    End of code
    """))

    blocks = json.loads(e.to_json())

    assert blocks["blocks"][0]["type"] == "paragraph", blocks["blocks"][0]["type"]
    assert blocks["blocks"][1]["type"] == "code", blocks["blocks"][1]["type"]
    assert blocks["blocks"][2]["type"] == "paragraph", blocks["blocks"][2]["type"]

    # check if it's still the same after export and import:

    e = EditorJS.from_json(blocks)

    blocks = json.loads(e.to_json())

    assert blocks["blocks"][0]["type"] == "paragraph", blocks["blocks"][0]["type"]
    assert blocks["blocks"][1]["type"] == "code", blocks["blocks"][1]["type"]
    assert blocks["blocks"][2]["type"] == "paragraph", blocks["blocks"][2]["type"]

    # note: without `time` and `version` boilerplate:
    blocks_json = r"""[{"id":"DD966BQf_t","type":"paragraph","data":{"text":"Pre"}},{"id":"sjr2JyuC1y","type":"code","data":{"code":"html"}},{"id":"aJN_wgBv7b","type":"paragraph","data":{"text":"Post"}}]"""

    e = EditorJS.from_json(blocks_json)

    blocks = json.loads(e.to_json())

    assert blocks["blocks"][0]["type"] == "paragraph", blocks["blocks"][0]["type"]
    assert blocks["blocks"][1]["type"] == "code", blocks["blocks"][1]["type"]
    assert blocks["blocks"][2]["type"] == "paragraph", blocks["blocks"][2]["type"]
