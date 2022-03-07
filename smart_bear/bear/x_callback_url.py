from enum import Enum

from furl import furl

# bear://x-callback-url/[action]?[action parameters]&[x-callback parameters]

BASE_URL = "bear://x-callback-url/"


def open_note(
    id: str = None,
    title: str = None,
    header: str = None,
    exclude_trashed: bool = None,
    new_window: bool = None,
    float: bool = None,
    show_window: bool = None,
    open_note: bool = None,
    selected: bool = None,
    pin: bool = None,
    edit: bool = None,
) -> furl:
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
    args = locals().copy()
    for key, value in locals().items():
        if value is None:
            args.pop(key)
        elif type(value) == bool:
            args[key] = "yes" if value is True else "no"

    url = furl(BASE_URL)
    url.path = "open-note"
    url.args = args
    return url


class CreateType(Enum):
    html = "html"


def create(
    title: str = None,
    text: str = None,
    clipboard: bool = None,
    tags: list[str] = None,
    file: bytes = None,
    filename: str = None,
    open_note: bool = None,
    new_window: bool = None,
    float: bool = None,
    show_window: bool = None,
    pin: bool = None,
    edit: bool = None,
    timestamp: bool = None,
    create_type: CreateType = None,
    url: str = None,
) -> furl:
    locals()["type"] = locals()["create_type"]
    locals().pop("create_type")
    args = locals().copy()
    for key, value in locals().items():
        if value is None:
            args.pop(key)
        elif type(value) == bool:
            args[key] = "yes" if value is True else "no"

    url = furl(BASE_URL)
    url.path = "create"
    url.args = args
    return url


class Mode(Enum):
    prepend = "prepend"
    append = "append"
    replace_all = "replace_all"
    replace = "replace"


def add_text(
    id: str = None,
    title: str = None,
    selected: bool = None,
    text: str = None,
    clipboard: bool = None,
    header: str = None,
    mode: Mode = None,
    new_line: bool = None,
    tags: list[str] = None,
    exclude_trashed: bool = None,
    open_note: bool = None,
    new_window: bool = None,
    show_window: bool = None,
    edit: bool = None,
    timestamp: bool = None,
) -> furl:
    args = locals().copy()
    for key, value in locals().items():
        if value is None:
            args.pop(key)
        elif type(value) == bool:
            args[key] = "yes" if value is True else "no"

    url = furl(BASE_URL)
    url.path = "add-text"
    url.args = args
    return url


def trash(id: str, show_window: bool = False) -> furl:
    args = locals().copy()
    for key, value in locals().items():
        if value is None:
            args.pop(key)
        elif type(value) == bool:
            args[key] = "yes" if value is True else "no"
    url = furl(BASE_URL)
    url.path = "trash"
    url.args = args
    return url
