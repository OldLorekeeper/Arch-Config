#!/bin/zsh

cd "/home/curtis/Obsidian/Arch-Config/Secrets/Antigravity" || exit 1

echo "Renaming Global files..."
git mv Global/config.json Global/mcp_config.json
git mv Global/settings.json Global/config.json
git mv Global/persona.md Global/GEMINI.md

echo "Grouping Workspaces..."
mkdir -p Workspaces
git mv Arch Workspaces/Arch-Config
git mv Lorestone Workspaces/Lorestone

echo "Renaming Workspace Dotfiles..."
git mv Workspaces/Arch-Config/VSCode Workspaces/Arch-Config/.vscode
git mv Workspaces/Arch-Config/EditorConfig Workspaces/Arch-Config/.editorconfig
git mv Workspaces/Lorestone/git_exclude Workspaces/Lorestone/.git_exclude

echo "Renaming IDE Profile..."
git mv IDE IDE-Profile

echo "Done! The Secrets repository structure has been updated."
echo "Please run Scripts/Operations/antigravity_sync.zsh to apply the new symlinks to your system."
