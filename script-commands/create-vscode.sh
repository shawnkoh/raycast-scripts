#!/opt/homebrew/bin/fish --login

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Create VSCode Project
# @raycast.mode silent
# @raycast.refreshTime 1h
# @raycast.argument1 { "type": "text", "placeholder": "project name", "optional": true }

# Optional parameters:
# @raycast.icon 🤖
# @raycast.packageName sg.shawnkoh.vscode-create

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

mkdir -p ~/repos/$argv[1]
code ~/repos/$argv[1]
git init