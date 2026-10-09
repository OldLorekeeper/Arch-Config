# Installation

## 1. Pre-Installation
Follow the ArchWiki pre-installation steps until you have successfully booted into the live environment:
[ArchWiki: Installation Guide](https://wiki.archlinux.org/title/Installation_guide)

## 2. Prepare Environment
```bash
loadkeys uk
iwctl --passphrase [password] station wlan0 connect [SSID]
```

## 3. Run Install Script
This installer formats target storage with an optimised Btrfs subvolume layout, bootstraps CachyOS base packages, and hands off system configuration directly to the declarative **pyinfra** engine (`System/deploy.py`).

> [!IMPORTANT]
> Do not run this command via a pipe (`| zsh`) as it requires interactive user input. Use the process substitution method below.

```bash
zsh <(curl -Ls https://smplu.link/bYUs7)
```

Alternatively, if you already cloned the repository in the live environment:
```bash
sudo zsh Scripts/Core/setup_install.zsh
```

### Installation Stages & Inputs

The setup process proceeds across two automated phases during installation:

#### Stage 1: Storage & Bootstrapping (`setup_install.zsh`)
Be ready to provide the following information when prompted:

1. **Secrets Decryption:**
   - The script downloads `setup_secrets.enc` and prompts for the decryption password.
   - *Fallback:* If decryption fails or the file is missing, you can manually enter root/user passwords and Git credentials.

2. **User & Identity Configuration:**
   - **Hostname:** Defaults to `NCC-1701`.
   - **Username:** Defaults to `user`.
   - **Git Credentials:** Name, Email, and **GitHub Personal Access Token (PAT)** for cloning private dotfiles and secrets.

3. **Device Profile:**
   - Select **1** for Desktop (Ryzen 7800X3D / RX 7900 XT).
   - Select **2** for Laptop (Dell XPS 9550).

4. **Desktop Specifics (Profile 1 Only):**
   - **Media Partition:** Option to supply a UUID to mount an existing media drive at `/mnt/Media`.
   - **Headless EDID:** Option to inject a custom 2560x1600 EDID for headless Sunshine streaming.

5. **Target Disk:**
   - Select the target drive (e.g. `nvme0n1`). The installer creates GPT partitions and Btrfs subvolumes (`@`, `@home`, `@log`, `@pkg`, `@.snapshots`, `@games`).

#### Stage 2: Declarative Provisioning (`System/deploy.py`)
Once base pacstrap completes, the installer automatically invokes pyinfra inside `arch-chroot`:
```bash
arch-chroot /mnt uv run --with pyinfra pyinfra @local /home/$TARGET_USER/Obsidian/Arch-Config/System/deploy.py
```
This declaratively provisions all official and AUR packages, user accounts, sudo policies, kernel sysctls, ZRAM, theming, pacman hooks, and hardware-specific tunings (LACT/Sunshine or TLP/dGPU power-off), before removing temporary installation credentials from disk.

---

## 4. Reboot & First Boot

Once the installer outputs `Installation Complete!`, reboot the machine:

```bash
reboot
```

> [!TIP]
> **First Boot (Stage 3):** Upon logging in to KDE Plasma, a terminal window will automatically launch [`setup_boot.zsh`](../Scripts/Core/setup_boot.zsh) to connect Tailscale, prompt for Sunshine display mode indices, and migrate Git PAT to KWallet (`libsecret`). **Do not close this window** until it self-destructs.

---

## 5. Ongoing Maintenance & Drift Remediation

In an installed system, you do not re-run the bare-metal installer. Instead, manage and audit declarative state directly:

```bash
# Preview declarative drift (dry run)
uv run --with pyinfra pyinfra @local System/deploy.py --dry

# Apply declarative state and reconcile any drift
sudo uv run --with pyinfra pyinfra @local System/deploy.py

# Or execute full maintenance suite (system update + pyinfra drift check + orphans + mirror optimisations)
system_maintain
```
