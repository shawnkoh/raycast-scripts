from functional.streams import Stream
from rich.text import Text


def str_stream(before: str, after: str) -> Stream:
    from difflib import unified_diff

    import parsy
    from functional import seq

    diff = unified_diff(
        before,
        after,
        fromfile="before",
        tofile="after",
    )

    any_chars = parsy.any_char.at_least(1).concat()
    pp = (
        (
            parsy.peek(parsy.string("@@"))
            >> any_chars.map(lambda x: Text(text=x, style="bold magenta"))
        )
        | (
            parsy.string("-")
            >> (
                any_chars.map(lambda x: Text(text=x, style="bold red"))
                | parsy.success(Text("  ", style="on red"))
            )
        )
        | (
            parsy.string("+")
            >> (
                any_chars.map(lambda x: Text(text=x, style="bold green"))
                | parsy.success(Text("  ", style="on green"))
            )
        )
        | (parsy.string(" ") >> parsy.any_char.at_least(1).concat().map(Text))
        | (
            parsy.string("?")
            >> any_chars.map(lambda x: Text(text=x, style="bold magenta"))
        )
        | (any_chars.map(Text))
    )

    return seq(diff).drop(2).map(pp.parse)
