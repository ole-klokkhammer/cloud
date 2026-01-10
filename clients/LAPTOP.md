# 

## brave
setup brave

## vscode
### Sync via Settings Sync (recommended):
1. `Ctrl+Shift+P` → "Settings Sync: Turn On"
2. Sign in with GitHub
3. Select what to sync (settings, extensions, keybindings, UI state)

## sync
rsync -ahHAX --info=progress2 --partial --no-links   --exclude '**/node_modules/'   --exclude '**/build/'   --exclude '**/dist/' --exclude '**/.venv/' --exclude '**/venv/'    /home/ole/workspace/ /run/media/ole/79DD-D7E3/FILES/workspace/