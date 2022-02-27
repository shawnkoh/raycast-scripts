import datetime
import glob
import os
import pathlib
import re
import shutil
import webbrowser
from pathlib import Path
from rich.console import Console
from tqdm import tqdm

import arrow
import click
from dotenv import dotenv_values

from smart_bear.anki.anki import Anki
from smart_bear.anki.prompts import extract_prompts
from smart_bear.bear import x_callback_url
from smart_bear.beeminder.beeminder import Beeminder
from smart_bear.core.document import Document
from smart_bear.markdown import md_parser
from smart_bear.markdown.crawler import Crawler, link_map
from smart_bear.markdown.parser import parser
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
def update_beeminder():
    config = dotenv_values()
    anki = Anki(
        collection_path=COLLECTION_PATH,
        deck_id=DECK_ID,
        basic_model_id=BASIC_MODEL_ID,
        cloze_model_id=CLOZE_MODEL_ID,
    )
    beeminder = Beeminder(config["BEEMINDER_USERNAME"], config["BEEMINDER_AUTH_TOKEN"])
    date = datetime.date.today().strftime("%Y-%m-%d")
    response = beeminder.create_datapoint(
        "anki-api", value=len(anki.notes_rated_today()), requestid=date
    )


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
def sync_anki():
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
def prettify_markdowns():
    for url in get_urls():
        document = Document(url)
        result = document.build_str()
        if result == document.original_md:
            continue

        with open(url, "w") as file:
            file.write(result)


def _validate_tag(ctx, param, value) -> bool:
    if not md_parser.is_tag(value):
        raise click.BadParameter("--tag must be #tag_name")
    return value


@run.command()
@click.option("--tag", prompt=True, type=str, callback=_validate_tag)
@click.option("--filename", prompt=True, type=click.Path(exists=True))
@click.option("--dry", prompt=True, type=bool)
def add_tag_recursively(tag: str, filename: str, dry: bool):
    path = pathlib.Path(filename)
    count = 0

    def add_tag(document: Document):
        nonlocal count
        if tag in document.tags:
            return
        document.tags.add(tag)
        if not dry:
            with open(document.filename, "w") as file:
                file.write(document.build_str())
        count += 1

    urls = glob.glob(str(path.with_name("*.md")))
    title_url_map = link_map(urls)

    crawler = Crawler(title_url_map)
    crawler.crawl(filename, add_tag)
    click.echo(f"added {tag} to {count} notes")
    click.echo("titles without urls")
    titles_without_urls = sorted(crawler.titles_without_urls)
    click.echo("\n")
    click.echo("\n".join(titles_without_urls))


@run.command()
@click.option("--tag", prompt=True, type=str, callback=_validate_tag)
@click.option("--folder", prompt=True, type=click.Path(exists=True))
def export_tag(tag: str, folder: str):
    folder_path = pathlib.Path(folder)
    urls = glob.glob(MARKDOWN_PATH + "*.md")
    for url in urls:
        document = Document(url)

        if tag not in document.tags:
            continue

        pattern = re.compile(r"!\[\]\((.+)\)")
        # TODO: Quick hack
        for image_path in re.findall(pattern, document._current_md):
            image_path = pathlib.Path(MARKDOWN_PATH + "/" + image_path)
            print(image_path)
            shutil.copy2(image_path, folder_path)

        def repl(match: re.Match) -> str:
            path = pathlib.Path(match.group(1))
            return "[[" + path.name + "]]"

        document._current_md = re.sub(pattern, repl, document._current_md)

        note_path = folder_path / (document.title + ".md")
        with note_path.open("w") as file:
            # Obsidian treats filenames as headers, and has first class support for backlinks.
            file.write(document.build_str(include_title=False, include_backlinks=False))


@run.command()
def open_today():
    a = arrow.now()
    title = a.format("YYYY-MM-DD")
    tag = "#daily/" + a.format("YYYY/MM")
    url = x_callback_url.open_note(title=title)
    url.args["x-error"] = x_callback_url.create(title=title, tags=[tag])
    webbrowser.open(url.url)


@run.command()
def f():
    urls = get_urls()
    with open("report.txt", "wt") as report_file:
        console = Console(file=report_file)
        for url in tqdm(urls):
            with open(url, "r") as file:
                tokens = lexer.parse(file.read())
                root = parser.parse(tokens)
                pprint(root, console=console)


@run.command()
def p():
    urls = get_urls()
    for url in tqdm(urls):
        with open(url, "r") as file:
            print(url)
            tokens = lexer.parse(file.read())
            root = parser.parse(tokens)
            pprint(root)


@run.command()
def t():
    url = "/Users/shawnkoh/repos/notes/bear/What is my ideal window management.md"
    with open(url, "r") as file:
        tokens = lexer.parse(file.read())
        root = parser.parse(tokens)
        if root[1]:
            pprint(tokens)
            pprint(url)
            pprint(root)


@run.command()
def tt():
    url = "/Users/shawnkoh/repos/notes/bear/What is my ideal window management.md"
    with open(url, "r") as file:
        tokens = lexer.parse(file.read())
        root = parser.parse_partial(tokens)
        if root[1]:
            pprint(tokens)
            pprint(url)
            pprint(root)


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
