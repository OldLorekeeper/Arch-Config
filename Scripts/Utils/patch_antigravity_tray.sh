#!/bin/bash
# Extracts Antigravity ASAR, patches tray.js to use the symbolic trayTemplate on Linux, and repacks it.

if [ ! -f /opt/Antigravity/resources/app.asar ]; then
    exit 0
fi

cd /tmp
rm -rf patch_antigrav_asar
/usr/bin/asar extract /opt/Antigravity/resources/app.asar patch_antigrav_asar

# Inject the custom PNGs
cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/trayTemplate.png patch_antigrav_asar/trayTemplate.png
cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/trayTemplate@2x.png patch_antigrav_asar/trayTemplate@2x.png

# Patch the JS code so Linux loads trayTemplate.png instead of the full-colour icon.png
sed -i "s/(0, utils_1.isMacOS)() ? 'trayTemplate.png' : 'icon.png'/'trayTemplate.png'/g" patch_antigrav_asar/dist/tray.js

/usr/bin/asar pack patch_antigrav_asar /opt/Antigravity/resources/app.asar
rm -rf patch_antigrav_asar
