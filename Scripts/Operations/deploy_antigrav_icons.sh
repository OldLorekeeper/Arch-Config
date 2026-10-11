#!/bin/bash
echo "Deploying Antigravity Icon Hooks..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

sudo -A -v

sudo -A sh -c "cat << INNEREOF > /etc/pacman.d/hooks/antigravity-icon.hook
[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = papirus-icon-theme

[Action]
Description = Applying custom Antigravity icons to Papirus...
When = PostTransaction
Exec = /bin/sh -c 'cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-symbolic.svg && cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-ide-symbolic.svg && cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/22x22/panel/antigravity.svg && cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/24x24/panel/antigravity.svg && cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/22x22/panel/antigravity-symbolic.svg && cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/24x24/panel/antigravity-symbolic.svg && cp $REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-ide.svg /usr/share/icons/Papirus/64x64/apps/antigravity-ide.svg'
INNEREOF"

sudo -A sh -c "cat << INNEREOF > /etc/pacman.d/hooks/antigravity-tray.hook
[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = antigravity

[Action]
Description = Patching Antigravity internal tray icons...
When = PostTransaction
Exec = $REPO_DIR/Scripts/Utils/patch_antigravity_tray.sh
INNEREOF"

echo "Running physical deployments..."
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg" /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-symbolic.svg
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg" /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-ide-symbolic.svg
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg" /usr/share/icons/Papirus/22x22/panel/antigravity.svg
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg" /usr/share/icons/Papirus/24x24/panel/antigravity.svg
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg" /usr/share/icons/Papirus/22x22/panel/antigravity-symbolic.svg
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg" /usr/share/icons/Papirus/24x24/panel/antigravity-symbolic.svg
sudo -A cp "$REPO_DIR/Resources/Icons/GoogleWorkspace/google-antigravity-ide.svg" /usr/share/icons/Papirus/64x64/apps/antigravity-ide.svg
if [[ "$1" == "--patch-tray" ]]; then
    sudo -A "$REPO_DIR/Scripts/Utils/patch_antigravity_tray.sh"
fi

echo "Refreshing caches..."
sudo -A gtk-update-icon-cache -f /usr/share/icons/Papirus
rm -f ~/.cache/icon-cache.kcache ~/.cache/plasma_theme_*.kcache

echo "Done! Please restart the Antigravity application, and optionally restart Plasma to see toolbar changes."
