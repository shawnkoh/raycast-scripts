
import datetime
import glob
import os
from pathlib import Path
from pprint import pprint

import click
import regex
from dotenv import dotenv_values

from smart_bear.anki.anki import Anki
from smart_bear.anki.prompts import extract_prompts
from smart_bear.beeminder.beeminder import Beeminder
from smart_bear.markdown import md_parser
from smart_bear.markdown.crawler import Crawler
from smart_bear.markdown.pretty_bear import prettify

# Anki User Settings
PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/Shawn")
COLLECTION_PATH = os.path.join(PROFILE_HOME, "collection.anki2")

DECK_ID = 1631681814019
BASIC_MODEL_ID = 1635365642288
CLOZE_MODEL_ID = 1635539433589
ANKI_DELETED_NOTES_EXPORT_PATH = f"/Users/shawnkoh/repos/notes/anki/deleted-notes/"
MARKDOWN_PATH = "/Users/shawnkoh/repos/notes/bear/"

def get_urls():
    return glob.glob(f"{MARKDOWN_PATH}/*.md")

@click.group()
def run():
    pass

@run.command()
def update_beeminder():
    config = dotenv_values()
    anki = Anki(collection_path=COLLECTION_PATH, deck_id=DECK_ID, basic_model_id=BASIC_MODEL_ID, cloze_model_id=CLOZE_MODEL_ID)
    beeminder = Beeminder(config["BEEMINDER_USERNAME"], config["BEEMINDER_AUTH_TOKEN"])
    date = datetime.date.today().strftime("%Y-%m-%d")
    response = beeminder.create_datapoint("anki-api", value=len(anki.notes_rated_today()), requestid=date)
    pprint(response.json())

@run.command()
def study():
    anki = Anki(collection_path=COLLECTION_PATH, deck_id=DECK_ID, basic_model_id=BASIC_MODEL_ID, cloze_model_id=CLOZE_MODEL_ID)
    anki.study()
    if not anki.stats_studied:
        click.echo("no card to review")
    click.echo(f"studied {anki.stats_studied} cards")
    anki.collection.save()

@run.command()
def sync_anki():
    date = datetime.date.today().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    anki_deleted_notes_export_path = f"{ANKI_DELETED_NOTES_EXPORT_PATH}{date}.md"

    urls = get_urls()
    import_basic_prompts, import_cloze_prompts = extract_prompts(urls)
    notes_to_remove = []

    anki = Anki(collection_path=COLLECTION_PATH, deck_id=DECK_ID, basic_model_id=BASIC_MODEL_ID, cloze_model_id=CLOZE_MODEL_ID)
    anki.deck["mid"] = anki.basic_notetype["id"]
    anki.collection.decks.save(anki.deck)
    notes_to_remove += anki.replace_ankifiable_prompts(anki.basic_notes(), import_basic_prompts)

    anki.deck["mid"] = anki.cloze_notetype["id"]
    anki.collection.decks.save(anki.deck)
    notes_to_remove += anki.replace_ankifiable_prompts(anki.cloze_notes(), import_cloze_prompts)

    anki.export_notes(notes_to_remove, anki_deleted_notes_export_path)
    anki.remove_notes(notes_to_remove)

    anki.collection.save()

    stats = f"created:{anki.stats_created}\nupdated:{anki.stats_updated}\ndeleted:{anki.stats_deleted}\nunchanged:{anki.stats_unchanged}"
    print(stats)
    if anki.stats_created or anki.stats_updated or anki.stats_deleted:
        stats_log = Path(f"/Users/shawnkoh/repos/notes/anki/stats-log/{date}.log")
        stats_log.parent.mkdir(parents=True, exist_ok=True)
        stats = f"{time}\n{stats}\n\n"
        mode = "a" if os.path.exists(stats_log.parent) else "w"
        with open(stats_log, mode) as file:
                file.write(stats)

@run.command()
def prettify_markdowns():
    for url in get_urls():
        md = ""
        result = ""
        with open(url, "r") as file:
            md = file.read()
            result = prettify(md)

        if md == result:
            continue

        with open(url, "w") as file:
            file.write(result)


def _validate_tag(ctx, param, value) -> bool:
    if not regex.match(md_parser._tag_regex, value):
        raise click.BadParameter("tag must be #tag")
    return value

@run.command()
@click.option("--tag", prompt=True, callback=_validate_tag)
def add_tag_recursively(tag: str):
    def add_tag(url:str, title: str, md: str, backlink_blocks: list):
        pattern = r"(?<=\S?)#" + tag + r"(?=\S?)"
        if regex.match(pattern, md):
            return
        print(title)
    crawler = Crawler()
    urls = get_urls()
    crawler.update_title_url_dictionary(urls)
    crawler.crawl(f"{MARKDOWN_PATH}G2.md", add_tag)
    click.echo("titles without urls")
    titles_without_urls = sorted(crawler.titles_without_urls)
    click.echo("\n".join(titles_without_urls))
