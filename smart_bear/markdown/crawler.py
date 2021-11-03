from typing import Callable

import click
import regex
from smart_bear.markdown import md_parser


class Crawler:
    title_url_dictionary: dict[str, str]
    visited_titles = set()

    def __init__(self):
        self.title_url_dictionary = dict()

    def update_title_url_dictionary(self, urls):
        for url in urls:
            with open(url, "r") as file:
                md_text = file.read()
                match = regex.search(md_parser._title_regex, md_text)
                if not match:
                    continue
                # Drop #
                title = match[0][2:]
                self.title_url_dictionary[title] = url
                # print(title)

    def crawl(self, url, functor: Callable[[str, list], None] = None):
        with open(url, "r") as file:
            md = file.read()
            backlink_blocks = md_parser.extract_backlink_blocks(md)
            md = md_parser.strip_backlink_blocks(md)

            for title in regex.findall(md_parser._backlink_regex, md):
                if title in self.visited_titles:
                    continue
                self.visited_titles.add(title)
                if functor:
                    functor(md, backlink_blocks)

                url = self.title_url_dictionary.get(title)
                if not url:
                    click.echo(f"no url for title: {title}")
                    continue

                self.crawl(url)
