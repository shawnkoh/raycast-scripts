import os

from anki.storage import _Collection

import md_parser
import prompts

# Anki Settings
PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/Shawn")
DECK_ID = 1631681814019
BASIC_MODEL_ID = 1635365642288
CLOZE_MODEL_ID = 1635539433589

collection_path = os.path.join(PROFILE_HOME, "collection.anki2")

collection = _Collection(collection_path, log=True)
collection.decks.select(DECK_ID)

if collection.decks.get_current_id() != DECK_ID:
    print("Warning: deck id not found")
    exit()

deck = collection.decks.current()

basic_notetype = collection.models.get(BASIC_MODEL_ID)
if not basic_notetype:
    print("basic notetype not found")
    exit()

_basic_search_string = f"\"note:{basic_notetype['name']}\""

cloze_notetype = collection.models.get(CLOZE_MODEL_ID)
if not cloze_notetype:
    print("cloze notetype not found")
    exit()

_cloze_search_string = f"\"note:{cloze_notetype['name']}\""

class BasicPrompt(prompts.BasicPrompt):
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

    def to_anki_note(self):
        note = collection.new_note(basic_notetype)
        note.fields[0] = self.question_field()
        note.fields[1] = self.answer_field()
        return note

    def is_different_from(self, note) -> bool:
        return self.question_field != note.fields[0] or self.answer_field != note.fields[1]
    
    def override(self, note):
        note.fields[0] = self.question_field
        note.fields[1] = self.answer_field

class ClozePrompt(prompts.ClozePrompt):
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

    def to_anki_note(self):
        note = collection.new_note(cloze_notetype)
        note.fields[0] = self.field
        return note

    def is_different_from(self, note) -> bool:
        return self.field != note.fields[0]

    def override(self, note):
        note.fields[0] = self.field

def basic_notes():
    for note_id in collection.find_notes(_basic_search_string):
        note = collection.get_note(note_id)
        prompt = BasicPrompt.from_anki_note(note)
        yield (note, prompt)

def cloze_notes():
    for note_id in collection.find_notes(_cloze_search_string):
        note = collection.get_note(note_id)
        prompt = ClozePrompt.from_anki_note(note)
        yield (note, prompt)
