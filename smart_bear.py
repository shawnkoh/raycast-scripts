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
            question_md = md_parser.html_to_markdown(question_field)
        if not question_md:
            return None

        answer_md = None
        if answer_field := note.fields[1]:
            answer_md = md_parser.extract_data(answer_field, source_attribute)
            if not answer_md:
                answer_md = md_parser.html_to_markdown(answer_field)
        
        return cls(question_md, answer_md, source_attribute)

    def question_field(self):
        html = md_parser.markdown_to_html(self.question_md)
        field = md_parser.insert_data(html, self.source_attribute, self.question_md)
        return field

    def answer_field(self):
        if not self.answer_md:
            return ""
        html = md_parser.markdown_to_html(self.answer_md)
        field = md_parser.insert_data(html, self.source_attribute, self.answer_md)
        return field

    def to_anki_note(self):
        note = ankify.collection.new_note(ankify.basic_notetype)
        note.fields[0] = self.question_field()
        note.fields[1] = self.answer_field()
        return note

class ClozePrompt:
    def __init__(self, stripped_md: str, clozed_md: str, source_attribute=SOURCE_ATTRIBUTE):
        self.stripped_md = stripped_md.strip()
        self.clozed_md = clozed_md.strip()
        self.source_attribute = source_attribute

    @classmethod
    def from_anki_note(cls, note, source_attribute=SOURCE_ATTRIBUTE):
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

    def field(self):
        html = md_parser.markdown_to_html(self.clozed_md)
        field = md_parser.insert_data(html, self.source_attribute, self.stripped_md)
        return field

    def to_anki_note(self):
        note = ankify.collection.new_note(ankify.basic_notetype)
        note.fields[0] = self.field()
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

notes_to_remove = []

ankify.deck["mid"] = ankify.basic_notetype["id"]
ankify.collection.decks.save(ankify.deck)

basic_note_ids = ankify.collection.find_notes(ankify.basic_search_string)
# update and delete existing anki notes
for note_id in basic_note_ids:
    anki_note = ankify.collection.get_note(note_id)
    anki_basic_prompt = BasicPrompt.from_anki_note(anki_note)

    question_md = anki_basic_prompt.question_md

    if question_md not in import_basic_prompts:
        notes_to_remove.append(note_id)
        continue

    import_answer_md = import_basic_prompts.get(question_md)
    import_basic_prompt = BasicPrompt(question_md, import_answer_md)

    import_question_field = import_basic_prompt.question_field()
    import_answer_field = import_basic_prompt.answer_field()

    need_update = False

    if anki_note.fields[0] != import_question_field:
        anki_note.fields[0] = import_question_field
        need_update = True
    if anki_note.fields[1] != import_answer_field:
        anki_note.fields[1] = import_answer_field
        need_update = True

    import_basic_prompts.pop(question_md)

    if not need_update:
        stats_unchanged += 1
        continue

    ankify.collection.update_note(anki_note)
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
    anki_note = ankify.collection.get_note(note_id)
    anki_cloze_prompt = ClozePrompt.from_anki_note(anki_note)

    stripped_md = anki_cloze_prompt.stripped_md

    if stripped_md not in import_cloze_prompts:
        notes_to_remove.append(note_id)
        continue

    import_clozed_md = import_cloze_prompts.get(stripped_md)
    import_cloze_prompt = ClozePrompt(stripped_md, import_clozed_md)

    import_field = import_cloze_prompt.field()

    import_cloze_prompts.pop(stripped_md)

    if anki_note.fields[0] == import_field:
        stats_unchanged += 1
        continue

    anki_note.fields[0] = import_field
    ankify.collection.update_note(anki_note)
    stats_updated += 1

for stripped_paragraph, clozed_paragraph in import_cloze_prompts.items():
    note = ClozePrompt(stripped_paragraph, clozed_paragraph).to_anki_note()
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

ankify.collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

ankify.collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
