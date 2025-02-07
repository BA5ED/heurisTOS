from enum import Enum

import attr


class InputType(Enum):
    Text = "text"
    HTML = "html"


@attr.s()
class ParsedSection:
    name: str = attr.ib()
    content: str = attr.ib()
    subsections: list = attr.ib(factory=list)


@attr.s()
class ParsedPolicy:
    title: str = attr.ib()
    sections: list = attr.ib(factory=list)


# class PolicyParser:
#
#     def __init__(self, content: str, input_type: InputType):
#         self._content = content
#         self._input_type = input_type
#
#     def dictionary(self):
#         ...
