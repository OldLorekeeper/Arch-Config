import json
import os
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
        users = [p.name for p in Path("/home").iterdir() if p.is_dir()]
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

    # Defaults for other variables
    cfg.setdefault("MEDIA_UUID", "")
    cfg.setdefault("MONITOR_PORT", "")
    cfg.setdefault("EDID_ENABLE", "false")
    cfg.setdefault("APPLY_KONSAVE", "true")
    cfg.setdefault("GIT_NAME", "")
    cfg.setdefault("GIT_EMAIL", "")
    cfg.setdefault("GIT_PAT", "")

    cfg["REPO_DIR"] = str(REPO_DIR)
    cfg["USER_HOME"] = f"/home/{target_user}"
    cfg["SECRETS_DIR"] = f"/home/{target_user}/Obsidian/Secrets"

    return cfg
