
from abc import abstractmethod
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

    def is_different_from(self, note) -> bool:
        return self.question_field != note.fields[0] or self.answer_field != note.fields[1]
    
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

    def is_different_from(self, note) -> bool:
        return self.field != note.fields[0]

    def override(self, note):
        note.fields[0] = self.field

def extract_prompts(urls):
    import_basic_prompts = dict()
    import_cloze_prompts = dict()
    for url in urls:
        document = Document(url)
        import_basic_prompts = import_basic_prompts | document.basic_prompts
        import_cloze_prompts = import_cloze_prompts | document.clozed_prompts
    return import_basic_prompts, import_cloze_prompts
