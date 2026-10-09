from io import StringIO
from pathlib import Path
from pyinfra.operations import files
from System.config import get_config

cfg = get_config()
profile = cfg["DEVICE_PROFILE"]
repo_dir = cfg["REPO_DIR"]

files.directory(
    name="Ensure pacman hooks directory exists",
    path="/etc/pacman.d/hooks",
    present=True,
)

# 1. Initramfs Rebuild Hook
ucode_pkg = "amd-ucode" if profile == "desktop" else "intel-ucode"
hook_98 = f"""[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = {ucode_pkg}
Target = btrfs-progs
Target = mkinitcpio-firmware
Target = linux-cachyos-headers

[Action]
Description = Rebuilding initramfs...
When = PostTransaction
Exec = /usr/bin/mkinitcpio -P
"""
files.put(
    name="Install 98-rebuild-initramfs.hook",
    dest="/etc/pacman.d/hooks/98-rebuild-initramfs.hook",
    src=StringIO(hook_98),
)

# 2. GRUB Update Hook
hook_99 = """[Trigger]
Operation = Install
Operation = Upgrade
Operation = Remove
Type = Package
Target = linux-cachyos

[Action]
Description = Updating GRUB...
When = PostTransaction
Exec = /usr/bin/grub-mkconfig -o /boot/grub/grub.cfg
"""
files.put(
    name="Install 99-update-grub.hook",
    dest="/etc/pacman.d/hooks/99-update-grub.hook",
    src=StringIO(hook_99),
)

# 3. novelWriter Icon Hook
hook_novel = f"""[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = novelwriter

[Action]
Description = Applying custom Papirus icon to novelWriter internal assets...
When = PostTransaction
Exec = /bin/sh -c 'cp {repo_dir}/Resources/Icons/novelWriter/novelwriter.svg /usr/lib/python*/site-packages/novelwriter/assets/icons/novelwriter.svg'
"""
files.put(
    name="Install novelwriter-icon.hook",
    dest="/etc/pacman.d/hooks/novelwriter-icon.hook",
    src=StringIO(hook_novel),
)

# 4. Antigravity Papirus Icons Hook
hook_antigrav_icon = f"""[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = papirus-icon-theme

[Action]
Description = Applying custom Antigravity symbolic/panel icons to Papirus...
When = PostTransaction
Exec = /bin/sh -c "cp {repo_dir}/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-symbolic.svg && cp {repo_dir}/Resources/Icons/GoogleWorkspace/google-antigravity-symbolic.svg /usr/share/icons/Papirus/16x16/symbolic/apps/antigravity-ide-symbolic.svg && cp {repo_dir}/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/22x22/panel/antigravity.svg && cp {repo_dir}/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/24x24/panel/antigravity.svg && cp {repo_dir}/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/22x22/panel/antigravity-symbolic.svg && cp {repo_dir}/Resources/Icons/GoogleWorkspace/google-antigravity-panel.svg /usr/share/icons/Papirus/24x24/panel/antigravity-symbolic.svg"
"""
files.put(
    name="Install antigravity-icon.hook",
    dest="/etc/pacman.d/hooks/antigravity-icon.hook",
    src=StringIO(hook_antigrav_icon),
)

# 5. Antigravity Tray ASAR Patch Hook
hook_antigrav_tray = f"""[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = antigravity

[Action]
Description = Patching Antigravity internal tray icons...
When = PostTransaction
Exec = {repo_dir}/Scripts/Utils/patch_antigravity_tray.sh
"""
files.put(
    name="Install antigravity-tray.hook",
    dest="/etc/pacman.d/hooks/antigravity-tray.hook",
    src=StringIO(hook_antigrav_tray),
)
