import attr
from bs4 import BeautifulSoup

from heuristos.parser.shared import ParsedPolicy


@attr.s()
class HTMLPolicyParser:
    content: str = attr.ib()
    _root_node: BeautifulSoup

    def __attrs_post_init__(self):
        self._root_node = BeautifulSoup(self.content, "html.parser")

    def stdrep(self) -> ParsedPolicy | None: ...

    def _LCA(self, nodes: list[BeautifulSoup]) -> BeautifulSoup | None:

        if not nodes:
            return None

        # derive lineage of each input and then find the
        # lowest node that is shared among them.
        ancestries = []
        for node in nodes:
            ancestry = []
            parent = node.parent
            while parent:
                ancestry.append(parent)
                parent = node.parent

            ancestries.append(ancestry)

        common_ancestors = set(ancestries[0])

        for ancestry in ancestries[1:]:
            common_ancestors &= set(ancestry)

        # iterate in depth order
        for node in ancestries[0]:
            if node in common_ancestors:
                return node

        return None


