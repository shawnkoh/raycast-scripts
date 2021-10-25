#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Cleanup references
# @raycast.mode silent
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.cleanup-references

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob
import re
from os import replace

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

regex = r"(?i)(\s*-*\s*)*#+\s+References*\s*"
replacement = "\n\n---\n\n## References\n"

for url in urls:
    tags = []
    md_text = ""
    with open(url, "r") as file:
        md_text = file.read()
        if re.match(regex, md_text) != replacement:
            continue

        md_text = re.sub(regex, replacement, md_text)
    
    with open(url, "w") as file:
        file.write(md_text)
