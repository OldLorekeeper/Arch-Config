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

def stage_milestone(stage_num: int, total_stages: int, title: str):
    server.shell(
        name=f"[Stage {stage_num}/{total_stages}] {title}",
        commands=[
            f"printf '\\n\\033[1;34m====================================================================\\033[0m\\n' && "
            f"printf '\\033[1;32m==> [STAGE {stage_num}/{total_stages}] {title.upper()}\\033[0m\\n' && "
            f"printf '\\033[1;34m====================================================================\\033[0m\\n\\n'"
        ],
    )

server.shell(
    name=f"Starting deployment for {profile.upper()} profile ({target_user})",
    commands=[f"echo '==> Deploying {profile} profile for user {target_user}'"],
)

# 1. Base Configuration (Locale, Hosts, Makepkg, Pacman)
stage_milestone(1, 8, "Base System, Locales & Repositories")
import System.common.base

# 2. Users, Groups, and Sudoers
stage_milestone(2, 8, "User Accounts, Groups & Sudo Policies")
import System.common.users

# 3. Network, iwd, Dispatchers
stage_milestone(3, 8, "Network, Wi-Fi Backend & Dispatchers")
import System.common.network

# 4. Common Packages (Pacman, Yay, AUR)
stage_milestone(4, 8, "Core Packages & AUR Helper")
import System.common.packages

# 5. Kernel, Boot, Sysctl, ZRAM
stage_milestone(5, 8, "Kernel, Bootloader, Sysctl & ZRAM")
import System.common.kernel_boot

# 6. Theming, Dotfiles, Antigravity Sync, KWin
stage_milestone(6, 8, "Desktop Theming, Dotfiles & Plasma Assets")
import System.common.theming

# 7. Pacman Transaction Hooks
stage_milestone(7, 8, "Pacman Transaction Hooks")
import System.common.hooks

# 8. Profile-Specific Hardware Logic
stage_milestone(8, 8, f"Hardware Profile Optimisations ({profile.upper()})")
if profile == "desktop":
    import System.profiles.desktop
elif profile == "laptop":
    import System.profiles.laptop
else:
    raise ValueError(f"Unknown DEVICE_PROFILE: {profile}")

# 9. Final Regeneration (mkinitcpio & GRUB)
server.shell(
    name="[Completion] Regenerate initramfs and GRUB config",
    commands=[
        "mkinitcpio -P",
        "grub-mkconfig -o /boot/grub/grub.cfg",
    ],
)

# 10. Clean Up Sensitive Installation Variables and Temporary Sudo Rules
server.shell(
    name="[Completion] Clean up temporary installation variables and temporary sudo rules",
    commands=[
        "rm -f /install_vars.json /install_vars.zsh 2>/dev/null || true",
        "rm -f /etc/sudoers.d/zz_temp_yay /etc/sudoers.d/99_*_temp_yay 2>/dev/null || true",
    ],
)

