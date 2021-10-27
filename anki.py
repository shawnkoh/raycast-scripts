#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Anki
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.anki

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob
import re

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

qa_regex = r"Q:((?:(?!A:).+\n)+)(?:[\S\s]*?)(?:A:((?:(?!Q:).+\n)+))?"
questions = dict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        matches = re.findall(qa_regex, md_text)
        for match in matches:
            question = match[0]
            answer = match[1]
            # TODO: Save to Anki
