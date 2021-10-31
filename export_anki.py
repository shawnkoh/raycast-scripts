import datetime

import regex

import ankify
import md_parser

_anki_cloze_regex = regex.compile(r"(\{\{c\d+::((?>[^{}]|(?1))*)\}\})")
_multi_line_regex = regex.compile(r"\n\n+")

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

def export_notes(note_ids, export_url):
    date = datetime.date.today().strftime("%Y-%m-%d")
    title = f"# Exported from Anki on {date}\n\n"
    export = title
    for note_id in note_ids:
        note = ankify.collection.get_note(note_id)
        export += note_to_prompt_md(note)

    if export == title:
        print("nothing to export")
        return

    with open(export_url, "w") as file:
        file.write(export)

    print(f"exported to {export_url}")
