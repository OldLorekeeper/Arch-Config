#!/bin/zsh
# ------------------------------------------------------------------------------
# Antigravity 2.0 Synchronisation
# Enforces the dual-tier symlink topology across the system.
# ------------------------------------------------------------------------------

# BEGIN
setopt ERR_EXIT NO_UNSET PIPE_FAIL EXTENDED_GLOB
TARGET_USER=${1:-user}
REPO_DIR="/home/$TARGET_USER/Obsidian/Arch-Config"
SECRETS_DIR="$REPO_DIR/Secrets"
print -P "\n%K{green}%F{black} ANTIGRAVITY SYNC %k%f\n"
# END

# ------------------------------------------------------------------------------
# 1. Workspace Configuration
# ------------------------------------------------------------------------------
# BEGIN
print -P "%K{blue}%F{black} 1. WORKSPACE CONFIGURATION %k%f\n"
print -P "%F{cyan}ℹ Enforcing local .agents sandboxing...%f\n"
mkdir -p "$REPO_DIR/.vscode"
rm -rf "$REPO_DIR/.agents"
ln -sfn "$SECRETS_DIR/Antigravity/Arch/.agents" "$REPO_DIR/.agents"
ln -sf "$SECRETS_DIR/Antigravity/Arch/GEMINI.md" "$REPO_DIR/GEMINI.md"
ln -sf "$SECRETS_DIR/Antigravity/Arch/VSCode" "$REPO_DIR/.vscode"
ln -sf "$SECRETS_DIR/Antigravity/Arch/EditorConfig" "$REPO_DIR/.editorconfig"
# END

# ------------------------------------------------------------------------------
# 2. Antigravity Global Environment
# ------------------------------------------------------------------------------
# BEGIN
print -P "\n%K{blue}%F{black} 2. GLOBAL ENVIRONMENT %k%f\n"
print -P "%F{cyan}ℹ Enforcing global ~/.gemini logic...%f\n"
mkdir -p "/home/$TARGET_USER/.gemini/config"
mkdir -p "/home/$TARGET_USER/.gemini/antigravity-cli"
mkdir -p "/home/$TARGET_USER/.antigravity-ide"

[[ -f "$SECRETS_DIR/Antigravity/Global/config.json" ]] && ln -sf "$SECRETS_DIR/Antigravity/Global/config.json" "/home/$TARGET_USER/.gemini/config/mcp_config.json"
[[ -f "$SECRETS_DIR/Antigravity/Global/config.json" ]] && ln -sf "$SECRETS_DIR/Antigravity/Global/config.json" "/home/$TARGET_USER/.gemini/antigravity-cli/mcp_config.json"
[[ -f "$SECRETS_DIR/Antigravity/Global/persona.md" ]] && ln -sf "$SECRETS_DIR/Antigravity/Global/persona.md" "/home/$TARGET_USER/.gemini/GEMINI.md"
[[ -f "$SECRETS_DIR/Antigravity/Global/persona.md" ]] && ln -sf "$SECRETS_DIR/Antigravity/Global/persona.md" "/home/$TARGET_USER/.gemini/antigravity-cli/GEMINI.md"
[[ -f "$SECRETS_DIR/Antigravity/Global/argv.json" ]] && ln -sf "$SECRETS_DIR/Antigravity/Global/argv.json" "/home/$TARGET_USER/.antigravity-ide/argv.json"
[[ -f "$SECRETS_DIR/Antigravity/Global/argv.json" ]] && ln -sf "$SECRETS_DIR/Antigravity/Global/argv.json" "/home/$TARGET_USER/.gemini/antigravity-cli/argv.json"
# END

# ------------------------------------------------------------------------------
# 3. User Desktop Profile
# ------------------------------------------------------------------------------
# BEGIN
print -P "\n%K{blue}%F{black} 3. USER DESKTOP PROFILE %k%f\n"
print -P "%F{cyan}ℹ Enforcing local desktop logic...%f\n"
IDE_SECRETS="$SECRETS_DIR/Antigravity/IDE"
if [[ -d "$IDE_SECRETS" ]]; then
    mkdir -p "/home/$TARGET_USER/.config/antigravity-ide"
    rm -rf "/home/$TARGET_USER/.config/antigravity-ide/User" 2>/dev/null
    ln -sf "$IDE_SECRETS/User" "/home/$TARGET_USER/.config/antigravity-ide/User"
fi
# END

# ------------------------------------------------------------------------------
# 4. Lorestone Workspace
# ------------------------------------------------------------------------------
# BEGIN
print -P "\n%K{blue}%F{black} 4. LORESTONE WORKSPACE %k%f\n"
print -P "%F{cyan}ℹ Enforcing Lorestone local sandboxing...%f\n"
LORESTONE_DIR="/home/$TARGET_USER/Obsidian/Lorestone"
if [[ -d "$LORESTONE_DIR" ]]; then
    rm -rf "$LORESTONE_DIR/.agents"
    ln -sfn "$SECRETS_DIR/Antigravity/Lorestone/.agents" "$LORESTONE_DIR/.agents"
    ln -sf "$SECRETS_DIR/Antigravity/Lorestone/GEMINI.md" "$LORESTONE_DIR/GEMINI.md"
    ln -sf "$SECRETS_DIR/Antigravity/Lorestone/git_exclude" "$LORESTONE_DIR/.git/info/exclude"
fi
# END

# ------------------------------------------------------------------------------
# 5. Operations Scripts
# ------------------------------------------------------------------------------
# BEGIN
print -P "\n%K{blue}%F{black} 5. OPERATIONS SCRIPTS %k%f\n"
print -P "%F{cyan}ℹ Symlinking Scripts from Secrets...%f\n"
ln -sf "$SECRETS_DIR/Scripts/repo_sync.zsh" "$REPO_DIR/Scripts/Operations/repo_sync.zsh"
# END

# ------------------------------------------------------------------------------
# End
# ------------------------------------------------------------------------------
# BEGIN
print -P "\n%K{green}%F{black} SYNC COMPLETE %k%f\n"
# END
