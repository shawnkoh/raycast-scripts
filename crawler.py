#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Cleanup references
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.crawl

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import glob

import regex

import md_parser

url = "/Users/shawnkoh/repos/notes/bear/G2.md"
urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")
# TODO: need to exclude those in the backlinks block
backlink_regex = r"\[\[(.+)\]\]"
tag_regex = r"#evergreen"

url_title_dictionary = dict()
for url in urls:
    with open(url, "r") as file:
        md_text = file.read()
        match = regex.search(md_parser._title_regex, md_text)
        if not match:
            continue
        title = match.group(1)
        url_title_dictionary[title] = url

visited_urls = set()

def crawl(url):
    md_text = ""
    with open(url, "r") as file:
        md_text = file.read()

    match = regex.search(tag_regex, md_text)
    if not match:
        with open(url, "w") as file:
            md_text += "\n#evergreen\n"
            file.write(md_text)

    url_title_dictionary[url]

    unvisited_backlinks = get_backlinks(md_text) - visited_urls
    for link in unvisited_backlinks:
        crawl(link)

def get_backlinks(md_text):
    backlinks = regex.findall(backlink_regex, md_text)
    return set(backlinks)

for url in urls:
    md_text = ""
    with open(url, "r") as file:
        md_text = file.read()
        match = regex.search(regex, md_text)
        if not match:
            continue

    # with open(url, "w") as file:
    #     file.write(new_text)
