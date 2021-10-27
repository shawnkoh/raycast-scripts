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
        # print(url)
        matches = re.findall(qa_regex, md_text)
        if len(matches) > 0:
            print(url)
        for match in matches:
            print(match)
            # print(matches[1])
        # while True:
        #     match = re.search(qa_regex, md_text)
        #     if not match:
        #         break
        #     print(match.group(1))
        #     print(match.group(2))
        #     questions[match.group(1)] = match.group(2)
        #     md_text = re.sub(qa_regex, "", md_text)
