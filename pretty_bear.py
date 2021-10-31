import glob

import regex

import md_parser

_reference_standard_regex = regex.compile(r"(?i)(?m)^##+\s+References*\s*")
_reference_standard = "## References\n"

def _standardise_references(md: str) -> str:
    return regex.sub(_reference_standard_regex, _reference_standard, md)

def prettify(md: str) -> str:
    # apply standardisations

    md = _standardise_references(md)

    # extract and strip

    backlinks = md_parser.extract_backlinks(md)
    if backlinks:
        md = md_parser.strip_backlinks(md)

    tag_block = md_parser.extract_tag_block(md)
    if tag_block:
        md = md_parser.strip_tags(md)

    references = md_parser.extract_references(md)
    if references:
        md = md_parser.strip_references(md)

    bear_id = md_parser.extract_bear_id(md)
    if bear_id:
        md = md_parser.strip_bear_id(md)

    # rebuild

    # clear whitespaces at end of file
    md = regex.sub(r"\s*$", "", md)
    # strip eof dividers
    md = regex.sub(r"\s*---\s*$", "", md)
    if references or backlinks or tag_block:
        md += "\n\n---\n\n"

    if references:
        md += f"\n\n{references}\n\n"
    
    if backlinks:
        md += f"\n\n{backlinks}\n\n"

    if tag_block:
        md += f"\n\n{tag_block}\n\n"

    if bear_id:
        md += f"\n\n{bear_id}"

    return md

urls = glob.glob("/Users/shawnkoh/repos/notes/bear/*.md")

for url in urls:
    md = ""
    result = ""
    with open(url, "r") as file:
        md = file.read()
        result = prettify(md)

    if md == result:
        continue

    with open(url, "w") as file:
        file.write(result)
