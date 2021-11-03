import datetime
import os
import pathlib

import click
import psutil
import regex
from smart_bear.anki.prompts import BasicPrompt, ClozePrompt
from smart_bear.markdown import md_parser

from anki.collection import SearchNode
from anki.decks import DeckDict
from anki.models import NotetypeDict
from anki.scheduler.v2 import Scheduler
from anki.storage import _Collection

# Change this if you're not on Mac.
# TODO: Too dangerous to use regex, better to compile a list of names instead
ANKI_PROCESS_NAME = "AnkiMac"

_anki_cloze_regex = regex.compile(r"(\{\{c\d+::((?>[^{}]|(?1))*)\}\})")
_multi_line_regex = regex.compile(r"\n\n+")

def close_anki_process(process_name: str = ANKI_PROCESS_NAME):
    for process in psutil.process_iter():
        if process.name() == process_name:
            process.kill()
            return

class Anki:
    collection: _Collection
    deck: DeckDict
    basic_notetype: NotetypeDict
    cloze_notetype: NotetypeDict
    stats_created: int
    stats_updated: int
    stats_deleted: int
    stats_unchanged: int
    stats_studied: int
    scheduler: Scheduler

    def __init__(self, collection_path, deck_id, basic_model_id, cloze_model_id, will_close_anki=True) -> None:
        if will_close_anki:
            close_anki_process()
        self.collection = _Collection(collection_path, log=True)
        self.collection.decks.select(deck_id)
        self.deck = self.collection.decks.current()
        self.stats_created = 0
        self.stats_updated = 0
        self.stats_deleted = 0
        self.stats_unchanged = 0
        self.stats_studied = 0
        self.scheduler = Scheduler(self.collection)

        # TODO: Throw instead
        if self.collection.decks.get_current_id() != deck_id:
            click.echo("deck id not found")
            raise click.Abort

        self.basic_notetype = self.collection.models.get(basic_model_id)
        if not self.basic_notetype:
            click.echo("basic_notetype not found")
            raise click.Abort

        self.cloze_notetype = self.collection.models.get(cloze_model_id)
        if not self.cloze_notetype:
            click.echo("cloze_notetype not found")
            raise click.Abort

    def basic_notes(self):
        search_string = f"\"note:{self.basic_notetype['name']}\""
        for note_id in self.collection.find_notes(search_string):
            note = self.collection.get_note(note_id)
            prompt = BasicPrompt.from_anki_note(note)
            yield (note, prompt)

    def cloze_notes(self):
        search_string = f"\"note:{self.cloze_notetype['name']}\""
        for note_id in self.collection.find_notes(search_string):
            note = self.collection.get_note(note_id)
            prompt = ClozePrompt.from_anki_note(note)
            yield (note, prompt)

    def notes_rated_today(self):
        rated = SearchNode.Rated(days=0, rating=0)
        node = SearchNode(rated=rated)
        search_string = self.collection.build_search_string(node)
        return self.collection.find_notes(search_string)

    def replace_ankifiable_prompts(self, anki_collection, import_collection):
        notes_to_remove = []

        # update and delete existing anki notes
        for anki_note, anki_prompt in anki_collection:
            import_prompt = import_collection.get(anki_prompt.id)
            if not import_prompt:
                notes_to_remove.append(anki_note.id)
                continue
            import_collection.pop(import_prompt.id)

            if not import_prompt.is_different_from(anki_note):
                self.stats_unchanged += 1
                continue

            import_prompt.override(anki_note)
            self.collection.update_note(anki_note)
            self.stats_updated += 1

        # save new questions
        for id, prompt in import_collection.items():
            if isinstance(prompt, ClozePrompt):
                note = self.collection.new_note(self.cloze_notetype)
            else:
                note = self.collection.new_note(self.basic_notetype)
            prompt.override(note)
            self.collection.add_note(note, self.deck["id"])
            self.stats_created += 1

        return notes_to_remove

    def remove_notes(self, note_ids):
        self.stats_deleted += self.collection.remove_notes(note_ids).count


    def export_notes(self, note_ids, export_url):
        date = datetime.date.today().strftime("%Y-%m-%d")
        time = datetime.datetime.now().strftime("%H:%M:%S")
        title = f"# Exported from Anki on {date}\n\n"
        export = ""
        for note_id in note_ids:
            note = self.collection.get_note(note_id)
            export += note_to_prompt_md(note)

        if export == "":
            print("nothing to export")
            return
        pathlib.Path(export_url).parent.mkdir(parents=True, exist_ok=True)
        if os.path.exists(export_url):
            with open(export_url, "a") as file:
                file.write(f"\n\n---\n\n{time}\n\n{export}")
        else:
            with open(export_url, "w") as file:
                file.write(f"{title}\n\n{time}\n\n{export}")

        print(f"exported to {export_url}")

    def study(self):
        while True:
            card = self.scheduler.getCard()
            self.scheduler.answerCard
            if not card:
                return
            self.stats_studied += 1
            note = card.note()
            prompt = None
            if note.cloze_numbers_in_fields():
                prompt = ClozePrompt.from_anki_note(note)
            else:
                prompt = BasicPrompt.from_anki_note(note)

            if not prompt:
                click.echo(md_parser.html_to_markdown(card.question()))
            elif isinstance(prompt, BasicPrompt):
                click.echo(prompt.question_md)
            elif isinstance(prompt, ClozePrompt):
                # TODO: Handle this better
                click.echo(md_parser.html_to_markdown(card.question()))

            click.confirm("Show Answer", default=True)
            if not prompt:
                click.echo(md_parser.html_to_markdown(card.answer()))
            elif isinstance(prompt, BasicPrompt):
                click.echo(prompt.answer_md)
            elif isinstance(prompt, ClozePrompt):
                click.echo(prompt.clozed_md)

            remembered = click.confirm("Remembered?", default=True)
            ease = 4 if remembered else 2
            self.scheduler.answerCard(card, ease)

def note_to_prompt_md(note):
    front = md_parser.html_to_markdown(note.fields[0])
    front = regex.sub(_multi_line_regex, "\n", front)
    back = md_parser.html_to_markdown(note.fields[1])
    back = regex.sub(_multi_line_regex, "\n", back)
    if note.cloze_numbers_in_fields():
        replace_regex = r"{\2}"
        front = regex.sub(_anki_cloze_regex, replace_regex, front)
        if back:
            return f"{front}\n---\n{back}\n\n"
        else:
            return f"{front}\n\n"
    else:
        return f"Q: {front}\nA: {back}\n\n"
