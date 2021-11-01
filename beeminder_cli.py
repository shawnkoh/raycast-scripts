#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Beeminder
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon
# @raycast.packageName sg.shawnkoh.beeminder

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

import datetime

from dotenv import dotenv_values

import ankify
from beeminder import Beeminder

if __name__ == "__main__":
    config = dotenv_values()
    anki = ankify.Anki(ankify.COLLECTION_PATH, ankify.DECK_ID)
    beeminder = Beeminder(config["BEEMINDER_USERNAME"], config["BEEMINDER_AUTH_TOKEN"])
    date = datetime.date.today().strftime("%Y-%m-%d")
    response = beeminder.create_datapoint("anki-api", value=len(anki.notes_rated_today()), requestid=date)
    print("Created")
    print(response)
