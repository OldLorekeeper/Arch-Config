from io import StringIO
from pathlib import Path
from pyinfra.operations import files, pacman, server, systemd
from System.config import get_config

cfg = get_config()
target_user = cfg["TARGET_USER"]
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# 1. Laptop Packages
LAPTOP_PACKAGES = [
    "intel-ucode", "cachyos-v3-mirrorlist", "vulkan-intel", "intel-media-driver",
    "lib32-vulkan-intel", "scx-scheds", "scx-tools",
    "moonlight-qt", "tlp", "tlp-rdw", "acpi_call-dkms", "sof-firmware",
]

pacman.packages(
    name="Install laptop official packages",
    packages=LAPTOP_PACKAGES,
    present=True,
)

LAPTOP_AUR_PACKAGES = ["mkinitcpio-numlock", "thermald"]

server.shell(
    name="Install laptop AUR packages via yay",
    commands=[
        f"sudo -u {target_user} yay -S --needed --noconfirm {' '.join(LAPTOP_AUR_PACKAGES)}"
    ],
)

# 2. Graphics & Environment
files.line(
    name="Set Intel iHD VAAPI driver",
    path="/etc/environment",
    line="LIBVA_DRIVER_NAME=iHD",
)

# 3. Kernel & Boot Configuration
grub_cmdline = "split_lock_detect=off loglevel=3 quiet hugepages=512 i915.enable_fbc=1 i915.enable_guc=3 rcutree.enable_rcu_lazy=1 mitigations=off zswap.enabled=0 mem_sleep_default=deep"

files.line(
    name="Configure GRUB kernel command line for Laptop",
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
    name="Set mkinitcpio modules for Intel",
    path="/etc/mkinitcpio.conf",
    line=r"^MODULES=.*",
    replace="MODULES=(i915 nvme)",
)

server.shell(
    name="Ensure numlock hook in mkinitcpio.conf",
    commands=[
        "grep -q 'numlock' /etc/mkinitcpio.conf || sed -i 's/HOOKS=(\\(.*\\))/HOOKS=(\\1 numlock)/' /etc/mkinitcpio.conf"
    ],
)

# 4. NVIDIA dGPU Hard-Off via ACPI
disable_nvidia_conf = """blacklist nouveau
options nouveau modeset=0
blacklist nvidia
blacklist nvidia_drm
blacklist nvidia_modeset
blacklist nvidia_uvm
"""
files.put(
    name="Blacklist NVIDIA drivers in modprobe.d",
    dest="/etc/modprobe.d/disable-nvidia.conf",
    src=StringIO(disable_nvidia_conf),
)

files.put(
    name="Install nvidia-acpi-off service unit",
    dest="/etc/systemd/system/nvidia-acpi-off.service",
    src=str(TEMPLATES_DIR / "systemd" / "nvidia-acpi-off.service"),
)

files.directory(
    name="Ensure system-sleep directory exists",
    path="/usr/lib/systemd/system-sleep",
    present=True,
)
files.put(
    name="Install nvidia-acpi-off sleep hook",
    dest="/usr/lib/systemd/system-sleep/nvidia-acpi-off",
    src=str(TEMPLATES_DIR / "systemd" / "nvidia-acpi-sleep.sh"),
    mode="0755",
)

systemd.service(
    name="Enable nvidia-acpi-off service",
    service="nvidia-acpi-off",
    enabled=True,
)

# 5. Intel Wi-Fi Tuning
iwlwifi_conf = """options iwlwifi 11n_disable=8
options iwlmvm power_scheme=1
"""
files.put(
    name="Configure Intel Wi-Fi aggregation and power scheme",
    dest="/etc/modprobe.d/iwlwifi.conf",
    src=StringIO(iwlwifi_conf),
)

# 6. Battery Protection
files.put(
    name="Configure battery charge thresholds (75-90%)",
    dest="/etc/udev/rules.d/99-battery-threshold.rules",
    src=str(TEMPLATES_DIR / "udev" / "99-battery-threshold.rules"),
)

# 7. TLP Power Management
systemd.service(
    name="Mask systemd-rfkill service",
    service="systemd-rfkill",
    running=False,
    enabled=False,
)
systemd.service(
    name="Mask systemd-rfkill socket",
    service="systemd-rfkill.socket",
    running=False,
    enabled=False,
)

files.line(
    name="Set TLP Wi-Fi power on battery to off",
    path="/etc/tlp.conf",
    line=r"^#*WIFI_PWR_ON_BAT=.*",
    replace="WIFI_PWR_ON_BAT=off",
)
files.line(
    name="Set TLP PCIe ASPM on battery to default",
    path="/etc/tlp.conf",
    line=r"^#*PCIE_ASPM_ON_BAT=.*",
    replace="PCIE_ASPM_ON_BAT=default",
)
files.line(
    name="Set TLP NVMe energy policy on battery to default",
    path="/etc/tlp.conf",
    line=r"^#*NVM_ENERGY_PERF_POLICY_ON_BAT=.*",
    replace="NVM_ENERGY_PERF_POLICY_ON_BAT=default",
)

systemd.service(
    name="Enable TLP service",
    service="tlp",
    enabled=True,
)
systemd.service(
    name="Disable NetworkManager-wait-online service",
    service="NetworkManager-wait-online",
    enabled=False,
)

# 8. SCX Scheduler (scx_bpfland)
files.directory(
    name="Ensure /etc/scx_loader exists",
    path="/etc/scx_loader",
    present=True,
)
files.put(
    name="Configure scx_bpfland default scheduler",
    dest="/etc/scx_loader/config.toml",
    src=str(TEMPLATES_DIR / "scx_bpfland.toml"),
)
systemd.service(
    name="Enable scx_loader daemon",
    service="scx_loader",
    enabled=True,
)

# 9. Additional Laptop Services
for svc in ["thermald", "paccache.timer"]:
    systemd.service(
        name=f"Enable laptop service {svc}",
        service=svc,
        enabled=True,
    )
