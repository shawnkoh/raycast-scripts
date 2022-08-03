import datetime
import glob
import os
import webbrowser
from pathlib import Path
from timeit import timeit
from typing import Optional

import arrow
import click
import pyperclip
import typer
from functional import pseq, seq
from rich.console import Console
from rich.pretty import pprint
from rich.traceback import install

install(show_locals=True)
from tqdm import tqdm

from smart_bear.anki.anki import Anki
from smart_bear.bear import x_callback_url
from smart_bear.markdown.lexer import lexer
from smart_bear.markdown.nuke import uuid_if_sync_conflict
from smart_bear.markdown.parser import Root, parser
from smart_bear.visitor import extract_prompts

# Anki User Settings
PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/GCR")
COLLECTION_PATH = os.path.join(PROFILE_HOME, "collection.anki2")

DECK_ID = 1
BASIC_MODEL_ID = 1659511437904
CLOZE_MODEL_ID = 1659511443353
ANKI_DELETED_NOTES_EXPORT_PATH = f"/Users/shawnkoh/repos/notes/anki/deleted-notes/"
MARKDOWN_PATH = "/Users/shawnkoh/repos/notes/bear/"

app = typer.Typer()


def get_urls():
    return [
        *glob.glob(f"{MARKDOWN_PATH}/*.md"),
        # *glob.glob("/Users/shawnkoh/repos/windows/*.md"),
    ]


@app.command()
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


@app.command()
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


@app.command()
def open_today():
    a = arrow.now()
    title = a.format("YYYY-MM-DD")
    tag = "#daily/" + a.format("YYYY/MM")
    url = x_callback_url.open_note(title=title)
    url.args["x-error"] = x_callback_url.create(title=title, tags=[tag])
    webbrowser.open(url.url)


@app.command()
def backlinks():
    from .backlinks.pipeline import process

    process(get_urls())


@app.command()
def p():
    urls = get_urls()
    with open("report.txt", "wt") as report_file:
        console = Console(file=report_file)

        with console.capture() as capture:
            pseq(tqdm(urls)).map(_read).map(_parse).for_each(
                lambda x: pprint(x, console=console)
            )
        report_file.write(capture.get())


@app.command()
def pp():
    urls = get_urls()
    for url in tqdm(urls):
        with open(url, "r") as file:
            tokens = lexer.parse(file.read())
            root = parser.parse_partial(tokens)
            if root[1]:
                pprint(url)
                pprint(root)


@app.command()
def nuke_sync_conflicts():
    urls = get_urls()

    pseq(tqdm(urls)).map(_read).map(uuid_if_sync_conflict).filter(lambda x: x).for_each(
        lambda x: webbrowser.open(x_callback_url.trash(x).url)
    )


@app.command()
def missing_titles():
    urls = get_urls()

    pseq(tqdm(urls)).map(_read).map(_parse).filter(lambda x: x.title is None).for_each(
        lambda x: pprint(x)
    )


@app.command()
def benchmark():
    urls = get_urls()
    notes = seq(urls).map(_read).to_list()
    pseq_lexer_benchmark = (
        timeit(lambda: pseq(notes).map(lexer.parse).for_each(lambda _: _), number=3) / 3
    )
    pprint("pseq_lexer_benchmark: " + str(pseq_lexer_benchmark))


def _read(url) -> str:
    r = None
    with open(url, "r") as file:
        r = file.read()
    return r


def _parse(body: str) -> Root:
    tokens = lexer.parse(body)
    root = parser.parse(tokens)
    return root


@app.command()
def blocks(hours_busy: Optional[float] = typer.Argument(None)):
    if hours_busy is None:
        hours_busy = 0
    now = arrow.now()
    end = now.shift(days=1)
    end = end.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_left = end.int_timestamp - now.int_timestamp
    seconds_busy = hours_busy * 60 * 60
    work = work_blocks(
        seconds=seconds_left - seconds_busy,
        work=45,
        short_break=5,
        long_break=15,
        work_per_long_break=3,
    )
    max = work_blocks(
        seconds=seconds_left,
        work=45,
        short_break=5,
        long_break=15,
        work_per_long_break=3,
    )

    circledcirc = "⊚"
    bigcirc = "○"
    schedule_bullets = f"{bigcirc * work} | {circledcirc * (max - work)}"
    schedule = f"Today: {schedule_bullets} ({work}/{max})"
    pprint(schedule)
    pyperclip.copy(schedule)
    pprint("Copied focus blocks to clipboard")


def work_blocks(
    seconds: int, work: int, short_break: int, long_break: int, work_per_long_break: int
) -> int:
    seconds_per_minute = 60
    work *= seconds_per_minute
    short_break *= seconds_per_minute
    long_break *= seconds_per_minute

    work_count = 0
    long_break_quota = work_per_long_break
    index = seconds
    while index >= work:
        index -= work
        work_count += 1
        if long_break_quota == 1:
            index -= long_break
            long_break_quota = work_per_long_break
        else:
            index -= short_break
            long_break_quota -= 1
    return work_count


if __name__ == "__main__":
    app()
