from functools import cached_property

import regex
from smart_bear.core.prompts import BasicPrompt, ClozePrompt, Identifiable
from smart_bear.markdown import md_parser, pretty_bear


class Document(Identifiable):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def id(self) -> str:
        return self.title

    @cached_property
    def title(self) -> str or None:
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
            tags.add(match[1])
            return ""

        self._current_md = regex.sub(md_parser._tag_regex, repl, self._current_md)
        return tags

    # TODO: implement my own backlinks
    @cached_property
    def backlink_blocks(self) -> list[str]:
        backlink_blocks = list()

        def repl(match: regex.Match) -> str:
            nonlocal backlink_blocks
            backlink_blocks.append(match[0])
            return ""

        self._current_md = regex.sub(md_parser._backlinks_regex, repl, self._current_md)
        return backlink_blocks

    @cached_property
    def links(self) -> set[str]:
        # force backlinks to be stripped to avoid double counting
        self.backlink_blocks
        links = set()

        def repl(match: regex.Match) -> str:
            nonlocal links
            links.add(match[1])
            return ""

        self._current_md = regex.sub(md_parser._link_regex, repl, self._current_md)
        return links

    @cached_property
    def bear_id(self) -> str or None:
        bear_id = None

        def repl(match: regex.Match) -> str:
            nonlocal bear_id
            bear_id = match[0]
            return ""

        self._current_md = regex.sub(md_parser._bear_id_regex, repl, self._current_md)
        return bear_id

    @cached_property
    def references(self) -> str or None:
        self._current_md = regex.sub(
            pretty_bear._reference_standard_regex,
            pretty_bear._reference_standard,
            self._current_md,
        )
        references = None

        def repl(match: regex.Match) -> str:
            nonlocal references
            references = match[0]
            return ""

        self._current_md = regex.sub(md_parser._reference_regex, repl, self._current_md)
        return references

    @cached_property
    def basic_prompts(self) -> dict[str, BasicPrompt]:
        self.title
        self.backlink_blocks
        basic_prompts = dict()
        for question_md, answer_md in md_parser.extract_basic_prompts(
            self._current_md
        ).items():
            prompt = BasicPrompt(question_md, answer_md)
            basic_prompts[prompt.id] = prompt
        return basic_prompts

    @cached_property
    def clozed_prompts(self) -> dict[str, ClozePrompt]:
        self.title
        self.backlink_blocks
        cloze_prompts = dict()
        for stripped_md, clozed_md in md_parser.extract_cloze_prompts(
            self._current_md
        ).items():
            prompt = ClozePrompt(stripped_md, clozed_md)
            cloze_prompts[prompt.id] = prompt
        return cloze_prompts

    def build_str(self, include_title: bool = True, include_backlinks: bool = True) -> str:
        self.title
        self.references
        self.backlink_blocks
        self.tags
        self.bear_id
        md = self._current_md

        tag_block = "\n".join(sorted(self.tags))

        print("self.title", self.title)

        # rebuild
        # TODO: super hacky but whatever

        if include_title:
            if title := self.title:
                md = f"# {title}\n{md}"

        # strip eof dividers
        if self.references or self.backlink_blocks or tag_block:
            md = regex.sub(r"\s*(---)?\s*$", "", md)
            md += "\n\n---\n\n"

        if self.references:
            md = regex.sub(pretty_bear._eof_whitespace_regex, "", md)
            md += f"\n\n{self.references}\n"

        if include_backlinks:
            for backlink_block in self.backlink_blocks:
                md = regex.sub(pretty_bear._eof_whitespace_regex, "", md)
                md += f"\n\n{backlink_block}\n"

        if tag_block:
            md = regex.sub(pretty_bear._eof_whitespace_regex, "", md)
            md += f"\n\n{tag_block}\n\n"

        if self.bear_id:
            md = regex.sub(pretty_bear._eof_whitespace_regex, "", md)
            # Intentionally end file with new line.
            md += f"\n\n{self.bear_id}\n"

        return md
