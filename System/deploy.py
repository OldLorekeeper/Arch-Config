"""
Arch-Config Declarative System Deployer (pyinfra)
Orchestrates base configuration, security, users, packages, and profile-specific hardware logic.
"""
import sys
from pathlib import Path

# Ensure repository root is on sys.path so 'import System.*' works regardless of working directory
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pyinfra.operations import server
from System.config import get_config

cfg = get_config()
profile = cfg["DEVICE_PROFILE"]
target_user = cfg["TARGET_USER"]

server.shell(
    name=f"Starting deployment for {profile.upper()} profile ({target_user})",
    commands=[f"echo '==> Deploying {profile} profile for user {target_user}'"],
)

# 1. Base Configuration (Locale, Hosts, Makepkg, Pacman)
import System.common.base

# 2. Users, Groups, and Sudoers
import System.common.users

# 3. Network, iwd, Dispatchers
import System.common.network

# 4. Common Packages (Pacman, Yay, AUR)
import System.common.packages

# 5. Kernel, Boot, Sysctl, ZRAM
import System.common.kernel_boot

# 6. Theming, Dotfiles, Antigravity Sync, KWin
import System.common.theming

# 7. Pacman Transaction Hooks
import System.common.hooks

# 8. Profile-Specific Hardware Logic
if profile == "desktop":
    import System.profiles.desktop
elif profile == "laptop":
    import System.profiles.laptop
else:
    raise ValueError(f"Unknown DEVICE_PROFILE: {profile}")

# 9. Final Regeneration (mkinitcpio & GRUB)
server.shell(
    name="Regenerate initramfs and GRUB config",
    commands=[
        "mkinitcpio -P",
        "grub-mkconfig -o /boot/grub/grub.cfg",
    ],
)

# 10. Clean Up Sensitive Installation Variables
server.shell(
    name="Clean up temporary installation variables",
    commands=[
        "rm -f /install_vars.json /install_vars.zsh 2>/dev/null || true"
    ],
)

