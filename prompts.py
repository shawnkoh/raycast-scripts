import functools
from abc import abstractmethod
from typing import Protocol

import md_parser

SOURCE_ATTRIBUTE = 'data-source'

class Identifiable(Protocol):
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

class BasicPrompt(Identifiable):
    def __init__(self, question_md: str, answer_md: str or None, source_attribute=SOURCE_ATTRIBUTE):
        self.question_md = question_md.strip()
        if answer_md:
            self.answer_md = answer_md.strip()
        else:
            self.answer_md = None

        self.source_attribute = source_attribute

    def id(self) -> str:
        return self.question_md

    @functools.cached_property
    def question_field(self):
        html = md_parser.markdown_to_html(self.question_md)
        field = md_parser.insert_data(html, self.source_attribute, self.question_md)
        return field

    @functools.cached_property
    def answer_field(self):
        if not self.answer_md:
            return ""
        html = md_parser.markdown_to_html(self.answer_md)
        field = md_parser.insert_data(html, self.source_attribute, self.answer_md)
        return field

class ClozePrompt(Identifiable):
    def __init__(self, stripped_md: str, clozed_md: str, source_attribute=SOURCE_ATTRIBUTE):
        self.stripped_md = stripped_md.strip()
        self.clozed_md = clozed_md.strip()
        self.source_attribute = source_attribute
    
    def id(self) -> str:
        return self.stripped_md

    @functools.cached_property
    def field(self):
        html = md_parser.markdown_to_html(self.clozed_md)
        field = md_parser.insert_data(html, self.source_attribute, self.stripped_md)
        return field
