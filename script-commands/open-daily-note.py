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

date = datetime.today().strftime("%Y-%m-%d")
open_url = f"bear://x-callback-url/open-note?title={date}&new_window=yes&edit=yes"
# comma separated list of tags e.g. journal/daily,journal/weekly
tags = "journal/daily"
create_url = (
    f"bear://x-callback-url/create?title={date}&tags={tags}&new_window=yes&edit=yes"
)
create_url = urllib.parse.quote_plus(create_url)
url = f"{open_url}&x-error={create_url}"
webbrowser.open(url)
