#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open daily note
# @raycast.mode silent
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.open-daily-note

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import urllib.parse
import webbrowser
from datetime import *
from subprocess import PIPE, Popen


def get_first_process():
    name_script = """
    global frontApp, frontAppName, windowTitle

    set windowTitle to ""
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set frontAppName to name of frontApp
        tell process frontAppName
            tell (1st window whose value of attribute "AXMain" is true)
                set windowTitle to value of attribute "AXTitle"
            end tell
        end tell
    end tell

    return {frontAppName, windowTitle}
    """

    p = Popen(
        ["osascript", "-"],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    stdout, stderr = p.communicate(name_script)
    process_name, window_title = stdout.split(",")
    process_name = process_name.strip()
    window_title = window_title.strip()
    return process_name, window_title


def hide_first_process():
    script = """
        tell application "System Events"
            set frontProcess to first process whose frontmost is true
            set visible of frontProcess to false
        end tell
    """
    p = Popen(
        ["osascript", "-"],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    stdout, stderr = p.communicate(script)


def title():
    return datetime.today().strftime("%Y-%m-%d")


def open_today(title: str):
    open_url = f"bear://x-callback-url/open-note?title={title}&new_window=yes&edit=yes"
    tags = "journal/daily"
    create_url = f"bear://x-callback-url/create?title={title}&tags={tags}&new_window=yes&edit=yes"
    create_url = urllib.parse.quote_plus(create_url)
    url = f"{open_url}&x-error={create_url}"
    webbrowser.open(url)


process_name, window_title = get_first_process()
title = title()

if process_name == "Bear" and window_title == title:
    hide_first_process()
else:
    open_today(title)
