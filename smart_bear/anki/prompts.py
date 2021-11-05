from abc import abstractmethod
from functools import cached_property
from typing import Protocol

from smart_bear.core import prompts
from smart_bear.core.document import Document
from smart_bear.markdown import md_parser


class Ankifiable(Protocol):
    @classmethod
    @abstractmethod
    def from_anki_note(cls, note, source_attribute=prompts.SOURCE_ATTRIBUTE):
        raise NotImplementedError

    @abstractmethod
    def is_different_from(self, note) -> bool:
        raise NotImplementedError

    @abstractmethod
    def override(self, note):
        raise NotImplementedError


class BasicPrompt(prompts.BasicPrompt, Ankifiable):
    @classmethod
    def from_anki_note(cls, note, source_attribute=prompts.SOURCE_ATTRIBUTE):
        question_field = note.fields[0]
        if not question_field:
            return None

        question_md = md_parser.extract_data(question_field, source_attribute)
        if not question_md:
            question_md = md_parser.html_to_markdown(question_field)
        if not question_md:
            return None

        answer_md = None
        if answer_field := note.fields[1]:
            answer_md = md_parser.extract_data(answer_field, source_attribute)
            if not answer_md:
                answer_md = md_parser.html_to_markdown(answer_field)

        return cls(question_md, answer_md, source_attribute)

    @cached_property
    def question_field(self):
        html = md_parser.markdown_to_html(self.question_md)
        field = md_parser.insert_data(html, self.source_attribute, self.question_md)
        return field

    @cached_property
    def answer_field(self):
        if not self.answer_md:
            return ""
        html = md_parser.markdown_to_html(self.answer_md)
        field = md_parser.insert_data(html, self.source_attribute, self.answer_md)
        return field

    def is_different_from(self, note) -> bool:
        return (
            self.question_field != note.fields[0] or self.answer_field != note.fields[1]
        )

    def override(self, note):
        note.fields[0] = self.question_field
        note.fields[1] = self.answer_field


class ClozePrompt(prompts.ClozePrompt, Ankifiable):
    @classmethod
    def from_anki_note(cls, note, source_attribute=prompts.SOURCE_ATTRIBUTE):
        field = note.fields[0]
        if not field:
            return None

        md = md_parser.html_to_markdown(field)

        stripped_md = None
        clozed_md = md_parser.replace_anki_cloze_with_smart_cloze(md)

        stripped_md = md_parser.extract_data(field, source_attribute)
        if not stripped_md:
            stripped_md = md_parser.strip_anki_cloze(md)

        return cls(stripped_md, clozed_md, source_attribute)

    @cached_property
    def field(self):
        html = md_parser.markdown_to_html(self.clozed_md)
        field = md_parser.insert_data(html, self.source_attribute, self.stripped_md)
        return field

    def is_different_from(self, note) -> bool:
        return self.field != note.fields[0]

    def override(self, note):
        note.fields[0] = self.field


def extract_prompts(urls):
    import_basic_prompts = dict()
    import_cloze_prompts = dict()
    for url in urls:
        document = Document(url)
        for id, prompt in document.basic_prompts.items():
            # antipattern!
            prompt.__class__ = BasicPrompt
            import_basic_prompts[id] = prompt
        for id, prompt in document.clozed_prompts.items():
            # antipattern!
            prompt.__class__ = ClozePrompt
            import_cloze_prompts[id] = prompt
    return import_basic_prompts, import_cloze_prompts
