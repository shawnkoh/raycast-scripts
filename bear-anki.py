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

qa_regex = r"Q:((?:(?!A:).+\n)+)(?:[\S\s]*?)(?:A:((?:(?!Q:).+\n)+))?"
md_basic_questions = dict()
md_cloze_questions = dict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        basic_matches = re.findall(qa_regex, md_text)
        for match in basic_matches:
            question = match[0]
            answer = match[1]
            md_basic_questions[question] = answer

notes_to_remove = []
# update and delete existing anki notes
for note_id in collection.find_notes(f"nid:{notetype['id']}"):
    note = collection.get_note(note_id)
    question = note.fields[0]
    answer = note.fields[1]

    md_qa_answer = md_basic_questions.get(question)
    if md_qa_answer:
        if answer != md_qa_answer:
            note.fields[1] = md_qa_answer
            collection.update_note(note)
    else:
        # question was deleted from markdown
        notes_to_remove.append(note_id)
    
    md_basic_questions.pop(question)

collection.remove_notes(notes_to_remove)

# save new notes
for question, answer in md_basic_questions.items():
    note = collection.new_note(notetype)
    note.fields[0] = question
    note.fields[1] = answer
    collection.add_note(note, DECK_ID)

collection.save()
