import regex

_reference_standard_regex = regex.compile(r"(?i)(?m)^##+\s+References*\s*")
_reference_standard = "## References\n"
_eof_whitespace_regex = regex.compile(r"\s*$")


def _standardise_references(md: str) -> str:
    return regex.sub(_reference_standard_regex, _reference_standard, md)
