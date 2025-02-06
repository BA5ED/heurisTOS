import bs4
from bs4 import BeautifulSoup
from loguru import logger
from httpx import Client

from urllib.parse import urlparse


def extract_links_with_keywords(html: str, keywords: list[str]):
    soup = BeautifulSoup(html, 'html.parser')

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        for keyword in keywords:
            if keyword in href:
                yield href


class Crawler:

    def __init__(self, url: str):
        self._url = urlparse(url)
        self._graph = dict()  # node -> [edges]
        self._search_frontier = [url]
        self._client = Client()

    @property
    def origin(self):
        return self._url.scheme + '://' + self._url.netloc

    def resolve_link(self, link: str):
        if link.startswith('/'):
            return urlparse(self.origin + link)
        if link.startswith('http'):
            return urlparse(link)

        return urlparse(self._url.geturl() + '/' + link)

    def load_page(self, url: str) -> bs4.PageElement:
        logger.info("Fetching {}...", url)
        response = self._client.get(url)
        response.raise_for_status()

        return BeautifulSoup(response.text, 'html.parser')

    def crawl(self, keywords: list[str], content_keywords: list[str]):
        matched = []

        # todo: this needs a lot of work
        while self._search_frontier:
            url = self._search_frontier.pop()
            resolved = self.resolve_link(url)

            if resolved.netloc != self._url.netloc:
                logger.info("Skipping external {}...", resolved.geturl())
                self._graph[resolved.netloc] = []
                continue

            self._graph[url] = []
            page = self.load_page(resolved.geturl())

            for link in extract_links_with_keywords(str(page), keywords):
                logger.info("Link found: {}", link)
                if link not in self._graph:
                    self._graph[url] += [self.resolve_link(link)]
                    self._search_frontier.insert(0, link)

        return matched