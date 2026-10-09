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
            TRANS_DIR="/home/{target_user}/.local/share/plasma/plasmoids/com.oldlorekeeper.transmission"
            mkdir -p "$TRANS_DIR"
            tar -xf "$TRANS_ARCHIVE" -C "${{TRANS_DIR:h}}"
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
            [[ -f "{repo_dir}/Resources/Icons/Kate/${{icon:t}}" ]] && cp -f "{repo_dir}/Resources/Icons/Kate/${{icon:t}}" "$icon"
        done"""
    ],
)

# 4. ZSH Plugins & Links
server.shell(
    name="Install Oh My Zsh plugins and link zshrc",
    commands=[
        f"""if [[ ! -d "/home/{target_user}/.oh-my-zsh" ]]; then
            sudo -u {target_user} git clone https://github.com/ohmyzsh/ohmyzsh.git "/home/{target_user}/.oh-my-zsh" || true
        fi
        ZSH_CUSTOM="/home/{target_user}/.oh-my-zsh/custom"
        mkdir -p "$ZSH_CUSTOM/plugins"
        [[ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]] && sudo -u {target_user} git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions" || true
        [[ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]] && sudo -u {target_user} git clone https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" || true

        ln -sf "/home/{target_user}/.oh-my-zsh" /root/.oh-my-zsh
        rm -f "/home/{target_user}/.zshrc"
        ln -sf "{repo_dir}/Resources/zshrc/zshrc_{profile}" "/home/{target_user}/.zshrc"
        ln -sf "/home/{target_user}/.zshrc" /root/.zshrc
        chown -R {target_user}:{target_user} "/home/{target_user}/.oh-my-zsh" "/home/{target_user}/.zshrc"
        """
    ],
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
server.shell(
    name="Ensure KDE local share directories exist",
    commands=[
        f'mkdir -p "/home/{target_user}/.local/share/"{{icons,kxmlgui5,plasma,color-schemes,aurorae,fonts,wallpapers}}',
        f'chown -R {target_user}:{target_user} "/home/{target_user}/.local/share"',
    ],
)

# 7. Apply Konsave Profile
if str(cfg.get("APPLY_KONSAVE", "true")).lower() == "true":
    server.shell(
        name="Apply latest Konsave theme profile",
        commands=[
            f"""if command -v konsave &>/dev/null; then
                PROFILE_DIR="{repo_dir}/Resources/Konsave"
                [[ "{profile}" == "desktop" ]] && LATEST_KNSV=$(ls -t "$PROFILE_DIR"/Desktop*.knsv 2>/dev/null | head -n1) || LATEST_KNSV=$(ls -t "$PROFILE_DIR"/Laptop*.knsv 2>/dev/null | head -n1)
                if [[ -n "$LATEST_KNSV" && -f "$LATEST_KNSV" ]]; then
                    sudo -u {target_user} konsave -i "$LATEST_KNSV" --force 2>/dev/null || true
                    sudo -u {target_user} konsave -a "${{LATEST_KNSV:t:r}}" 2>/dev/null || true
                fi
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

