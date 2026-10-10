from io import StringIO
from pathlib import Path
from pyinfra.operations import files, pacman, server, systemd
from System.config import get_config

cfg = get_config()
target_user = cfg["TARGET_USER"]
repo_dir = cfg["REPO_DIR"]
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# 1. Desktop Packages
DESKTOP_PACKAGES = [
    "amd-ucode", "cachyos-v4-mirrorlist", "scx-scheds", "scx-tools", "vulkan-radeon",
    "lib32-vulkan-radeon", "rocm-hip-runtime", "rocm-opencl-runtime",
    "ffmpeg", "jellyfin-server", "jellyfin-web", "lutris", "solaar", "yt-dlp",
]

pacman.packages(
    name="Install desktop official packages",
    packages=DESKTOP_PACKAGES,
    present=True,
)

DESKTOP_AUR_PACKAGES = [
    "lact", "prowlarr-bin", "radarr-bin", "seerr", "sonarr-bin", "sunshine", "bun-bin", "valkey"
]

server.shell(
    name="Install desktop AUR packages via yay",
    commands=[
        f"sudo -u {target_user} yay -S --needed --noconfirm --sudoloop=false {' '.join(DESKTOP_AUR_PACKAGES)}"
    ],
)

# 2. Graphics & Environment
files.line(
    name="Set AMD VAAPI driver",
    path="/etc/environment",
    line="LIBVA_DRIVER_NAME=radeonsi",
)
files.line(
    name="Set AMD VDPAU driver",
    path="/etc/environment",
    line="VDPAU_DRIVER=radeonsi",
)

# 3. Hardware & Power Management
files.put(
    name="Install AMD XHCI power fix udev rule",
    dest="/etc/udev/rules.d/99-xhci-fix.rules",
    src=str(TEMPLATES_DIR / "udev" / "99-xhci-fix.rules"),
)

files.line(
    name="Disable ASPM on MediaTek Wi-Fi (mt7921e)",
    path="/etc/modprobe.d/mt7921e.conf",
    line="options mt7921e disable_aspm=Y",
)

files.put(
    name="Configure AMD EPP performance profile",
    dest="/etc/tmpfiles.d/amd-epp.conf",
    src=StringIO("w /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference - - - - performance\n"),
)

files.put(
    name="Install Solaar uinput udev permissions",
    dest="/etc/udev/rules.d/42-solaar-uinput.rules",
    src=str(TEMPLATES_DIR / "udev" / "42-solaar-uinput.rules"),
)

# 4. LACT Fan & Power Daemon
files.directory(
    name="Ensure /etc/lact directory exists",
    path="/etc/lact",
    present=True,
)
if not Path("/etc/lact/config.yaml").exists():
    files.put(
        name="Install default LACT configuration",
        dest="/etc/lact/config.yaml",
        src=str(TEMPLATES_DIR / "lact.yaml"),
    )

systemd.service(
    name="Enable lactd daemon",
    service="lactd",
    enabled=True,
)

# 5. Kernel & Boot Configuration
edid_flag = ""
edid_enabled = str(cfg.get("EDID_ENABLE", "")).lower() in ("true", "yes", "y", "1")
if edid_enabled:
    edid_src = f"{repo_dir}/Resources/Sunshine/custom_sunshine.bin"
    if Path(edid_src).exists():
        files.directory(
            name="Ensure firmware EDID directory exists",
            path="/usr/lib/firmware/edid",
            present=True,
        )
        files.put(
            name="Copy custom Sunshine EDID binary",
            dest="/usr/lib/firmware/edid/custom_sunshine.bin",
            src=edid_src,
        )
        files.line(
            name="Include custom EDID in mkinitcpio FILES",
            path="/etc/mkinitcpio.conf",
            line=r"^FILES=.*",
            replace="FILES=(/usr/lib/firmware/edid/custom_sunshine.bin)",
        )
        mon_port = cfg.get("MONITOR_PORT", "") or "DP-2"
        if mon_port:
            edid_flag = f" drm.edid_firmware={mon_port}:edid/custom_sunshine.bin"

grub_cmdline = f"split_lock_detect=off loglevel=3 quiet amdgpu.ppfeaturemask=0xffffffff video=3440x1440@60{edid_flag} mitigations=off amd_pstate=active"

files.line(
    name="Configure GRUB kernel command line for Desktop",
    path="/etc/default/grub",
    line=r"^GRUB_CMDLINE_LINUX_DEFAULT=.*",
    replace=f'GRUB_CMDLINE_LINUX_DEFAULT="{grub_cmdline}"',
)
files.line(
    name="Set GRUB timeout to 2s",
    path="/etc/default/grub",
    line=r"^GRUB_TIMEOUT=.*",
    replace="GRUB_TIMEOUT=2",
)

files.line(
    name="Set mkinitcpio modules for AMD",
    path="/etc/mkinitcpio.conf",
    line=r"^MODULES=.*",
    replace="MODULES=(amdgpu nvme)",
)
files.line(
    name="Set mkinitcpio compression to lz4",
    path="/etc/mkinitcpio.conf",
    line=r"^COMPRESSION=.*",
    replace='COMPRESSION="lz4"',
)

# 6. Sunshine Game Streaming
for script in [
    "sunshine_gpu_boost.zsh", "sunshine_hdr.zsh", "sunshine_res.zsh",
    "sunshine_laptop.zsh", "sunshine_configure.zsh", "sunshine_pixel.zsh"
]:
    script_path = Path(repo_dir) / "Scripts" / "Sunshine" / script
    if script_path.exists():
        bin_name = script.removesuffix(".zsh")
        files.link(
            name=f"Symlink Sunshine helper {bin_name} to /usr/local/bin",
            path=f"/usr/local/bin/{bin_name}",
            target=str(script_path),
            symbolic=True,
        )

sunshine_icons_script = f"""#!/bin/bash
shopt -s nullglob
cp "{repo_dir}/Resources/Icons/Sunshine"/*.svg "/usr/share/sunshine/web/images/" 2>/dev/null || true
cp "{repo_dir}/Resources/Icons/Sunshine"/*.png "/usr/share/sunshine/web/images/" 2>/dev/null || true
SUN_BIN=$(readlink -f $(command -v sunshine 2>/dev/null) 2>/dev/null)
[[ -n "$SUN_BIN" ]] && setcap cap_sys_admin+p "$SUN_BIN" || true
"""
files.put(
    name="Install replace-sunshine-icons.sh",
    dest="/usr/local/bin/replace-sunshine-icons.sh",
    src=StringIO(sunshine_icons_script),
    mode="0755",
)

files.put(
    name="Install sunshine-icons pacman hook",
    dest="/etc/pacman.d/hooks/sunshine-icons.hook",
    src=StringIO(f"""[Trigger]
Operation = Install
Operation = Upgrade
Type = Package
Target = sunshine

[Action]
Description = Replacing Sunshine tray icons...
When = PostTransaction
Exec = /usr/local/bin/replace-sunshine-icons.sh
"""),
)

files.put(
    name="Configure NOPASSWD for sunshine_gpu_boost",
    dest="/etc/sudoers.d/90-sunshine-boost",
    src=StringIO(f"{target_user} ALL=(ALL) NOPASSWD: /usr/local/bin/sunshine_gpu_boost\n"),
    mode="0440",
)

files.file(
    name="Enable systemd linger for user",
    path=f"/var/lib/systemd/linger/{target_user}",
    touch=True,
)

files.directory(
    name="Ensure user systemd autostart directory exists",
    path=f"/home/{target_user}/.config/systemd/user/default.target.wants",
    user=target_user,
    group=target_user,
    present=True,
)
files.link(
    name="Enable Sunshine user service",
    path=f"/home/{target_user}/.config/systemd/user/default.target.wants/app-dev.lizardbyte.app.Sunshine.service",
    target="/usr/lib/systemd/user/app-dev.lizardbyte.app.Sunshine.service",
    symbolic=True,
    user=target_user,
)

# Sunshine QoS via nftables
files.put(
    name="Configure Sunshine QoS nftables rules",
    dest="/etc/nftables.conf",
    src=str(TEMPLATES_DIR / "nftables.conf"),
)
systemd.service(
    name="Enable nftables service",
    service="nftables",
    enabled=True,
)

# 7. Media Server & Arr Stack
files.put(
    name="Configure Jellyfin transcode shm tmpfiles",
    dest="/etc/tmpfiles.d/jellyfin-transcode.conf",
    src=StringIO("d /dev/shm/jellyfin 0755 jellyfin jellyfin -\n"),
)

files.directory(
    name="Ensure /var/lib/jellyfin directory exists",
    path="/var/lib/jellyfin",
    present=True,
)

server.shell(
    name="Ensure jellyfin user permissions and nocow attribute",
    commands=[
        "chattr +C /var/lib/jellyfin 2>/dev/null || true",
        "id -u jellyfin &>/dev/null && usermod -aG render,video jellyfin || true",
    ],
)

server.shell(
    name="Configure media directories and permissions if /mnt/Media mounted",
    commands=[
        f"""if mountpoint -q /mnt/Media; then
            mkdir -p /mnt/Media/{{Films,TV,Music,Downloads/{{radarr,sonarr,transmission}}}}
            chattr +C /mnt/Media/Downloads 2>/dev/null || true
            chown -R {target_user}:media /mnt/Media
            chmod -R 775 /mnt/Media
            setfacl -R -m g:media:rwX /mnt/Media 2>/dev/null || true
            setfacl -R -m d:g:media:rwX /mnt/Media 2>/dev/null || true
        fi"""
    ],
)

for svc in ["sonarr", "radarr", "prowlarr", "transmission-daemon"]:
    files.directory(
        name=f"Ensure systemd drop-in dir for {svc}",
        path=f"/etc/systemd/system/{svc}.service.d",
        present=True,
    )
    files.put(
        name=f"Install media mount requirement for {svc}",
        dest=f"/etc/systemd/system/{svc}.service.d/media-mount.conf",
        src=str(TEMPLATES_DIR / "systemd" / "media-mount.conf"),
    )
    files.put(
        name=f"Install permissions umask for {svc}",
        dest=f"/etc/systemd/system/{svc}.service.d/permissions.conf",
        src=str(TEMPLATES_DIR / "systemd" / "permissions.conf"),
    )

server.shell(
    name="Add media stack service users to media group",
    commands=[
        "for u in sonarr radarr prowlarr transmission; do id -u $u &>/dev/null && usermod -aG media $u || true; done"
    ],
)

# Media Optimizer Systemd Service & Timer
files.link(
    name="Symlink media_optimizer script",
    path="/usr/local/bin/media_optimizer",
    target=f"{repo_dir}/Scripts/Utils/media_optimizer.zsh",
    symbolic=True,
)

files.put(
    name="Install media-optimizer.service",
    dest="/etc/systemd/system/media-optimizer.service",
    src=str(TEMPLATES_DIR / "systemd" / "media-optimizer.service"),
)

files.put(
    name="Install media-optimizer.timer",
    dest="/etc/systemd/system/media-optimizer.timer",
    src=str(TEMPLATES_DIR / "systemd" / "media-optimizer.timer"),
)

systemd.service(
    name="Enable media-optimizer.timer",
    service="media-optimizer.timer",
    enabled=True,
)

# Clean legacy cronjob if present
server.shell(
    name="Remove obsolete media_optimizer cronjob",
    commands=[
        f'sudo -u {target_user} bash -c \'crontab -l 2>/dev/null | grep -v "media_optimizer" | crontab - 2>/dev/null || true\''
    ],
)

for svc in ["jellyfin", "transmission-daemon", "sonarr", "radarr", "prowlarr", "seerr"]:
    systemd.service(
        name=f"Enable desktop media service {svc}",
        service=svc,
        enabled=True,
    )

if Path("/mnt/Media").is_mount():
    systemd.service(
        name="Enable btrfs scrub timer for /mnt/Media",
        service="btrfs-scrub@mnt-Media.timer",
        enabled=True,
    )

# 8. Trawl & Arrstack MCP
server.shell(
    name="Setup Trawl and arrstack-mcp repositories",
    commands=[
        f"""TRAWL_DIR="/home/{target_user}/Projects/Trawl"
        if [[ ! -d "$TRAWL_DIR" ]]; then
            sudo -u {target_user} git clone https://github.com/germondai/trawl "$TRAWL_DIR" || true
            if [[ -d "$TRAWL_DIR" ]]; then
                cd "$TRAWL_DIR"
                sudo -u {target_user} cp .env.example .env
                sudo -u {target_user} sed -i 's/MITM_PROXY_ENABLED=false/MITM_PROXY_ENABLED=true/g' .env
                sudo -u {target_user} sed -i "s|MITM_PROXY_CA_DIR=/data/proxy-ca|MITM_PROXY_CA_DIR=$TRAWL_DIR/proxy-ca|g" .env
                sudo -u {target_user} bun install || true
            fi
        fi

        ARRSTACK_DIR="/home/{target_user}/Projects/arrstack-mcp"
        if [[ ! -d "$ARRSTACK_DIR" ]]; then
            sudo -u {target_user} git clone https://github.com/ct4nk3r/arrstack-mcp.git "$ARRSTACK_DIR" || true
            if [[ -d "$ARRSTACK_DIR" ]]; then
                cd "$ARRSTACK_DIR"
                sudo -u {target_user} uv venv
                sudo -u {target_user} uv pip install -r requirements.txt "mcp<2.0.0" || true
            fi
        fi
        """
    ],
)

files.put(
    name="Install trawl user service unit",
    dest=f"/home/{target_user}/.config/systemd/user/trawl.service",
    src=str(TEMPLATES_DIR / "systemd" / "trawl.service"),
    user=target_user,
    group=target_user,
)
files.link(
    name="Enable trawl user service",
    path=f"/home/{target_user}/.config/systemd/user/default.target.wants/trawl.service",
    target=f"/home/{target_user}/.config/systemd/user/trawl.service",
    symbolic=True,
    user=target_user,
)

# 9. SCX Scheduler (scx_lavd)
files.directory(
    name="Ensure /etc/scx_loader exists",
    path="/etc/scx_loader",
    present=True,
)
files.put(
    name="Configure scx_lavd default scheduler",
    dest="/etc/scx_loader/config.toml",
    src=str(TEMPLATES_DIR / "scx_lavd.toml"),
)
systemd.service(
    name="Enable scx_loader daemon",
    service="scx_loader",
    enabled=True,
)
