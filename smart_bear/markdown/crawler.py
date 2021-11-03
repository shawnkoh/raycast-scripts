from typing import Callable

import click
import regex
from smart_bear.markdown import md_parser


def link_map(urls):
    link_map = dict()
    for url in urls:
        with open(url, "r") as file:
            title_line = file.readline()
            match = regex.search(md_parser._title_regex, title_line)
            if not match:
                continue
            title = match[1]
            # two way dictionary because titles and urls should be mutually exclusive
            link_map[title] = url
            link_map[url] = title
    return link_map

class Crawler:
    visited_titles: set
    titles_without_urls: set

    def __init__(self, link_map: dict[str, str]):
        self.link_map = link_map
        self.visited_titles = set()
        self.titles_without_urls = set()

    def crawl(self, url, functor: Callable[[str, str, str], None] = None):
        title = self.link_map.get(url)
        if not title:
            click.echo(f"no title for url: {title}")
            return
        if title in self.visited_titles:
            return
        self.visited_titles.add(title)

        with open(url, "r") as file:
            md = file.read()
            if functor:
                functor(url, title, md)

            stripped_md = md_parser.strip_backlink_blocks(md)
            for title in regex.findall(md_parser._link_regex, stripped_md):
                url = self.link_map.get(title)
                if not url:
                    self.titles_without_urls.add(title)
                    continue

                self.crawl(url, functor)
