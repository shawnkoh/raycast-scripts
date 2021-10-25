#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Detect duplicate titles
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.detect-duplicate-titles

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob
import re
from os import replace

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

regex = r"(?i)#(.+)"

titles = {}

for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        match = re.search(regex, md_text)
        if not match:
            continue
        title = match.group(1).lower().strip()
        count = titles.get(title)
        if count:
            titles[title] = count + 1
        else:
            titles[title] = 1


for title in titles:
    count = titles.get(title)
    if count > 1:
        print(title)
