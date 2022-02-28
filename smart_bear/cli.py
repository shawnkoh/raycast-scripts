import datetime
import glob
import os
import pathlib
from functional import pseq
import webbrowser
from pathlib import Path
from rich.console import Console
from tqdm import tqdm

import arrow
import click
from smart_bear.anki import visitor

from smart_bear.anki.anki import Anki
from smart_bear.anki.prompts import extract_prompts
from smart_bear.bear import x_callback_url
from smart_bear.markdown.parser import Root, parser
from smart_bear.markdown.lexer import lexer
from rich.pretty import pprint

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
def study():
    anki = Anki(
        collection_path=COLLECTION_PATH,
        deck_id=DECK_ID,
        basic_model_id=BASIC_MODEL_ID,
        cloze_model_id=CLOZE_MODEL_ID,
    )
    anki.study()
    if not anki.stats_studied:
        click.echo("no card to review")
    click.echo(f"studied {anki.stats_studied} cards")
    anki.collection.save()


@run.command()
def anki():
    date = datetime.date.today().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    anki_deleted_notes_export_path = f"{ANKI_DELETED_NOTES_EXPORT_PATH}{date}.md"

    urls = get_urls()
    import_basic_prompts, import_cloze_prompts = extract_prompts(urls)
    notes_to_remove = []

    anki = Anki(
        collection_path=COLLECTION_PATH,
        deck_id=DECK_ID,
        basic_model_id=BASIC_MODEL_ID,
        cloze_model_id=CLOZE_MODEL_ID,
    )
    anki.deck["mid"] = anki.basic_notetype["id"]
    anki.collection.decks.save(anki.deck)
    notes_to_remove += anki.replace_ankifiable_prompts(
        anki.basic_notes(), import_basic_prompts
    )

    anki.deck["mid"] = anki.cloze_notetype["id"]
    anki.collection.decks.save(anki.deck)
    notes_to_remove += anki.replace_ankifiable_prompts(
        anki.cloze_notes(), import_cloze_prompts
    )

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
def open_today():
    a = arrow.now()
    title = a.format("YYYY-MM-DD")
    tag = "#daily/" + a.format("YYYY/MM")
    url = x_callback_url.open_note(title=title)
    url.args["x-error"] = x_callback_url.create(title=title, tags=[tag])
    webbrowser.open(url.url)


@run.command()
def p():
    urls = get_urls()
    with open("report.txt", "wt") as report_file:
        console = Console(file=report_file)

        def read(url) -> str:
            r = None
            with open(url, "r") as file:
                r = file.read()
            return r

        def parse(body: str) -> Root:
            tokens = lexer.parse(body)
            root = parser.parse(tokens)
            return root

        with console.capture() as capture:
            pseq(tqdm(urls)).map(read).map(parse).for_each(
                lambda x: pprint(x, console=console)
            )
        report_file.write(capture.get())


@run.command()
def pp():
    urls = get_urls()
    for url in tqdm(urls):
        with open(url, "r") as file:
            tokens = lexer.parse(file.read())
            root = parser.parse_partial(tokens)
            if root[1]:
                pprint(url)
                pprint(root)
