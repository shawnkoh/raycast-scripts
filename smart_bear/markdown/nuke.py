from typing import Optional

from parsy import any_char

from smart_bear.markdown.lexer import BearID, bear_id, exclude_none


def uuid_if_sync_conflict(md: str) -> Optional[BearID]:
    if "Sync conflict!" in md:
        return (
            (bear_id.map(lambda x: x.value) | any_char.map(lambda _: None))
            .many()
            .map(exclude_none)
            .concat()
            .parse(md)
        )
    return None
