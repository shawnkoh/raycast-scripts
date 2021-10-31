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

import ankify
import md_parser

pp = pprint.PrettyPrinter(indent=4)

SOURCE_ATTRIBUTE = 'data-source'

class BasicPrompt:
    def __init__(self, question_md: str, answer_md: str or None, source_attribute=SOURCE_ATTRIBUTE):
        self.question_md = question_md.strip()
        if answer_md:
            self.answer_md = answer_md.strip()
        else:
            self.answer_md = None

        self.source_attribute = source_attribute

    @classmethod
    def from_anki_note(cls, note, source_attribute=SOURCE_ATTRIBUTE):
        question_field = note.fields[0]
        if not question_field:
            return None

        question_md = md_parser.extract_data(question_field, source_attribute)
        if not question_md:
            question_md = md_parser.markdown_to_html(question_field)
        if not question_md:
            return None

        answer_md = None
        if answer_field := note.fields[1]:
            answer_md = md_parser.extract_data(answer_field, source_attribute)
            if not answer_md:
                answer_md = md_parser.markdown_to_html(answer_field)
        
        return cls(question_md, answer_md, source_attribute)

    def question_field(self):
        html = md_parser.markdown_to_html(self.question_md)
        field = md_parser.insert_data(html, self.source_attribute, self.question_md)
        return field

    def answer_field(self):
        if not self.answer_md:
            return None
        html = md_parser.markdown_to_html(self.answer_md)
        field = md_parser.insert_data(html, self.source_attribute, self.answer_md)
        return field

    def to_anki_note(self):
        note = ankify.collection.new_note(ankify.basic_notetype)
        note.fields[0] = self.question_field()
        note.fields[1] = self.answer_field()
        return note

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

import_basic_prompts = dict()
import_cloze_prompts = dict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        md_text = md_parser.strip_backlinks(md_text)
        basic_prompts = md_parser.extract_basic_prompts(md_text)
        basic_clozes = md_parser.extract_cloze_prompts(md_text)
        import_basic_prompts = import_basic_prompts | basic_prompts
        import_cloze_prompts = import_cloze_prompts | basic_clozes

stats_created = 0
stats_updated = 0
stats_deleted = 0
stats_unchanged = 0

def field_to_source(field):
    source = md_parser.extract_data(field, SOURCE_ATTRIBUTE)
    return source

def basic_to_field(md):
    html = md_parser.markdown_to_html(md)
    field = md_parser.insert_data(html, SOURCE_ATTRIBUTE, md)
    return field

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
    if anki_question_md not in import_basic_prompts:
        notes_to_remove.append(note_id)
        continue

    # At this point, they are the same
    import_question_md = anki_question_md
    import_answer_md = import_basic_prompts.get(import_question_md)

    # pop from list because its going to be processed
    import_basic_prompts.pop(import_question_md)

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
for question_md, answer_md in import_basic_prompts.items():
    note = BasicPrompt(question_md, answer_md).to_anki_note()
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
    if stripped_paragraph_md not in import_cloze_prompts:
        notes_to_remove.append(note_id)
        continue

    clozed_paragraph_md = import_cloze_prompts.get(stripped_paragraph_md)

    import_cloze_prompts.pop(stripped_paragraph_md)

    # Ignore if same
    field = cloze_to_field(stripped_paragraph_md, clozed_paragraph_md)
    if field == anki_field:
        stats_unchanged += 1
        continue

    note.fields[0] = field
    ankify.collection.update_note(note)
    stats_updated += 1

for stripped_paragraph, clozed_paragraph in import_cloze_prompts.items():
    note = ankify.collection.new_note(ankify.cloze_notetype)
    note.fields[0] = cloze_to_field(stripped_paragraph, clozed_paragraph)
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

ankify.collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

ankify.collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
