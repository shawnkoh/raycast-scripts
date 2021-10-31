import glob

import regex

import md_parser

_reference_standard_regex = regex.compile(r"(?i)(?m)^##+\s+References*\s*")
_reference_standard = "## References\n"
_eof_whitespace_regex = regex.compile(r"\s*$")

def _standardise_references(md: str) -> str:
    return regex.sub(_reference_standard_regex, _reference_standard, md)

def prettify(md: str) -> str:
    # apply standardisations

    md = _standardise_references(md)

    # extract and strip

    backlink_blocks = md_parser.extract_backlink_blocks(md)
    if backlink_blocks:
        md = md_parser.strip_backlink_blocks(md)

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
    # TODO: super hacky but whatever

    # strip eof dividers
    if references or backlink_blocks or tag_block:
        md = regex.sub(r"\s*(---)?\s*$", "", md)
        md += "\n\n---\n\n"

    if references:
        md = regex.sub(_eof_whitespace_regex, md)
        md += f"\n\n{references}\n"
    
    for backlink_block in backlink_blocks:
        md = regex.sub(_eof_whitespace_regex, md)
        md += f"\n\n{backlink_block}\n"

    if tag_block:
        md = regex.sub(_eof_whitespace_regex, md)
        md += f"\n\n{tag_block}\n\n"

    if bear_id:
        md = regex.sub(_eof_whitespace_regex, md)
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
