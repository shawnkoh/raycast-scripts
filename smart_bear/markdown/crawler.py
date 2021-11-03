from typing import Callable

import click
import regex
from smart_bear.markdown import md_parser


class Crawler:
    # two way dictionary because titles and urls should be mutually exclusive
    title_url_dictionary: dict[str, str]
    visited_titles: set
    titles_without_urls: set

    def __init__(self):
        self.title_url_dictionary = dict()
        self.visited_titles = set()
        self.titles_without_urls = set()

    def update_title_url_dictionary(self, urls):
        for url in urls:
            with open(url, "r") as file:
                title_line = file.readline()
                match = regex.search(md_parser._title_regex, title_line)
                if not match:
                    continue
                # Drop #
                title = match[0][2:]
                self.title_url_dictionary[title] = url
                self.title_url_dictionary[url] = title

    def crawl(self, url, functor: Callable[[str, str, str, list], None] = None):
        title = self.title_url_dictionary.get(url)
        if not title:
            click.echo(f"no title for url: {title}")
            return
        if title in self.visited_titles:
            return
        self.visited_titles.add(title)

        with open(url, "r") as file:
            md = file.read()
            backlink_blocks = md_parser.extract_backlink_blocks(md)
            md = md_parser.strip_backlink_blocks(md)
            if functor:
                functor(url, title, md, backlink_blocks)

            for title in regex.findall(md_parser._backlink_regex, md):
                url = self.title_url_dictionary.get(title)
                if not url:
                    self.titles_without_urls.add(title)
                    continue

                self.crawl(url, functor)
