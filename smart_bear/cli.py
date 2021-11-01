
import datetime
import glob
import os
from pathlib import Path

from smart_bear.anki.anki import Anki

ANKI_DELETED_NOTES_EXPORT_PATH = f"/Users/shawnkoh/repos/notes/anki/deleted-notes/"
MARKDOWN_PATH = "/Users/shawnkoh/repos/notes/bear/"

if __name__ == "__main__":
    date = datetime.date.today().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    anki_deleted_notes_export_path = f"{ANKI_DELETED_NOTES_EXPORT_PATH}{date}.md"

    urls = glob.glob(f"{MARKDOWN_PATH}/*.md")
    import_basic_prompts, import_cloze_prompts = import_markdowns(urls)
    stats_created = 0
    stats_updated = 0
    stats_deleted = 0
    stats_unchanged = 0
    notes_to_remove = []

    anki = Anki()
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
