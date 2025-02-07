import attr
from bs4 import BeautifulSoup, Tag

from heuristos.parser.shared import ParsedPolicy, ParsedSection


_TEXT_NODES = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'span']


def _find_headers(node: Tag):
    header_nodes = node.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    return header_nodes


def _node_histogram(nodes: list[Tag]) -> dict:
    histogram = {}
    for node in nodes:
        histogram[node.name] = histogram.get(node.name, 0) + 1
    return histogram


@attr.s()
class HTMLPolicyParser:
    content: str = attr.ib()
    _root_node: BeautifulSoup

    def __attrs_post_init__(self):
        self._root_node = BeautifulSoup(self.content, "html.parser")

    def stdrep(self) -> ParsedPolicy | None:
        # heuristically, I think long text nodes are going to be our best starting point.
        large_text_nodes = self._find_long_text_nodes()
        if not large_text_nodes:
            return None

        lca = self._LCA(large_text_nodes)
        if lca is None:
            return None

        headers = _find_headers(lca)
        hhist = _node_histogram(headers)
        ranked = sorted(hhist.items(), key=lambda x: x[1], reverse=True)

        likely_title = ranked[0][0]
        likely_section = ranked[::-1][0][0]

    def _derive_sections(self): ...

    def _LCA(self, nodes: list[Tag]) -> Tag | None:
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

        # iterate in depth order to determine lowest node
        for node in ancestries[0]:
            if node in common_ancestors:
                return node

        return None

    def _find_long_text_nodes(self, min_length = 100):
        """
        Identify nodes that contain significant amounts of direct, non-child text.
        :param min_length:
        :return:
        """

        result = []

        for element in self._root_node.find_all(True):
            if element.string is None:
                continue

            raw_text = element.string.strip()
            if len(raw_text) < min_length:
                continue

            result.append(element)

        return result
