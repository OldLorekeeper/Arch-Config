from pyinfra.operations import pacman, server
from System.config import get_config

cfg = get_config()
target_user = cfg["TARGET_USER"]

# 1. Common Official Packages
COMMON_PACKAGES = [
    "base", "base-devel", "bluez", "bluez-utils", "btrfs-progs",
    "cachyos-keyring", "cachyos-mirrorlist", "cachyos-settings",
    "efibootmgr", "git", "git-lfs", "grub", "grub-btrfs", "linux-cachyos",
    "linux-cachyos-headers", "linux-firmware", "networkmanager", "networkmanager-qt",
    "openssh", "pacman-contrib", "reflector", "sudo", "timeshift", "vim",
    "wireless-regdb", "zram-generator", "zsh",
    "ark", "bluedevil", "dolphin", "kate", "kinfocenter", "konsole", "kscreen",
    "kwallet-pam", "mesa", "partitionmanager", "pipewire", "pipewire-alsa",
    "pipewire-pulse", "plasma-desktop", "plasma-disks", "plasma-login-manager",
    "plasma-nm", "plasma-pa", "plasma-systemmonitor", "powerdevil", "spectacle", "wireplumber",
    "flatpak-kcm", "kde-gtk-config", "kdeplasma-addons", "krdp", "kwrited",
    "oxygen", "oxygen-sounds", "plasma-browser-integration", "plasma-firewall",
    "plasma-thunderbolt", "plasma-vault", "plasma-welcome", "print-manager",
    "7zip", "bash-language-server", "chromium", "cmake", "cmake-extras", "cpupower",
    "cups", "dkms", "dnsmasq", "dosfstools", "edk2-ovmf", "ethtool", "extra-cmake-modules", "ghostscript",
    "fastfetch", "fwupd", "gamemode", "gamescope", "gwenview", "hunspell-en_gb",
    "inkscape", "isoimagewriter", "iw", "iwd", "jq", "kio-admin", "kio-gdrive", "lib32-gamemode",
    "lib32-gnutls", "libva-utils", "libvirt", "lz4", "mkinitcpio-firmware",
    "npm", "nss-mdns", "obsidian", "papirus-icon-theme", "protontricks", "protonup-qt",
    "qemu-desktop", "realtime-privileges", "steam", "tailscale", "transmission-cli", "uv", "vdpauinfo",
    "virt-manager", "vlc", "vlc-plugin-ffmpeg", "vulkan-headers", "wayland-protocols",
    "wine-staging", "wine-mono", "winetricks", "xpadneo-dkms", "inotify-tools"
]

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
