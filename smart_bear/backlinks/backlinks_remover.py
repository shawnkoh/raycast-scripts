from smart_bear.backlinks.parser import BacklinksBlock, Note
from functional import seq


def remove_backlinks(note: Note) -> Note:
    return Note(
        title=note.title,
        children=(
            seq(note.children)
            .filter(lambda child: not isinstance(child, BacklinksBlock))
            .to_list()
        ),
        bear_id=note.bear_id,
    )
