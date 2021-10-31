
import datetime
import glob
import pprint

import ankify
import export_anki
import md_parser
import prompts

pp = pprint.PrettyPrinter(indent=4)
_date = datetime.date.today().strftime("%Y-%m-%d")
_export_url = f"/Users/shawnkoh/repos/notes/anki/deleted-notes/export-{_date}.md"
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
    anki_basic_prompt = prompts.BasicPrompt.from_anki_note(anki_note)

    question_md = anki_basic_prompt.question_md

    if question_md not in import_basic_prompts:
        notes_to_remove.append(note_id)
        continue

    import_answer_md = import_basic_prompts.get(question_md)
    import_basic_prompt = prompts.BasicPrompt(question_md, import_answer_md)

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
    note = prompts.BasicPrompt(question_md, answer_md).to_anki_note()
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

ankify.deck["mid"] = ankify.cloze_notetype["id"]
ankify.collection.decks.save(ankify.deck)
cloze_note_ids = ankify.collection.find_notes(ankify.cloze_search_string)

for note_id in cloze_note_ids:
    anki_note = ankify.collection.get_note(note_id)
    anki_cloze_prompt = prompts.ClozePrompt.from_anki_note(anki_note)

    stripped_md = anki_cloze_prompt.stripped_md

    if stripped_md not in import_cloze_prompts:
        notes_to_remove.append(note_id)
        continue

    import_clozed_md = import_cloze_prompts.get(stripped_md)
    import_cloze_prompt = prompts.ClozePrompt(stripped_md, import_clozed_md)

    import_field = import_cloze_prompt.field()

    import_cloze_prompts.pop(stripped_md)

    if anki_note.fields[0] == import_field:
        stats_unchanged += 1
        continue

    anki_note.fields[0] = import_field
    ankify.collection.update_note(anki_note)
    stats_updated += 1

for stripped_paragraph, clozed_paragraph in import_cloze_prompts.items():
    note = prompts.ClozePrompt(stripped_paragraph, clozed_paragraph).to_anki_note()
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

export_anki.export_notes(notes_to_remove, _export_url)
ankify.collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

ankify.collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
