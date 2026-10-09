# Arch Config

**WARNING:** All scripts and configurations in this repo are highly-opinionated and specific to the repo owner's needs. They contain hardcoded kernel parameters and hardware-specific udev rules. Do not execute on unsupported hardware without significant modification.

This repository hosts a bespoke automation suite for deploying a high-performance Arch Linux environment. It enforces a strict configuration hierarchy (Core → Device), tailored for maximum throughput and stability across diverse hardware profiles (including AMD Ryzen/RDNA3 desktops and Intel/NVIDIA laptops).

### [Get Started ⇢](Docs/Installation.md)

```bash
# Live USB interactive installation:
zsh <(curl -Ls https://smplu.link/bYUs7)

# Installed system declarative drift audit:
uv run --with pyinfra pyinfra @local System/deploy.py --dry
```

---
## Hardware specs

The scripts and steps contained in this repo are tailored to the below system profiles.
#### Desktop profile:

| Component       | Model                      | Specs / Link                                                                                                                                                                              |
| :-------------- | :------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Motherboard** | Asus ROG Strix X670E-I     | [Specifications](https://rog.asus.com/uk/motherboards/rog-strix/rog-strix-x670e-i-gaming-wifi-model/spec/)                                                                                |
| **CPU**         | AMD Ryzen 7 7800X3D        | [TechPowerUp](https://www.techpowerup.com/cpu-specs/ryzen-7-7800x3d.c3022)                                                                                                                |
| **GPU**         | Gigabyte Radeon RX 7900 XT | [TechPowerUp](https://www.techpowerup.com/gpu-specs/gigabyte-rx-7900-xt-gaming-oc.b9940)                                                                                                  |
| **RAM**         | Corsair Vengeance DDR5     | [32GB (2x16GB) 6400MT/s CL36](https://www.corsair.com/uk/en/p/ddr5-ram/cmk32gx5m2b6400c36/vengeance-32gb-2x16gb-ddr5-dram-6400mt-s-c36-memory-kit-black-cmk32gx5m2b6400c36#tab-techspecs) |
| **PSU**         | Corsair SF750              | [750W 80+ Platinum SFX](https://www.corsair.com/ww/en/p/psu/cp-9020186-uk/sf-series-sf750-750-watt-80-plus-platinum-certified-high-performance-sfx-psu-uk-cp-9020186-uk#tab-techspecs)    |
| **SSD**         | Samsung 970 EVO Plus       | [1TB NVMe M.2](https://www.techpowerup.com/ssd-specs/samsung-970-evo-plus-1-tb.d61)                                                                                                       |
| **Network**     | Intel I225-V / Wi-Fi 6E    | 2.5GbE LAN / 802.11ax                                                                                                                                                                     |
#### Laptop profile:

| Component   | Model                    | Specs / Link                                                                            |
| :---------- | :----------------------- | :-------------------------------------------------------------------------------------- |
| **Model**   | Dell XPS 15 9550         | [Dell Support](https://www.dell.com/support/home/en-us/product-support/product/xps-15-9550-laptop/docs) |
| **CPU**     | Intel Core i5-6300HQ     | [TechPowerUp](https://www.techpowerup.com/cpu-specs/core-i5-6300hq.c1833)                               |
| **GPU**     | Nvidia GeForce GTX 960M  | [TechPowerUp](https://www.techpowerup.com/gpu-specs/geforce-gtx-960m.c2635)                             |
| **RAM**     | 8GB DDR4                 | [Crucial Upgrades](https://www.crucial.com/compatible-upgrade-for/dell/xps-15-(9550))                   |
| **SSD**     | Samsung SSD 850 EVO      | [TechPowerUp](https://www.techpowerup.com/ssd-specs/samsung-850-evo-1-tb.d66)                           |
| **Network** | Intel Wireless 8265      | [Intel ARK](https://ark.intel.com/content/www/us/en/ark/products/94150/intel-dual-band-wireless-ac-8265.html) |

---
## Architecture

The setup utilises a modular multi-stage deployment pipeline ensuring reproducible, declarative configuration.

#### Stage 1: Bare-Metal Installer (Live Environment)

**Script:** `setup_install.zsh` (Zsh)

- **Pre-flight:** Validates UEFI boot mode, internet connectivity, and decrypts secrets (`setup_secrets.enc`).
- **Configuration:** Collects target configuration parameters and clones repository trees into the target disk.
- **Partitioning:** Formats Btrfs layout with optimised subvolumes (including `+C` for `@games`).
- **Base System:** Pacstraps CachyOS base kernel, `uv`, and core system packages.
- **Handoff:** Hands off execution directly to Stage 2 inside `arch-chroot`.

#### Stage 2: Declarative System Provisioning

**Engine:** `System/deploy.py` (pyinfra via `uv`)

- **Single Source of Truth:** Manages pacman/AUR packages, users, sudo policies, kernel parameters, sysctl, network dispatchers, and systemd units.
- **Profile Tuning:** Automatically applies desktop (AMD Ryzen 7800X3D / RX 7900 XT / LACT / Sunshine) or laptop (Intel / ACPI dGPU isolation / TLP) hardware optimisations.
- **Theming & Desktop:** Deploys Papirus dark icons, Konsole color schemes, Oh My Zsh configurations, Konsave profiles, and KWin rules.
- **Secrets Cleanup:** Erases temporary installation variables from the target filesystem prior to unmounting.

#### Stage 3: First Graphical Login

**Script:** `setup_boot.zsh` (Zsh Autostart)

- **Execution:** Runs automatically upon first user desktop login in a floating terminal window.
- **Interactive Prompts:** Configures Tailscale node association and Sunshine display mode indexes.
- **Self-Destruct:** Removes the autostart entry and cleans up on completion.

---
## Development standards

This repository adheres to strict configuration standards to maintain stability:

- **Declarative Core:** `pyinfra` (orchestrated ephemerally via `uv`) serves as the definitive source of truth for system state and configuration drift remediation.
- **Shell:** `zsh` is reserved for bare-metal bootstrapping and standalone operational CLI utilities.
- **Idempotency:** All pyinfra deployment operations and maintenance scripts are idempotent and safe to re-run.
- **Safety:** All zsh scripts enforce `setopt ERR_EXIT NO_UNSET PIPE_FAIL`.
- **Formatting:** Scripts utilise compact layouts with double-dotted line separators for readability (see [Templates](./Scripts/Templates) folder))

---
## License and disclaimer

This is a personal configuration repository provided "as-is". No warranty is implied. Use these scripts at your own risk.
