import arrow
from furl import furl

BASE_URL = "bear://x-callback-url/"


class Success:
    note: str
    identifier: str
    title: str
    tags: list[str]
    is_trashed: bool
    modification_date: arrow.Arrow
    creation_date: arrow.Arrow

    def __init__(self) -> None:
        pass


def open_note(
    id: str = None,
    title: str = None,
    header: str = None,
    exclude_trashed: bool = False,
    new_window: bool = None,
    float: bool = None,
    show_window: bool = None,
    open_note: bool = False,
    selected: bool = False,
    pin: bool = None,
    edit: bool = None,
) -> Success:
    """Open a note identified by its title or id and return its content.

    Args:
        id (str, optional): note unique identifier. Defaults to None.
        title (str, optional): optional note title. Defaults to None.
        header (str, optional): an header inside the note. Defaults to None.
        exclude_trashed (bool, optional): if yes exclude trashed notes. Defaults to False.
        new_window (bool, optional):  if yes open the note in an external window (MacOS only). Defaults to None.
        float (bool, optional): if yes makes the external window float on top (MacOS only). Defaults to None.
        show_window (bool, optional): if no the call don't force the opening of bear main window (MacOS only). Defaults to None.
        open_note (bool, optional): if no do not display the new note in Bear’s main or external window. Defaults to False.
        selected (bool, optional): if yes return the note currently selected in Bear (token required). Defaults to False.
        pin (bool, optional): if yes pin the note to the top of the list. Defaults to None.
        edit (bool, optional): if yes place the cursor inside the note editor. Defaults to None.
    """
    args = locals()
    for key, value in args.items():
        if value is None:
            args.pop(key)
        if type(value) != bool:
            continue
        args[key] = "yes" if value == True else "no"

    url = furl(BASE_URL)
    url.path = "open-note"
    url.args = args
    print(url.url)
    # bear://x-callback-url/[action]?[action parameters]&[x-callback parameters]
