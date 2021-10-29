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
import re

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
md_basic_questions = dict()
md_cloze_questions = dict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        basic_questions = md_parser.md_to_basic_questions(md_text)
        md_basic_questions = md_basic_questions | basic_questions

stats_created = 0
stats_updated = 0
stats_deleted = 0
stats_unchanged = 0

for question, answer in md_basic_questions.items():
    html_question = md_parser.markdown_to_html(question)
    print(html_question)
    # pp.pprint(html_question)

notes_to_remove = []
# update and delete existing anki notes
search_string = f"\"note:{notetype['name']}\""
# anki_basic_note_ids = collection.find_notes(search_string)
# print(len(anki_basic_note_ids))
# for note_id in anki_basic_note_ids:
#     note = collection.get_note(note_id)
#     pp.pprint(note.fields)
exit()
for note_id in anki_basic_note_ids:
    note = collection.get_note(note_id)
    question = note.fields[0]
    answer = note.fields[1]
    md_qa_answer = md_basic_questions.get(question)
    if md_qa_answer:
        pp.pprint(answer)
        pp.pprint(md_qa_answer)
        if answer != md_qa_answer:
            note.fields[1] = md_qa_answer
            collection.update_note(note)
            stats_updated += 1
        else:
            stats_unchanged += 1
    else:
        notes_to_remove.append(note_id)
    
    md_basic_questions.pop(question)

collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

# save new notes
for question, answer in md_basic_questions.items():
    note = collection.new_note(notetype)
    note.fields[0] = question
    note.fields[1] = answer
    collection.add_note(note, DECK_ID)
    stats_created += 1

collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
