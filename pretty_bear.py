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

        # apply standardisations

        result = md_parser.standardise_references(result)

        # extract and strip

        backlinks = md_parser.extract_backlinks(result)
        if backlinks:
            result = md_parser.strip_backlinks(result)

        tag_block = md_parser.extract_tag_block(result)
        if tag_block:
            result = md_parser.strip_tags(result)

        references = md_parser.extract_references(result)
        if references:
            result = md_parser.strip_references(result)

        bear_id = md_parser.extract_bear_id(result)
        if bear_id:
            result = md_parser.strip_bear_id(result)

        # rebuild

        # clear whitespaces at end of file
        result = regex.sub(r"\s*$", "", result)
        # strip eof dividers
        result = regex.sub(r"\s*---\s*$", "", result)
        if references or backlinks or tag_block:
            result += "\n\n---\n\n"

        if references:
            result += f"\n\n{references}\n\n"
        
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
