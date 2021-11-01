
import datetime
import glob
import pprint

import ankify
import export_anki
import md_parser

pp = pprint.PrettyPrinter(indent=4)
_date = datetime.date.today().strftime("%Y-%m-%d")
_export_url = f"/Users/shawnkoh/repos/notes/anki/deleted-notes/{_date}.md"
urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

def extract_basic_prompts(md) -> dict[str, ankify.BasicPrompt]:
    basic_prompts = dict()
    for question_md, answer_md in md_parser.extract_basic_prompts(md).items():
        basic_prompts[question_md] = ankify.BasicPrompt(question_md, answer_md)
    return basic_prompts

def extract_cloze_prompts(md) -> dict[str, ankify.ClozePrompt]:
    cloze_prompts = dict()   
    for stripped_md, clozed_md in md_parser.extract_cloze_prompts(md).items():
        cloze_prompts[stripped_md] = ankify.ClozePrompt(stripped_md, clozed_md)
    return cloze_prompts

def import_markdowns(urls):
    import_basic_prompts = dict()
    import_cloze_prompts = dict()
    for url in urls:
        with open(url, "r") as file:
            md_text = file.read()
            md_text = md_parser.strip_title(md_text)
            md_text = md_parser.strip_backlink_blocks(md_text)

            basic_prompts = extract_basic_prompts(md_text)
            import_basic_prompts = import_basic_prompts | basic_prompts

            cloze_prompts = extract_cloze_prompts(md_text)
            import_cloze_prompts = import_cloze_prompts | cloze_prompts
    return import_basic_prompts, import_cloze_prompts

import_basic_prompts, import_cloze_prompts = import_markdowns(urls)

stats_created = 0
stats_updated = 0
stats_deleted = 0
stats_unchanged = 0

notes_to_remove = []

ankify.deck["mid"] = ankify.basic_notetype["id"]
ankify.collection.decks.save(ankify.deck)

# update and delete existing anki notes
for anki_note, anki_prompt in ankify.basic_notes():
    import_basic_prompt = import_basic_prompts.get(anki_prompt.question_md)
    if not import_basic_prompt:
        notes_to_remove.append(anki_note.id)
        continue
    import_basic_prompts.pop(import_basic_prompt.question_md)

    if not import_basic_prompt.is_different_from(anki_note):
        stats_unchanged += 1
        continue

    import_basic_prompt.override(anki_note)
    ankify.collection.update_note(anki_note)
    stats_updated += 1

# save new questions
for question_md, basic_prompt in import_basic_prompts.items():
    note = basic_prompt.to_anki_note()
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

ankify.deck["mid"] = ankify.cloze_notetype["id"]
ankify.collection.decks.save(ankify.deck)

for anki_note, anki_prompt in ankify.cloze_notes():
    import_cloze_prompt = import_cloze_prompts.get(anki_prompt.id)
    if not import_cloze_prompt:
        notes_to_remove.append(anki_note.id)
        continue
    import_cloze_prompts.pop(import_cloze_prompt.id)

    if not import_cloze_prompt.is_different_from(anki_note):
        stats_unchanged += 1
        continue

    import_cloze_prompt.override(anki_note)
    ankify.collection.update_note(anki_note)
    stats_updated += 1

for stripped_md, clozed_prompt in import_cloze_prompts.items():
    note = clozed_prompt.to_anki_note()
    ankify.collection.add_note(note, ankify.DECK_ID)
    stats_created += 1

export_anki.export_notes(notes_to_remove, _export_url)
ankify.collection.remove_notes(notes_to_remove)
stats_deleted += len(notes_to_remove)

ankify.collection.save()

print(f"statistics\ncreated:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}")
