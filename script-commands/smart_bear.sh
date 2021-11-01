#!/usr/local/bin/fish

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Smart Bear
# @raycast.mode fullOutput
# @raycast.refreshTime 1h

# Optional parameters:
# @raycast.icon 🤖
# @raycast.packageName sg.shawnkoh.smart-bear

# Documentation:
# @raycast.author Shawn Koh
# @raycast.authorURL https://github.com/shawnkoh

cd ~/repos/notes ;

git add -A && git commit -m "Commit unexpected changes" ;

python3 ~/repos/Bear-Markdown-Export/bear_export_sync.py --out ~/repos/notes/bear --backup ~/repos/notes/bear-backup ;
git add -A && git commit -m "Commit exported changes from Bear" ;

cd ~/repos/raycast-scripts ;
poetry run smart_bear prettify-markdowns ;
cd ~/repos/notes ;
git add -A && git commit -m "Pretty Bear" ;

/usr/local/bin/node ~/.config/yarn/global/node_modules/@andymatuschak/note-link-janitor/dist/index.js ~/repos/notes/bear ;
git add -A && git commit -m "Update backlinks" ;

python3 ~/repos/Bear-Markdown-Export/bear_export_sync.py --out ~/repos/notes/bear --backup ~/repos/notes/bear-backup ;
cd ~/repos/notes ;
git add -A && git commit -m "Commit imported changes to Bear" ;

cd ~/repos/raycast-scripts ;
poetry run python script-commands/detect-duplicate-titles.py ;
poetry run smart_bear sync-anki ;
cd ~/repos/notes ;
git add -A && git commit -m "Commit Smart Bear" ;

git push ;