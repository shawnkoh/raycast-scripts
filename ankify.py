import os
from abc import abstractmethod
from typing import Protocol

import psutil
from anki.collection import SearchNode
from anki.decks import DeckDict
from anki.storage import _Collection

import md_parser
import prompts

# Anki User Settings
DECK_ID = 1631681814019
BASIC_MODEL_ID = 1635365642288
CLOZE_MODEL_ID = 1635539433589
PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/Shawn")
COLLECTION_PATH = os.path.join(PROFILE_HOME, "collection.anki2")

# Change this if you're not on Mac.
# TODO: Too dangerous to use regex, better to compile a list of names instead
ANKI_PROCESS_NAME = "AnkiMac"

def close_anki_process():
    for process in psutil.process_iter():
        if process.name() == ANKI_PROCESS_NAME:
            process.kill()
            return

class Anki:
    collection: _Collection
    deck: DeckDict

    def __init__(self, collection_path=COLLECTION_PATH, deck_id=DECK_ID, basic_model_id=BASIC_MODEL_ID, cloze_model_id=CLOZE_MODEL_ID, will_close_anki=True) -> None:
        if will_close_anki:
            close_anki_process()
        self.collection = _Collection(collection_path, log=True)
        self.collection.decks.select(deck_id)
        self.deck = self.collection.decks.current()
        if self.collection.decks.get_current_id() != DECK_ID:
            print("Warning: deck id not found")
            exit()

        self.basic_notetype = self.collection.models.get(basic_model_id)
        if not self.basic_notetype:
            print("basic notetype not found")
            exit()

        self.basic_search_string = f"\"note:{self.basic_notetype['name']}\""

        self.cloze_notetype = self.collection.models.get(cloze_model_id)
        if not self.cloze_notetype:
            print("cloze notetype not found")
            exit()

    def basic_notes(self):
        for note_id in self.collection.find_notes(self.basic_search_string):
            note = self.collection.get_note(note_id)
            prompt = BasicPrompt.from_anki_note(note)
            yield (note, prompt)

    def cloze_notes(self):
        cloze_search_string = f"\"note:{self.cloze_notetype['name']}\""
        for note_id in self.collection.find_notes(cloze_search_string):
            note = self.collection.get_note(note_id)
            prompt = ClozePrompt.from_anki_note(note)
            yield (note, prompt)

    def notes_rated_today(self):
        search_string = self.collection.build_search_string(SearchNode(rated=SearchNode.Rated(days=0, rating=0)))
        return len(self.collection.find_notes(search_string))

    def replace_ankifiable_prompts(self, anki_collection, import_collection):
        created = 0
        updated = 0
        unchanged = 0
        notes_to_remove = []

        # update and delete existing anki notes
        for anki_note, anki_prompt in anki_collection:
            import_basic_prompt = import_collection.get(anki_prompt.id)
            if not import_basic_prompt:
                notes_to_remove.append(anki_note.id)
                continue
            import_collection.pop(import_basic_prompt.id)

            if not import_basic_prompt.is_different_from(anki_note):
                unchanged += 1
                continue

            import_basic_prompt.override(anki_note)
            self.collection.update_note(anki_note)
            updated += 1

        # save new questions
        for id, basic_prompt in import_collection.items():
            note = basic_prompt.to_anki_note()
            self.collection.add_note(note, self.DECK_ID)
            created += 1

        return created, updated, unchanged, notes_to_remove

class Ankifiable(Protocol):
    @classmethod
    @abstractmethod
    def from_anki_note(cls, note, source_attribute=prompts.SOURCE_ATTRIBUTE):
        raise NotImplementedError

    @abstractmethod
    def to_anki_note(self):
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

    def to_anki_note(self, anki: Anki):
        note = anki.collection.new_note(anki.basic_notetype)
        note.fields[0] = self.question_field
        note.fields[1] = self.answer_field
        return note

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

    def to_anki_note(self, anki: Anki):
        note = anki.collection.new_note(anki.cloze_notetype)
        note.fields[0] = self.field
        return note

    def is_different_from(self, note) -> bool:
        return self.field != note.fields[0]

    def override(self, note):
        note.fields[0] = self.field
