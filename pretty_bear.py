#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Pretty Bear
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.pretty-bear

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob

import regex

import md_parser

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

for url in urls:
    md = ""
    result = ""
    with open(url, "r") as file:
        md = file.read()
        result = md

        # extract and strip

        backlinks = md_parser.extract_backlinks(result)
        if backlinks:
            result = md_parser.strip_backlinks(result)

        tag_block = md_parser.extract_tag_block(result)
        if tag_block:
            result = md_parser.strip_tags(result)

        bear_id = md_parser.extract_bear_id(result)
        if bear_id:
            result = md_parser.strip_bear_id(result)

        # apply standardisations

        result = md_parser.standardise_references(result)

        # rebuild

        # clear whitespaces at end of file
        result = regex.sub(r"\s*$", "", result)
        
        if backlinks:
            result += f"\n\n{backlinks}\n\n"

        if tag_block:
            result += f"\n\n{tag_block}\n\n"

        if bear_id:
            result += f"\n\n{bear_id}"

    if md == result:
        continue

    with open(url, "w") as file:
        file.write(md)
