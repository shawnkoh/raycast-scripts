
import datetime
import glob
import os
from pathlib import Path
from pprint import pprint

import click
from dotenv import dotenv_values

from smart_bear.anki.anki import Anki
from smart_bear.anki.prompts import extract_prompts
from smart_bear.beeminder.beeminder import Beeminder
from smart_bear.markdown.pretty_bear import prettify

# Anki User Settings
PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/Shawn")
COLLECTION_PATH = os.path.join(PROFILE_HOME, "collection.anki2")

DECK_ID = 1631681814019
BASIC_MODEL_ID = 1635365642288
CLOZE_MODEL_ID = 1635539433589
ANKI_DELETED_NOTES_EXPORT_PATH = f"/Users/shawnkoh/repos/notes/anki/deleted-notes/"
MARKDOWN_PATH = "/Users/shawnkoh/repos/notes/bear/"

@click.group()
def run():
    pass

@run.command()
def update_beeminder():
    click.confirm("Hello")
    config = dotenv_values()
    anki = Anki(collection_path=COLLECTION_PATH, deck_id=DECK_ID, basic_model_id=BASIC_MODEL_ID, cloze_model_id=CLOZE_MODEL_ID)
    beeminder = Beeminder(config["BEEMINDER_USERNAME"], config["BEEMINDER_AUTH_TOKEN"])
    date = datetime.date.today().strftime("%Y-%m-%d")
    response = beeminder.create_datapoint("anki-api", value=len(anki.notes_rated_today()), requestid=date)
    pprint("Created")
    pprint(response.content)

@run.command()
def sync_anki():
    date = datetime.date.today().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    anki_deleted_notes_export_path = f"{ANKI_DELETED_NOTES_EXPORT_PATH}{date}.md"

    urls = glob.glob(f"{MARKDOWN_PATH}/*.md")
    import_basic_prompts, import_cloze_prompts = extract_prompts(urls)
    stats_created = 0
    stats_updated = 0
    stats_deleted = 0
    stats_unchanged = 0
    notes_to_remove = []

    anki = Anki(collection_path=COLLECTION_PATH, deck_id=DECK_ID, basic_model_id=BASIC_MODEL_ID, cloze_model_id=CLOZE_MODEL_ID)
    anki.deck["mid"] = anki.basic_notetype["id"]
    anki.collection.decks.save(anki.deck)
    created, updated, unchanged, to_remove = anki.replace_ankifiable_prompts(anki.basic_notes(), import_basic_prompts)
    stats_created += created
    stats_updated += updated
    stats_unchanged += unchanged
    notes_to_remove += to_remove

    anki.deck["mid"] = anki.cloze_notetype["id"]
    anki.collection.decks.save(anki.deck)
    created, updated, unchanged, to_remove = anki.replace_ankifiable_prompts(anki.cloze_notes(), import_cloze_prompts)
    stats_created += created
    stats_updated += updated
    stats_unchanged += unchanged
    notes_to_remove += to_remove

    anki.export_notes(notes_to_remove, anki_deleted_notes_export_path)
    anki.collection.remove_notes(notes_to_remove)
    stats_deleted += len(notes_to_remove)

    anki.collection.save()

    stats = f"created:{stats_created}\nupdated:{stats_updated}\ndeleted:{stats_deleted}\nunchanged:{stats_unchanged}"
    print(stats)
    if stats_created or stats_updated or stats_deleted:
        stats_log = Path(f"/Users/shawnkoh/repos/notes/anki/stats-log/{date}.log")
        stats_log.parent.mkdir(parents=True, exist_ok=True)
        stats = f"{time}\n{stats}\n\n"
        mode = "a" if os.path.exists(stats_log.parent) else "w"
        with open(stats_log, mode) as file:
                file.write(stats)

@run.command()
def prettify_markdowns():
    urls = glob.glob(f"{MARKDOWN_PATH}/*.md")

    for url in urls:
        md = ""
        result = ""
        with open(url, "r") as file:
            md = file.read()
            result = prettify(md)

        if md == result:
            continue

        with open(url, "w") as file:
            file.write(result)
