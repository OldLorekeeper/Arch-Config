from io import StringIO
from pathlib import Path
from pyinfra.operations import files, systemd

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# 1. NetworkManager & iwd
files.put(
    name="Configure NetworkManager iwd backend",
    dest="/etc/NetworkManager/conf.d/wifi_backend.conf",
    src=str(TEMPLATES_DIR / "network" / "wifi_backend.conf"),
)

files.put(
    name="Configure iwd regulatory domain",
    dest="/etc/iwd/main.conf",
    src=str(TEMPLATES_DIR / "network" / "iwd_main.conf"),
)

# 2. Bluetooth
files.line(
    name="Enable Bluetooth experimental features",
    path="/etc/bluetooth/main.conf",
    line=r"^#*Experimental\s*=.*",
    replace="Experimental = true",
)

# 3. Network Dispatchers
files.put(
    name="Install Tailscale GRO network dispatcher",
    dest="/etc/NetworkManager/dispatcher.d/99-tailscale-gro",
    src=str(TEMPLATES_DIR / "network" / "99-tailscale-gro"),
    mode="0755",
)

files.put(
    name="Install Wi-Fi power save disable dispatcher",
    dest="/etc/NetworkManager/dispatcher.d/disable-wifi-powersave",
    src=str(TEMPLATES_DIR / "network" / "disable-wifi-powersave"),
    mode="0755",
)

# 4. Reflector
reflector_conf = """--country GB,IE,NL,DE,FR
--protocol https
--latest 20
--sort score
--save /etc/pacman.d/mirrorlist
"""
files.put(
    name="Configure reflector.conf",
    dest="/etc/xdg/reflector/reflector.conf",
    src=StringIO(reflector_conf),
)

# 5. Core Services
for svc in ["NetworkManager", "bluetooth", "sshd", "plasmalogin", "fwupd", "reflector.timer"]:
    systemd.service(
        name=f"Enable core service {svc}",
        service=svc,
        enabled=True,
    )
