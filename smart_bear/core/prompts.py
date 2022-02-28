from abc import abstractmethod
from typing import Protocol
from attrs import define

SOURCE_ATTRIBUTE = "data-source"


class Identifiable(Protocol):
    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError


@define
class BasicPrompt(Identifiable):
    question_md: str
    answer_md: str | None
    source_attribute = SOURCE_ATTRIBUTE

    @property
    def id(self) -> str:
        return self.question_md


@define
class ClozePrompt(Identifiable):
    stripped_md: str
    clozed_md: str
    source_attribute = SOURCE_ATTRIBUTE

    @property
    def id(self) -> str:
        return self.stripped_md
