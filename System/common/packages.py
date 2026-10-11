import re
import subprocess
from pyinfra.operations import pacman, server
from System.config import get_config

cfg = get_config()
target_user = cfg["TARGET_USER"]

def get_plasma_meta_packages(exclude=("discover",)):
    """
    Dynamically resolve upstream plasma-meta dependencies excluding unwanted packages
    (e.g. Discover), ensuring KDE Plasma components stay current with upstream.
    """
    try:
        out = subprocess.check_output(["pacman", "-Si", "plasma-meta"], text=True)
        match = re.search(r"Depends On\s*:\s*(.*?)(?:\n[A-Z]|\Z)", out, re.DOTALL)
        if match:
            deps = [re.split(r"[><=]", pkg.strip())[0] for pkg in match.group(1).split() if pkg.strip()]
            resolved = [d for d in deps if d not in exclude and d != "None"]
            if resolved:
                return resolved
    except Exception:
        pass
    # Safety fallback list if pacman database is offline or uninitialised
    return [
        "plasma-desktop", "plasma-login-manager", "plasma-nm", "plasma-pa",
        "powerdevil", "kscreen", "plasma-systemmonitor", "plasma-disks",
        "plasma-firewall", "plasma-thunderbolt", "plasma-vault", "plasma-welcome",
        "plasma-browser-integration", "print-manager", "flatpak-kcm", "kde-gtk-config",
        "kdeplasma-addons", "krdp", "kwrited", "spectacle", "kwallet-pam", "bluedevil",
        "kinfocenter", "oxygen", "oxygen-sounds"
    ]

# 1. Base System, Tools & Non-Plasma Applications
BASE_AND_APP_PACKAGES = [
    # System Base, Kernel & Storage
    "base", "base-devel", "btrfs-progs", "cachyos-keyring", "cachyos-mirrorlist",
    "cachyos-settings", "efibootmgr", "grub", "grub-btrfs", "linux-cachyos",
    "linux-cachyos-headers", "linux-firmware", "mkinitcpio-firmware", "sudo",
    "timeshift", "zram-generator",
    # Networking & Connectivity
    "bluez", "bluez-utils", "ethtool", "iw", "iwd", "networkmanager", "networkmanager-qt",
    "openssh", "reflector", "tailscale", "wireless-regdb",
    # Audio, Graphics & Media Framework
    "mesa", "pipewire", "pipewire-alsa", "pipewire-pulse", "wireplumber", "libva-utils",
    "vdpauinfo", "vulkan-headers", "wayland-protocols",
    # Shell, Development & Utilities
    "7zip", "bash-language-server", "cmake", "cmake-extras", "cpupower", "cups", "dkms",
    "dnsmasq", "dosfstools", "edk2-ovmf", "extra-cmake-modules", "fastfetch", "fwupd",
    "ghostscript", "git", "git-lfs", "hunspell-en_gb", "inotify-tools", "jq", "libvirt",
    "lz4", "npm", "nss-mdns", "pacman-contrib", "qemu-desktop", "realtime-privileges",
    "transmission-cli", "uv", "vim", "virt-manager", "zsh",
    # Gaming & Proton Stack
    "gamemode", "gamescope", "lib32-gamemode", "lib32-gnutls", "protontricks", "protonup-qt",
    "steam", "wine-staging", "wine-mono", "winetricks", "xpadneo-dkms",
    # Core User Applications & KDE Integration
    "ark", "chromium", "dolphin", "gwenview", "inkscape", "isoimagewriter", "kate",
    "kio-admin", "kio-gdrive", "konsole", "obsidian", "papirus-icon-theme",
    "partitionmanager", "vlc", "vlc-plugin-ffmpeg",
]

# Merge dynamically resolved plasma components with base and app packages (deduplicated)
COMMON_PACKAGES = list(dict.fromkeys(BASE_AND_APP_PACKAGES + get_plasma_meta_packages(exclude=("discover",))))

pacman.packages(
    name="Install common official packages",
    packages=COMMON_PACKAGES,
    present=True,
)

# 2. Temporary Sudoers Drop-in for Non-Interactive AUR Bootstrap & Installation
server.shell(
    name="Grant temporary non-interactive sudo for AUR build",
    commands=[
        f'echo "{target_user} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/zz_temp_yay',
        'chmod 0440 /etc/sudoers.d/zz_temp_yay',
    ],
)

# 3. Bootstrap yay AUR helper if missing
server.shell(
    name="Bootstrap yay AUR helper if not installed",
    commands=[
        f"""if ! command -v yay &>/dev/null; then
            cd /home/{target_user}
            sudo -u {target_user} git clone https://aur.archlinux.org/yay.git
            cd yay
            sudo -u {target_user} makepkg -si --noconfirm
            cd ..
            rm -rf yay
        fi"""
    ],
)

# 4. Common AUR Packages
COMMON_AUR_PACKAGES = [
    "antigravity", "antigravity-cli", "antigravity-ide", "darkly-bin", "geekbench",
    "google-chrome", "konsave", "kwin-effects-better-blur-dx", "novelwriter-bin", "papirus-folders",
    "plasma6-applets-panel-colorizer", "timeshift-systemd-timer"
]

server.shell(
    name="Install common AUR packages via yay",
    commands=[
        f"sudo -u {target_user} yay -S --needed --noconfirm --sudoloop=false {' '.join(COMMON_AUR_PACKAGES)}"
    ],
)

# 5. Purge Discover (KDE is installed modularly without plasma-meta)
server.shell(
    name="Purge discover if present",
    commands=[
        "pacman -Qi discover &>/dev/null && pacman -Rns --noconfirm discover || true",
    ],
)
