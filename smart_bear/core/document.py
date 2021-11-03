from functools import cached_property

import regex
from smart_bear.core.prompts import Identifiable
from smart_bear.markdown import md_parser


class Document(Identifiable):
    filename: str
    bear_id: str or None

    def __init__(self, filename: str) -> None:
        self.filename = filename
    
    def id(self) -> str:
        return self.title

    @cached_property
    def title(self) -> str:
        title = None
        def repl(match: regex.Match) -> str:
            nonlocal title
            title = match[1]
            return ""
        self._current_md = regex.sub(md_parser._title_regex, repl, self._current_md)
        return title

    @cached_property
    def original_md(self) -> str:
        with open(self.filename, "r") as file:
            return file.read()

    @cached_property
    def _current_md(self) -> str:
        return self.original_md

    @cached_property
    def tags(self) -> set[str]:
        tags = set()
        def repl(match: regex.Match) -> str:
            nonlocal tags
            tags.append(match[1])
            return ""
        self._current_md = regex.sub(md_parser._tag_regex, repl, self._current_md)
        return tags

    # TODO: implement my own backlinks
    @cached_property
    def backlink_blocks(self) -> list[str]:
        backlink_blocks = list()
        def repl(match: regex.Match) -> str:
            backlink_blocks.append(match[0])
        pass
        self._current_md = regex.sub(md_parser._backlinks_regex, repl, self._current_md)
        return backlink_blocks

    @cached_property
    def links(self) -> set[str]:
        # force backlinks to be stripped to avoid double counting
        self.backlink_blocks
        links = set()
        def repl(match: regex.Match) -> str:
            nonlocal links
            links.append(match[1])
            return ""
        self._current_md = regex.sub(md_parser._link_regex, repl, self._current_md)
        return links

    @cached_property
    def bear_id(self) -> str or None:
        bear_id = None
        def repl(match: regex.Match) -> str:
            bear_id = match[0]
            return ""
        self._current_md = regex.sub(md_parser._bear_id_regex, repl, self._current_md)
        return bear_id
