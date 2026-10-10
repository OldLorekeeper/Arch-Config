from pathlib import Path
from pyinfra.operations import files, server
from System.config import get_config

cfg = get_config()
target_user = cfg["TARGET_USER"]
profile = cfg["DEVICE_PROFILE"]
repo_dir = cfg["REPO_DIR"]
secrets_dir = cfg["SECRETS_DIR"]

# 1. Konsole Color Schemes & Profiles
files.directory(
    name="Ensure user konsole directory exists",
    path=f"/home/{target_user}/.local/share/konsole",
    user=target_user,
    group=target_user,
    mode="0755",
    present=True,
)

server.shell(
    name="Copy Konsole profiles and color schemes",
    commands=[
        f"cp -f {repo_dir}/Resources/Konsole/* /home/{target_user}/.local/share/konsole/ 2>/dev/null || true",
        f"chown -R {target_user}:{target_user} /home/{target_user}/.local/share/konsole",
    ],
)

# 2. Transmission Plasmoid
server.shell(
    name="Extract Transmission Plasmoid",
    commands=[
        f"""TRANS_ARCHIVE="{repo_dir}/Resources/Plasmoids/transmission-plasmoid.tar.gz"
        if [[ -f "$TRANS_ARCHIVE" ]]; then
            PLASMOIDS_DIR="/home/{target_user}/.local/share/plasma/plasmoids"
            mkdir -p "$PLASMOIDS_DIR"
            tar -xf "$TRANS_ARCHIVE" -C "$PLASMOIDS_DIR"
            chown -R {target_user}:{target_user} "/home/{target_user}/.local/share/plasma"
        fi"""
    ],
)

# 3. Papirus Folders & Kate Overrides
server.shell(
    name="Apply Papirus Breeze dark folder colors",
    commands=["papirus-folders -C breeze --theme Papirus-Dark || true"],
)

server.shell(
    name="Apply custom Kate icons to Papirus theme",
    commands=[
        f"""find /usr/share/icons/Papirus -type f \\( -name "kate.svg" -o -name "kate-symbolic.svg" -o -name "kate2.svg" -o -name "org.kde.kate.svg" \\) | while read -r icon; do
            icon_name=$(basename "$icon")
            [[ -f "{repo_dir}/Resources/Icons/Kate/$icon_name" ]] && cp -f "{repo_dir}/Resources/Icons/Kate/$icon_name" "$icon"
        done"""
    ],
)

# 4. ZSH Plugins & Links
server.shell(
    name="Install Oh My Zsh and plugins",
    commands=[
        f"""if [[ ! -d "/home/{target_user}/.oh-my-zsh" ]]; then
            sudo -u {target_user} git clone https://github.com/ohmyzsh/ohmyzsh.git "/home/{target_user}/.oh-my-zsh" || true
        fi
        ZSH_CUSTOM="/home/{target_user}/.oh-my-zsh/custom"
        mkdir -p "$ZSH_CUSTOM/plugins"
        [[ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]] && sudo -u {target_user} git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions" || true
        [[ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]] && sudo -u {target_user} git clone https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" || true
        chown -R {target_user}:{target_user} "/home/{target_user}/.oh-my-zsh"
        """
    ],
)

files.link(
    name="Link root .oh-my-zsh to user .oh-my-zsh",
    path="/root/.oh-my-zsh",
    target=f"/home/{target_user}/.oh-my-zsh",
    symbolic=True,
)

files.link(
    name=f"Link user .zshrc to {profile} profile",
    path=f"/home/{target_user}/.zshrc",
    target=f"{repo_dir}/Resources/zshrc/zshrc_{profile}",
    symbolic=True,
    user=target_user,
    group=target_user,
)

files.link(
    name="Link root .zshrc to user .zshrc",
    path="/root/.zshrc",
    target=f"/home/{target_user}/.zshrc",
    symbolic=True,
)

# 5. Antigravity Dual-Tier Topology Sync
server.shell(
    name="Enforce Antigravity dual-tier symlink topology",
    commands=[
        f"""if [[ -f "{secrets_dir}/Scripts/antigravity_sync.zsh" ]]; then
            zsh "{secrets_dir}/Scripts/antigravity_sync.zsh" "{target_user}" || true
        fi"""
    ],
)

# 6. KDE Resource Directories
for d in ["icons", "kxmlgui5", "plasma", "color-schemes", "aurorae", "fonts", "wallpapers"]:
    files.directory(
        name=f"Ensure KDE directory ~/.local/share/{d} exists",
        path=f"/home/{target_user}/.local/share/{d}",
        user=target_user,
        group=target_user,
        mode="0755",
        present=True,
    )

# 7. Apply Konsave Profile
if str(cfg.get("APPLY_KONSAVE", "true")).lower() == "true":
    profile_dir = Path(repo_dir) / "Resources" / "Konsave"
    prefix = "Desktop" if profile == "desktop" else "Laptop"
    knsv_files = sorted(profile_dir.glob(f"{prefix}*.knsv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if knsv_files:
        latest_knsv = knsv_files[0]
        profile_name = latest_knsv.stem
        server.shell(
            name=f"Apply latest Konsave theme profile ({profile_name})",
            commands=[
                f"""if command -v konsave &>/dev/null; then
                    sudo -u {target_user} konsave -i "{latest_knsv}" --force 2>/dev/null || true
                    sudo -u {target_user} konsave -a "{profile_name}" 2>/dev/null || true
                fi"""
            ],
        )

# 8. Apply KWin Rules
server.shell(
    name=f"Compile and apply KWin rules for {profile}",
    commands=[
        f'sudo -u {target_user} zsh "{repo_dir}/Scripts/Operations/kwin_sync.zsh" "{profile}" || true'
    ],
)

