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

import webbrowser
from datetime import *

date = datetime.today().strftime("%Y-%m-%d")
url = f"bear://x-callback-url/open-note?title={date}&new_window=yes&edit=yes"
webbrowser.open(url)
