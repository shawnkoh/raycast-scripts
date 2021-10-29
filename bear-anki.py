#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Anki
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.anki

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob
import os
import pprint
from typing import OrderedDict

from anki.storage import _Collection

import md_parser

PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/Shawn")
DECK_ID = 1631681814019
MODEL_ID = 1635365642288

pp = pprint.PrettyPrinter(indent=4)

collection_path = os.path.join(PROFILE_HOME, "collection.anki2")

collection = _Collection(collection_path, log=True)
collection.decks.select(DECK_ID)

if collection.decks.get_current_id() != DECK_ID:
    print("Warning: deck id not found")
    exit()

deck = collection.decks.current()

notetype = collection.models.get(MODEL_ID)
if not notetype:
    print("model not found")
    exit()

deck["mid"] = notetype["id"]
collection.decks.save(deck)

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

qa_regex = r"Q:\s*((?:(?!A:).+(?:\n|\Z))+)(?:[\S\s]*?)(?:A:\s*((?:(?!Q:).+(?:\n|\Z))+))?"
import_basics = dict()
import_clozes = OrderedDict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        basics = md_parser.md_to_basics(md_text)
        clozes = md_parser.md_to_clozes(md_text)
        import_basics = import_basics | basics
        import_clozes = import_clozes | clozes

pp.pprint(import_clozes)

stats_created = 0
stats_updated = 0
stats_deleted = 0
stats_unchanged = 0

SOURCE_ATTRIBUTE = 'data-source'

def field_to_source(field):
    source = md_parser.extract_data(field, SOURCE_ATTRIBUTE)
    return source

def md_to_field(md):
    html = md_parser.markdown_to_html(md)
    field = md_parser.insert_data(html, SOURCE_ATTRIBUTE, md)
    return field

def basic_to_note(question, answer):
    note = collection.new_note(notetype)
    note.fields[0] = md_to_field(question)
    note.fields[1] = md_to_field(answer)
    return note

notes_to_remove = []

search_string = f"\"note:{notetype['name']}\""

anki_basic_note_ids = collection.find_notes(search_string)

# update and delete existing anki notes
for note_id in anki_basic_note_ids:
    note = collection.get_note(note_id)
    anki_question_field = note.fields[0]
    anki_answer_field = note.fields[1]

    # Delete if anki's question has no source
    anki_question_md = field_to_source(anki_question_field)
    if not anki_question_md:
        notes_to_remove.append(note_id)
        continue

    # Delete if anki's question is not found in import
    if anki_question_md not in import_basics:
        notes_to_remove.append(note_id)
        continue

    # At this point, they are the same
    import_question_md = anki_question_md
    import_answer_md = import_basics.get(import_question_md)

    # pop from list because its going to be processed
    import_basics.pop(import_question_md)

    # Ignore if anki's answer is the same as markdown
    anki_answer_md = field_to_source(anki_answer_field)
    if import_answer_md == anki_answer_md:
        stats_unchanged += 1
        continue

    # Edge case
    if import_answer_md == "" and anki_answer_md is None:
        stats_unchanged += 1
        continue
    
    # Update Anki's answer
    note.fields[1] = md_to_field(import_answer_md)
    collection.update_note(note)
    stats_updated += 1

# save new questions
for import_question_md, import_answer_md in import_basics.items():
    note = basic_to_note(import_question_md, import_answer_md)
    collection.add_note(note, DECK_ID)
    stats_created += 1

collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
