#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Cleanup tags
# @raycast.mode silent
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

html_tag_regex = r"<!--\s*#[\w\/|-]+\s*-->\s?"
bear_id_regex = r"\s*(<!--\s*\{BearID:.+\}\s*-->)\s*"

for url in urls:
    tags = []
    md_text = ""
    with open(url, "r") as file:
        md_text = file.read()
        html_tags = re.findall(html_tag_regex, md_text)
        if not html_tags:
            continue

        # Strip all html tags and their adjacent whitespaces
        md_text = re.sub(html_tag_regex, "", md_text)

        for html_tag in html_tags:
            tags.append(html_tag.strip())

    # Remove duplicate tags while preserving order
    tags = dict.fromkeys(tags)

    tag_block = "\n\n"
    for tag in tags:
        tag_block += f"{tag}\n"

    md_text = re.sub(bear_id_regex, rf"{tag_block}\n\1\n", md_text)
    
    with open(url, "w") as file:
        file.write(md_text)
