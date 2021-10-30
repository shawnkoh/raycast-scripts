import datetime
import os

import anki
import regex
import unmarkd

# anki changes cwd, save it here
_date = datetime.date.today().strftime("%Y-%m-%d")
_export_url = f"{os.getcwd()}/anki-export-{_date}.md"
import ankify

_delete_notes = False

_export = f"# Exported from Anki on {_date}\n\n"
_cloze_regex = regex.compile(r"(\{\{c\d+::((?>[^{}]|(?1))*)\}\})")
_multi_line_regex = regex.compile(r"\n\n+")

for note_id in ankify.collection.find_notes(""):
    note = ankify.collection.get_note(note_id)
    if note.mid == ankify.CLOZE_MODEL_ID or note.mid == ankify.BASIC_MODEL_ID:
        continue
    front = unmarkd.unmark(note.fields[0])
    front = regex.sub(_multi_line_regex, "\n", front)
    back = unmarkd.unmark(note.fields[1])
    back = regex.sub(_multi_line_regex, "\n", back)
    if note.cloze_numbers_in_fields():
        replace_regex = r"{\2}"
        front = regex.sub(_cloze_regex, replace_regex, front)
        if back:
            _export += f"{front}\n---\n{back}\n\n"
        else:
            _export += f"{front}\n\n"
    else:
        _export += f"Q:{front}\nA:{back}\n\n"

with open(_export_url, "w") as file:
    file.write(_export)

print(f"exported to {_export_url}")

if not _delete_notes:
    exit()
ankify.collection.remove_notes(note_id)
ankify.collection.save()
print("deleted notes")
