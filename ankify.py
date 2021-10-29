import os

from anki.storage import _Collection

# Anki Settings
PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/Shawn")
DECK_ID = 1631681814019
BASIC_MODEL_ID = 1635365642288

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
