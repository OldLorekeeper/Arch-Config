#!/bin/bash
echo "Deploying Antigravity Icon Hooks..."

sudo sh -c "cat << 'INNEREOF' > /etc/pacman.d/hooks/antigravity-icon.hook
[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = papirus-icon-theme

[Action]
Description = Applying custom Antigravity symbolic icons to Papirus...
When = PostTransaction
Exec = /bin/sh -c 'cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-symbolic.svg && cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-ide-symbolic.svg'
INNEREOF"

sudo sh -c "cat << 'INNEREOF' > /etc/pacman.d/hooks/antigravity-tray.hook
[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = antigravity

[Action]
Description = Patching Antigravity internal tray icons...
When = PostTransaction
Exec = /home/curtis/Obsidian/Arch-Config/Scripts/Utils/patch_antigravity_tray.sh
INNEREOF"

echo "Running physical deployments..."
sudo cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-symbolic.svg
sudo cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-ide-symbolic.svg
sudo /home/curtis/Obsidian/Arch-Config/Scripts/Utils/patch_antigravity_tray.sh

echo "Refreshing caches..."
sudo gtk-update-icon-cache -f /usr/share/icons/Papirus
rm -f ~/.cache/icon-cache.kcache ~/.cache/plasma_theme_*.kcache

echo "Done! Please restart the Antigravity application, and optionally restart Plasma to see toolbar changes."
