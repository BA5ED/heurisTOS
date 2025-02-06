

import attr
from bs4 import BeautifulSoup

from heuristos.parser.shared import ParsedPolicy


@attr.s()
class HTMLPolicyParser:
    content: str = attr.ib()
    _root_node: BeautifulSoup

    def __attrs_post_init__(self):
        self._root_node = BeautifulSoup(self.content, 'html.parser')

    def stdrep(self) -> ParsedPolicy | None:
        ...

    def _LCA(self, nodes: list[BeautifulSoup]) -> BeautifulSoup:
        # derive lineage of each input and then find the
        # lowest node that is shared among them.
        ancestries = []
        for node in nodes:
            ancestry = []
            parent = node.parent
            while parent:
                ancestry.append(node.parent)
                parent = node.parent

            ancestries.append(ancestry)




        pass

