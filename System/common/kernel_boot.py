from io import StringIO
from pathlib import Path
from pyinfra.operations import files, server, systemd
from System.config import get_config

cfg = get_config()
profile = cfg["DEVICE_PROFILE"]
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# 1. Environment Variables
files.line(
    name="Enable Wayland in Proton",
    path="/etc/environment",
    line="PROTON_ENABLE_WAYLAND=1",
)

# 2. IO Scheduler
files.put(
    name="Set NVMe scheduler to none",
    dest="/etc/udev/rules.d/60-iosched.rules",
    src=str(TEMPLATES_DIR / "udev" / "60-iosched.rules"),
)

# 3. Sysctl Optimizations
files.put(
    name="Configure swappiness sysctl",
    dest="/etc/sysctl.d/99-swappiness.conf",
    src=str(TEMPLATES_DIR / "sysctl" / "99-swappiness.conf"),
)

files.put(
    name="Configure TCP BBR sysctl",
    dest="/etc/sysctl.d/99-bbr.conf",
    src=str(TEMPLATES_DIR / "sysctl" / "99-bbr.conf"),
)

files.put(
    name="Configure Tailscale IP forwarding sysctl",
    dest="/etc/sysctl.d/99-tailscale.conf",
    src=str(TEMPLATES_DIR / "sysctl" / "99-tailscale.conf"),
)

# Apply sysctl settings immediately
server.shell(
    name="Apply sysctl settings",
    commands=["sysctl --system"],
)

# 4. ZRAM Generator
zram_src = "zram_desktop.conf" if profile == "desktop" else "zram_laptop.conf"
files.put(
    name="Configure ZRAM generator",
    dest="/etc/systemd/zram-generator.conf",
    src=str(TEMPLATES_DIR / zram_src),
)

# 5. Btrfs Maintenance Timers
files.put(
    name="Install btrfs-balance service",
    dest="/etc/systemd/system/btrfs-balance.service",
    src=str(TEMPLATES_DIR / "systemd" / "btrfs-balance.service"),
)

files.put(
    name="Install btrfs-balance timer",
    dest="/etc/systemd/system/btrfs-balance.timer",
    src=str(TEMPLATES_DIR / "systemd" / "btrfs-balance.timer"),
)

# 6. grub-btrfsd & GRUB Bootloader
server.shell(
    name="Ensure GRUB EFI bootloader is installed",
    commands=[
        """if [[ ! -f /efi/EFI/GRUB/grubx64.efi ]]; then
            grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=GRUB
        fi"""
    ],
)

files.directory(
    name="Ensure grub-btrfsd service drop-in directory exists",
    path="/etc/systemd/system/grub-btrfsd.service.d",
    present=True,
)

files.put(
    name="Configure grub-btrfsd timeshift drop-in override",
    dest="/etc/systemd/system/grub-btrfsd.service.d/override.conf",
    src=StringIO("[Service]\nExecStart=\nExecStart=/usr/bin/grub-btrfsd --syslog --timeshift-auto\n"),
)

files.file(
    name="Remove obsolete full-file grub-btrfsd service",
    path="/etc/systemd/system/grub-btrfsd.service",
    present=False,
)

systemd.service(
    name="Enable grub-btrfsd daemon",
    service="grub-btrfsd",
    enabled=True,
)

# 7. Common Timers & Services
for timer in ["btrfs-balance.timer", "btrfs-scrub@-.timer", "timeshift-hourly.timer"]:
    systemd.service(
        name=f"Enable maintenance timer {timer}",
        service=timer,
        enabled=True,
    )
