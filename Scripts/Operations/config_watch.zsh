#!/bin/zsh
# ------------------------------------------------------------------------------
# Antigravity Config Watcher
# Watches ~/.gemini/config/ for Antigravity recreating config.json, then
# syncs the content back into the canonical Secrets file and restores the symlink.
# ------------------------------------------------------------------------------

# region Init
setopt NO_UNSET EXTENDED_GLOB
WATCH_DIR="/home/curtis/.gemini/config"
WATCH_FILE="config.json"
LIVE_PATH="$WATCH_DIR/$WATCH_FILE"
SECRETS_PATH="/home/curtis/Obsidian/Secrets/Antigravity/Global/config.json"
print -P "\n%K{green}%F{black} ANTIGRAVITY CONFIG WATCHER %k%f\n"
print -P "%F{cyan}ℹ Watching $WATCH_DIR for changes to $WATCH_FILE...%f\n"
# endregion

# ------------------------------------------------------------------------------
# 1. Functions
# ------------------------------------------------------------------------------

# Purpose: Define sync and symlink restoration logic.

# region 1. Functions
sync_and_relink() {
    print -P "\n%F{yellow}⚡ Change detected in $WATCH_FILE%f"

    # Wait briefly to ensure Antigravity has finished writing
    sleep 1

    # Only act if the live file is a regular file (symlink was broken by Antigravity)
    if [[ -L "$LIVE_PATH" ]]; then
        print -P "%F{cyan}ℹ Symlink is still intact. No action needed.%f\n"
        return
    fi

    if [[ ! -f "$LIVE_PATH" ]]; then
        print -P "%F{red}⚠ $WATCH_FILE not found after event. Skipping.%f\n"
        return
    fi

    print -P "%F{cyan}ℹ Syncing new content to Secrets...%f"
    cp "$LIVE_PATH" "$SECRETS_PATH"

    print -P "%F{cyan}ℹ Restoring symlink...%f"
    rm -f "$LIVE_PATH"
    ln -sf "$SECRETS_PATH" "$LIVE_PATH"

    print -P "%F{green}✔ Symlink restored. Secrets file is canonical.%f\n"
}
# endregion

# ------------------------------------------------------------------------------
# 2. Watch Loop
# ------------------------------------------------------------------------------

# Purpose: Block on inotifywait and call sync on each relevant event.

# region 2. Watch Loop
LAST_SYNC=0
while CHANGED_FILE=$(inotifywait -q -e close_write -e moved_to --format "%f" "$WATCH_DIR" 2>/dev/null); do
    [[ "$CHANGED_FILE" != "$WATCH_FILE" ]] && continue

    # Debounce: ignore events within 3 seconds of last sync
    NOW=$(date +%s)
    if (( NOW - LAST_SYNC < 3 )); then
        continue
    fi
    LAST_SYNC=$NOW

    sync_and_relink
done
# endregion
