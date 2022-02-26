from abc import abstractmethod
from typing import Protocol

SOURCE_ATTRIBUTE = "data-source"


class Identifiable(Protocol):
    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError


class BasicPrompt(Identifiable):
    def __init__(
        self,
        question_md: str,
        answer_md: str or None,
        source_attribute=SOURCE_ATTRIBUTE,
    ):
        self.question_md = question_md.strip()
        if answer_md:
            self.answer_md = answer_md.strip()
        else:
            self.answer_md = None

        self.source_attribute = source_attribute

    @property
    def id(self) -> str:
        return self.question_md


class ClozePrompt(Identifiable):
    def __init__(
        self, stripped_md: str, clozed_md: str, source_attribute=SOURCE_ATTRIBUTE
    ):
        self.stripped_md = stripped_md.strip()
        self.clozed_md = clozed_md.strip()
        self.source_attribute = source_attribute

    @property
    def id(self) -> str:
        return self.stripped_md
