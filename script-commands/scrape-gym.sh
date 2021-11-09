#!/opt/homebrew/bin/fish --login

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Scrape Gym
# @raycast.mode inline
# @raycast.refreshTime 3m
# @raycast.argument1 { "type": "text", "placeholder": "project name" }

# Optional parameters:
# @raycast.icon 🤖
# @raycast.packageName sg.shawnkoh.scrape-gym

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

cd ~/repos/scrape-gym
poetry run python scrape-gym.py
