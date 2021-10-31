import os

from anki.storage import _Collection

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

basic_search_string = f"\"note:{basic_notetype['name']}\""

cloze_notetype = collection.models.get(CLOZE_MODEL_ID)
if not cloze_notetype:
    print("cloze notetype not found")
    exit()

cloze_search_string = f"\"note:{cloze_notetype['name']}\""

class BasicPrompt(prompts.BasicPrompt):
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
    def to_anki_note(self):
        note = collection.new_note(cloze_notetype)
        note.fields[0] = self.field
        return note

    def is_different_from(self, note) -> bool:
        return self.field != note.fields[0]

    def override(self, note):
        note.fields[0] = self.field
