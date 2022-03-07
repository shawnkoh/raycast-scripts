import datetime
import glob
import os
import webbrowser
from pathlib import Path
from timeit import timeit

import arrow
import click
from functional import seq, pseq
from rich.console import Console
from rich.pretty import pprint
from tqdm import tqdm

from smart_bear.anki.anki import Anki
from smart_bear.bear import x_callback_url
from smart_bear.markdown.lexer import lexer
from smart_bear.markdown.nuke import uuid_if_sync_conflict
from smart_bear.markdown.parser import Root, parser
from smart_bear.visitor import extract_prompts

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

        with console.capture() as capture:
            pseq(tqdm(urls)).map(_read).map(_parse).for_each(
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


@run.command()
def nuke_sync_conflicts():
    urls = get_urls()

    pseq(tqdm(urls)).map(_read).map(uuid_if_sync_conflict).filter(lambda x: x).for_each(
        lambda x: webbrowser.open(x_callback_url.trash(x).url)
    )


@run.command()
def missing_titles():
    urls = get_urls()

    pseq(tqdm(urls)).map(_read).map(_parse).filter(lambda x: x.title is None).for_each(
        lambda x: pprint(x)
    )


@run.command()
def benchmark():
    urls_benchmark = timeit(lambda: get_urls, number=1000) / 1000
    pprint("urls_benchmark: " + str(urls_benchmark))
    urls = get_urls()
    # read_benchmark = timeit(lambda: pseq(urls).map(_read).to_list(), number=10) / 10
    # pprint("read_benchmark: " + str(read_benchmark))
    notes = pseq(urls).map(_read).to_list()
    lexer_benchmark = (
        timeit(lambda: pseq(notes).map(lexer.parse).to_list(), number=1) / 1
    )
    pprint("lexer_benchmark: " + str(lexer_benchmark))


def _read(url) -> str:
    r = None
    with open(url, "r") as file:
        r = file.read()
    return r


def _parse(body: str) -> Root:
    tokens = lexer.parse(body)
    root = parser.parse(tokens)
    return root
