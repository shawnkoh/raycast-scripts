#!/usr/local/bin/fish

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Refresh bear backlinks
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon 🤖
# @raycast.packageName sg.shawnkoh.bear-backlinks

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

cd /Users/shawnkoh/repos/notes ;

git add -A && git commit -m "Commit unexpected changes" ;

python3 /Users/shawnkoh/repos/Bear-Markdown-Export/bear_export_sync.py --out /Users/shawnkoh/repos/notes/bear --backup /Users/shawnkoh/repos/notes/bear-backup ;
git add -A && git commit -m "Commit exported changes from Bear" ;

/usr/local/bin/node /Users/shawnkoh/.config/yarn/global/node_modules/@andymatuschak/note-link-janitor/dist/index.js /Users/shawnkoh/repos/notes/bear ;

git add -A && git commit -m "Update backlinks" ;

cd /Users/shawnkoh/repos/raycast-scripts ;
poetry run python pretty_bear.py ;
cd /Users/shawnkoh/repos/notes ;
git add -A && git commit -m "Pretty Bear" ;

python3 /Users/shawnkoh/repos/Bear-Markdown-Export/bear_export_sync.py --out /Users/shawnkoh/repos/notes/bear --backup /Users/shawnkoh/repos/notes/bear-backup ;
cd /Users/shawnkoh/repos/notes ;
git add -A && git commit -m "Commit imported changes to Bear" ;

git push ;

cd /Users/shawnkoh/repos/raycast-scripts ;
poetry run python detect-duplicate-titles.py ;
kill (pgrep Anki) ;
poetry run python smart_bear.py ;