#!/bin/bash
# Extracts Antigravity ASAR, patches tray.js to use the symbolic trayTemplate on Linux, and repacks it.

if [ ! -f /opt/Antigravity/resources/app.asar ]; then
    echo "Error: /opt/Antigravity/resources/app.asar not found."
    exit 1
fi

if ! command -v asar &> /dev/null; then
    echo "Error: 'asar' is not installed. Please run 'sudo npm install -g @electron/asar' or install it via pacman."
    exit 1
fi

# Kill Antigravity if it is running to prevent EBUSY locks
if pgrep -x "antigravity" > /dev/null; then
    echo "Closing Antigravity to prevent file locks..."
    killall antigravity
    sleep 2
fi

cd /tmp
rm -rf patch_antigrav_asar
echo "Extracting ASAR..."
asar extract /opt/Antigravity/resources/app.asar patch_antigrav_asar

if [ ! -d "patch_antigrav_asar" ]; then
    echo "Error: ASAR extraction failed!"
    exit 1
fi

echo "Injecting PNGs..."
cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/trayTemplate.png patch_antigrav_asar/trayTemplate.png
cp /home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/trayTemplate@2x.png patch_antigrav_asar/trayTemplate@2x.png

echo "Patching JS..."
sed -i "s/(0, utils_1.isMacOS)() ? 'trayTemplate.png' : 'icon.png'/'trayTemplate.png'/g" patch_antigrav_asar/dist/tray.js

echo "Repacking ASAR..."
asar pack patch_antigrav_asar /opt/Antigravity/resources/app.asar

if [ $? -eq 0 ]; then
    echo "Success! ASAR has been patched."
else
    echo "Error: ASAR pack failed. Check permissions or locks."
fi

rm -rf patch_antigrav_asar
