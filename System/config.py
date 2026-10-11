import json
import os
import re
from pathlib import Path

# Paths
REPO_DIR = Path(__file__).resolve().parent.parent
INSTALL_VARS_FILE = Path("/install_vars.json")
ZSHRC_FILE = Path.home() / ".zshrc"

def get_config():
    """
    Resolve configuration from:
    1. /install_vars.json (Live installer chroot)
    2. Environment variables
    3. Live system discovery (Zshrc / Host / Sysfs)
    """
    cfg = {}

    if INSTALL_VARS_FILE.exists():
        try:
            with open(INSTALL_VARS_FILE, "r") as f:
                cfg = json.load(f)
        except Exception:
            pass

    # Profile determination
    profile = cfg.get("DEVICE_PROFILE") or os.environ.get("SYS_PROFILE")
    if not profile and ZSHRC_FILE.exists():
        for line in ZSHRC_FILE.read_text().splitlines():
            if line.startswith("export SYS_PROFILE="):
                profile = line.split("=")[1].strip('"\'')
                break

    if not profile:
        # Fallback heuristic: check CPU vendor / model
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text()
            if "AMD" in cpuinfo:
                profile = "desktop"
            else:
                profile = "laptop"
        except Exception:
            profile = "desktop"

    cfg["DEVICE_PROFILE"] = profile

    # User resolution
    target_user = cfg.get("TARGET_USER") or os.environ.get("SUDO_USER") or os.environ.get("USER") or "user"
    if target_user == "root":
        # Check /home for single user
        users = [p.name for p in Path("/home").iterdir() if p.is_dir() and not p.name.startswith(".")]
        target_user = users[0] if len(users) == 1 else "user"
    cfg["TARGET_USER"] = target_user

    # Hostname resolution
    hostname = cfg.get("HOSTNAME")
    if not hostname:
        try:
            hostname = Path("/etc/hostname").read_text().strip()
        except Exception:
            hostname = "NCC-1701"
    cfg["HOSTNAME"] = hostname

    # Dynamic EDID and Monitor Port Discovery
    edid_enable = cfg.get("EDID_ENABLE") or os.environ.get("EDID_ENABLE")
    monitor_port = cfg.get("MONITOR_PORT") or os.environ.get("MONITOR_PORT")

    # Inspect /etc/default/grub if not explicitly set
    grub_file = Path("/etc/default/grub")
    if grub_file.exists() and (not edid_enable or not monitor_port):
        try:
            grub_text = grub_file.read_text()
            match = re.search(r"drm\.edid_firmware=([^:]+):edid/custom_sunshine\.bin", grub_text)
            if match:
                if not edid_enable:
                    edid_enable = "true"
                if not monitor_port:
                    monitor_port = match.group(1)
        except Exception:
            pass

    # Desktop profile heuristic fallback
    if profile == "desktop":
        custom_edid = Path("/usr/lib/firmware/edid/custom_sunshine.bin")
        repo_edid = REPO_DIR / "Resources" / "Sunshine" / "custom_sunshine.bin"
        if (custom_edid.exists() or repo_edid.exists()) and not edid_enable:
            edid_enable = "true"
        if not monitor_port:
            try:
                connected = []
                for p in Path("/sys/class/drm").glob("*/status"):
                    if p.read_text().strip() == "connected":
                        port_name = p.parent.name.split("-", 1)[-1]
                        connected.append(port_name)
                if "DP-2" in connected:
                    monitor_port = "DP-2"
                elif connected:
                    monitor_port = connected[0]
            except Exception:
                pass
            if not monitor_port:
                monitor_port = "DP-2"

    cfg["EDID_ENABLE"] = str(edid_enable if edid_enable is not None else "false").lower()
    cfg["MONITOR_PORT"] = monitor_port or ""

    # Defaults for other variables
    cfg.setdefault("MEDIA_UUID", "")
    cfg.setdefault("APPLY_KONSAVE", "true")
    cfg.setdefault("GIT_NAME", "")
    cfg.setdefault("GIT_EMAIL", "")
    cfg.setdefault("GIT_PAT", "")

    cfg["REPO_DIR"] = str(REPO_DIR)
    cfg["USER_HOME"] = f"/home/{target_user}"
    cfg["SECRETS_DIR"] = f"/home/{target_user}/Obsidian/Secrets"

    return cfg
