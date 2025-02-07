from typing import Iterator

import attr
from bs4 import BeautifulSoup, Tag, PageElement
from loguru import logger

from heuristos.parser.shared import ParsedPolicy, ParsedSection, TextNode, SubNodeUnion

_TEXT_NODES = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "span", "a"]
_HEADER_NODES = ["h1", "h2", "h3", "h4", "h5", "h6"]
_SPANNABLE_HEADERS = ["b", "strong"]


def next_tag(iter: Iterator[PageElement]) -> Tag | None:
    while not isinstance((node := next(iter)), Tag):
        if node is None:
            return None
    return node


def _find_headers(node: Tag):
    """
    Find text nodes that are typically used for headers.
    """
    return node.find_all(_HEADER_NODES)


def _node_histogram(nodes: list[Tag]) -> dict:
    histogram = {}
    for node in nodes:
        histogram[node.name] = histogram.get(node.name, 0) + 1
    return histogram


def _is_spannable_header_inline(node: Tag) -> bool:
    """
    Heuristically detect if spannable header node types are shown inline.
    This helps determine if, for example, a <strong> text node is being used as a header.
    """
    previous_tag = next_tag(node.previous_siblings)
    successor_tag = next_tag(node.next_siblings)

    if previous_tag is None or successor_tag is None:
        return True
    if (previous_tag.name, successor_tag) == ("br", "br"):
        return False

    # todo: heuristic: extract the lowest block element type in lineage chain,
    #  and test if text value is equivalent to that of local node.
    #  If it is, then by extension, the element is displayed in it's own line.

    return True


@attr.s()
class HTMLPolicyParser:
    content: str = attr.ib()
    _root_node: BeautifulSoup = attr.ib(init=False)

    def __attrs_post_init__(self):
        self._root_node = BeautifulSoup(self.content, "html.parser")

    def stdrep(self) -> ParsedPolicy | None:
        # heuristically, I think long text nodes are going to be our best starting point.
        large_text_nodes = self._find_long_text_nodes()
        if not large_text_nodes:
            return None

        lca_long_nodes = self._lca(large_text_nodes)
        if lca_long_nodes is None:
            return None

        assumed_title = self._derive_title()
        if assumed_title is None:
            logger.warning("Could not derive title node for policy.")

        parsed_sections = self._parse_content(lca_long_nodes)

        return ParsedPolicy(title=assumed_title, content=parsed_sections)

    def _derive_title(self) -> str | None:
        header_precedence = self._derive_header_precedence()
        if not header_precedence:
            return None
        # access the text of the first least common header node type
        return self._root_node.find(header_precedence[0]).text

    def _parse_content(self, uniting: Tag) -> list[SubNodeUnion] | None:
        logger.info("Parsing content...")

        header_precedence = self._derive_header_precedence()

        if not header_precedence:
            return None

        if len(header_precedence) > 1:
            # remove the header type that we think is already reserved for the title.
            del header_precedence[0]

        node_seq = uniting.find_all(_TEXT_NODES)

        # frame indices are equivalent to that of header_precedence,
        # and the length thereof should be less than or equal.

        results = []

        precedence_frame = [0]
        frame = []
        while len(node_seq) > 0:
            current = node_seq.pop(0)

            if current.name in header_precedence:
                if (
                    prec_index := header_precedence.index(current.name)
                ) > precedence_frame[-1]:
                    # we hit a header with lower precedence
                    frame.append(ParsedSection(name=current.text, content=[]))
                    precedence_frame.append(prec_index)
                elif precedence_frame[-1] > prec_index:
                    # precondition: we hit a header with greater precedence

                    # we need to determine how far we should "collapse" the frame
                    frame_index = precedence_frame.index(prec_index)

                    if len(frame) == 1:
                        results.append(frame.pop())
                    else:
                        for i in range(len(frame) - 2, frame_index - 2, -1):
                            t = frame[i]
                            c = frame[i + 1]
                            t.content.append(c)
                            frame.pop()
                            precedence_frame.pop()

                    # now, push a new ParsedSection onto the frame.
                    frame.append(ParsedSection(name=current.text, content=[]))
                    precedence_frame.append(prec_index)
                else:
                    # precondition: precedence is equivalent

                    if len(frame) == 1:
                        results.append(frame.pop())
                    elif len(frame) >= 2:
                        frame[-2].content.append(frame.pop())

                    frame.append(ParsedSection(name=current.text, content=[]))
            else:
                if len(frame) == 0:
                    results.append(TextNode(text=current.text))
                    continue
                frame[-1].content.append(TextNode(text=current.text))

        return results


    def _derive_header_precedence(self) -> list[str]:
        nodes = self._root_node.find_all(_HEADER_NODES + _SPANNABLE_HEADERS)
        ranking = []

        for node in nodes:
            if node.name in ranking:
                continue
            ranking.append(node.name)

        return [
            n for n in _HEADER_NODES
            if n in ranking
        ]


    def _lca(self, nodes: list[Tag]) -> Tag | None:
        """
        Derive the least common ancestor of two or more nodes.
        """

        if not nodes:
            return None

        lookup_cache = {}

        def hashcode(node: Tag):
            return (node.sourceline, node.sourcepos).__hash__() if node else None

        # derive lineage of each input and then find the
        #  lowest node that is shared among them.

        ancestries = []
        for node in nodes:
            ancestry = []

            parent_node = node.parent
            parent_hashcode = hashcode(parent_node)
            lookup_cache[parent_hashcode] = parent_node

            while parent_node:
                ancestry.append(parent_hashcode)
                parent_node = parent_node.parent
                parent_hashcode = hashcode(parent_node)
                lookup_cache[parent_hashcode] = parent_node

            ancestries.append(ancestry)

        common_ancestors = set(ancestries[0])

        # eliminate all disjoint ancestors
        for ancestry in ancestries[1:]:
            common_ancestors &= set(ancestry)

        # iterate in depth order to determine lowest node.
        for node in ancestries[0]:
            if node in common_ancestors:
                return lookup_cache[node]

        return None

    def _find_long_text_nodes(self, min_length=100):
        """
        Identify nodes that contain significant amounts of direct, non-child text.
        """
        result = []

        for element in self._root_node.find_all(_TEXT_NODES):
            if element.string is None:
                continue

            raw_text = element.string.strip()
            if len(raw_text) < min_length:
                continue

            result.append(element)

        return result
