#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Cleanup tags
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.cleanup-tags

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob
import re

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

tag_regex = r"\s?<!--\s*(#[\w\/-]+)\s*-->\s?"
bear_id_regex = r"\s*(<!--\s*\{BearID:.+\}\s*-->)\s*"

progress = 0
count = len(urls)

for url in urls:
    progress += 1
    tags = []
    md_text = ""
    new_text = ""
    with open(url, "r") as file:
        print(f"{file.name} ({progress}/{count})")
        md_text = file.read()
        searched_tags = re.findall(tag_regex, md_text)
        if not searched_tags:
            continue

        # Strip all tags and their adjacent whitespaces
        new_text = re.sub(tag_regex, "", md_text)
        for tag in searched_tags:
            tags.append(tag)

    # Remove duplicate tags while preserving order
    tags = dict.fromkeys(tags)

    tag_block = "\n\n"
    for tag in tags:
        tag_block += f"{tag}\n"

    new_text = re.sub(bear_id_regex, rf"{tag_block}\n\1\n", new_text)

    if new_text == md_text:
        continue
    
    with open(url, "w") as file:
        file.write(new_text)
