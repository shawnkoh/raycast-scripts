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
import pprint
from typing import OrderedDict

import ankify
import md_parser

pp = pprint.PrettyPrinter(indent=4)

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

import_basics = dict()
import_clozes = OrderedDict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        basics = md_parser.md_to_basics(md_text)
        clozes = md_parser.md_to_clozes(md_text)
        import_basics = import_basics | basics
        import_clozes = import_clozes | clozes

stats_created = 0
stats_updated = 0
stats_deleted = 0
stats_unchanged = 0

SOURCE_ATTRIBUTE = 'data-source'

def field_to_source(field):
    source = md_parser.extract_data(field, SOURCE_ATTRIBUTE)
    return source

def basic_to_field(md):
    html = md_parser.markdown_to_html(md)
    field = md_parser.insert_data(html, SOURCE_ATTRIBUTE, md)
    return field

def basic_to_note(question, answer):
    note = ankify.collection.new_note(ankify.basic_notetype)
    note.fields[0] = basic_to_field(question)
    note.fields[1] = basic_to_field(answer)
    return note

def cloze_to_field(stripped_paragraph, clozed_paragraph):
    clozed_paragraph_html = md_parser.markdown_to_html(clozed_paragraph)
    field = md_parser.insert_data(clozed_paragraph_html, SOURCE_ATTRIBUTE, stripped_paragraph)
    return field

notes_to_remove = []

ankify.deck["mid"] = ankify.basic_notetype["id"]
ankify.collection.decks.save(ankify.deck)

basic_note_ids = ankify.collection.find_notes(ankify.basic_search_string)
# update and delete existing anki notes
for note_id in basic_note_ids:
    note = ankify.collection.get_note(note_id)
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
    note.fields[1] = basic_to_field(import_answer_md)
    ankify.collection.update_note(note)
    stats_updated += 1

# save new questions
for import_question_md, import_answer_md in import_basics.items():
    note = basic_to_note(import_question_md, import_answer_md)
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

ankify.deck["mid"] = ankify.cloze_notetype["id"]
ankify.collection.decks.save(ankify.deck)
cloze_note_ids = ankify.collection.find_notes(ankify.cloze_search_string)

for note_id in cloze_note_ids:
    note = ankify.collection.get_note(note_id)
    anki_field = note.fields[0]

    # Delete if anki's question has no source
    stripped_paragraph_md = field_to_source(anki_field)
    if not stripped_paragraph_md:
        notes_to_remove.append(note_id)
        continue

    # Delete if anki's question is not found in import
    if stripped_paragraph_md not in import_clozes:
        notes_to_remove.append(note_id)
        continue

    clozed_paragraph_md = import_clozes.get(stripped_paragraph_md)

    import_clozes.pop(stripped_paragraph_md)

    # Ignore if same
    field = cloze_to_field(stripped_paragraph_md, clozed_paragraph_md)
    if field == anki_field:
        stats_unchanged += 1
        continue

    note.fields[0] = field
    ankify.collection.update_note(note)
    stats_updated += 1

for stripped_paragraph, clozed_paragraph in import_clozes.items():
    note = ankify.collection.new_note(ankify.cloze_notetype)
    note.fields[0] = cloze_to_field(stripped_paragraph, clozed_paragraph)
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

ankify.collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

ankify.collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
