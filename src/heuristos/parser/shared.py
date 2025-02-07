from enum import Enum
from typing import Union

import attr


class InputType(Enum):
    Text = "text"
    HTML = "html"


SubNodeUnion = Union["TextNode", "ParsedSection"]


@attr.s()
class TextNode:
    text: str = attr.ib()

    def __dict__(self):
        return {"content": self.text, "type": "text"}


@attr.s()
class ParsedSection:
    name: str = attr.ib()
    content: list[SubNodeUnion] = attr.ib(factory=list)

    def __dict__(self):
        return {
            "name": self.name,
            "content": [dict(c) for c in self.content],
            "type": "section",
        }


# ParsedPolicy is not structurally different from ParsedSection, but it is semantically.
@attr.s()
class ParsedPolicy:
    title: str = attr.ib()
    content: list[SubNodeUnion] = attr.ib(factory=list)

    def __dict__(self):
        return {
            "title": self.title,
            "content": [dict(c) for c in self.content],
            "type": "policy",
        }
