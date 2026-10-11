# Arch-Config: Opinionated Architecture & Decision Rationale

> [!NOTE]
> This document records the architectural baseline, design rationale, and rejected alternatives evaluated as optimal at the time of writing (October 2026). It serves as an authoritative contextual record of current choices without constraining future iterations as the Linux kernel, schedulers, and driver ecosystems evolve.

---

## 1. Common Base Architecture

These decisions form the baseline for both hardware profiles and are declared under `System/common/`.

### 1.1 Distribution, Repositories & Package Management
- **Arch Linux + CachyOS Repositories**:
  - *Decision*: Overlay CachyOS repositories on top of Arch Linux, leveraging microarchitecture-optimized packages (`x86_64_v4` for Zen 4 desktop, `x86_64_v3` for Intel laptop).
  - *Rationale*: CachyOS packages are compiled with `-O3`, LTO, PGO, and instruction-set target flags, providing 5–15% uplift in CPU-bound tasks, shader compilation, and gaming 1% lows.
- **Purging KDE Discover**:
  - *Decision*: KDE Plasma is installed modularly (`plasma-desktop`, `plasma-nm`, etc.) without `plasma-meta`, and `discover` is explicitly purged via pacman.
  - *Rationale*: Discover introduces background PackageKit polling, Flatpak conflicts, and redundant memory consumption. All package management is strictly handled via `pacman`, `yay`, and declarative `pyinfra`.
- **Makepkg Compilation Tuning (`/etc/makepkg.conf`)**:
  - *Decision*:
    - `CFLAGS`: `-march=native -O2 -pipe -fno-plt -fexceptions -Wp,-D_FORTIFY_SOURCE=3 -Wformat -Werror=format-security -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer`
    - `MAKEFLAGS="-j$(nproc)"`
    - `BUILDDIR=/tmp/makepkg`
    - `COMPRESSZST=(zstd -c -z -q -T0 -3 -)`
    - `RUSTFLAGS="-C target-cpu=native"`
  - *Rationale*: Compiles AUR packages targeting the native host CPU instructions while retaining frame pointers (`-fno-omit-frame-pointer`) for system tracing and debugging. Building on `tmpfs` (`/tmp/makepkg`) reduces NVMe write wear and speeds up linking.
- **Pacman Concurrency & Repositories**:
  - *Decision*: `ParallelDownloads = 10` (Desktop) / `5` (Laptop), `Color` enabled, `multilib` enabled. `[lizardbyte]` repository added with `SigLevel = Optional`.
  - *Rationale*: Maximizes multi-connection mirror download speeds. `[lizardbyte]` repo supplies precompiled, signed binary releases of Sunshine host streaming.

### 1.2 Storage, Btrfs Subvolume Layout & Maintenance
- **Subvolume Isolation Scheme**:
  - *Decision*:
    - `@` -> `/`
    - `@home` -> `/home`
    - `@pkg` -> `/var/cache/pacman/pkg`
    - `@log` -> `/var/log`
    - `@.snapshots` -> `/.snapshots`
    - `@games` -> `/home/$USER/Games`
  - *Rationale*:
    - Isolating `@pkg` and `@log` prevents pacman package caches and systemd journals from bloating root snapshots.
    - Isolating `@games` ensures large multi-gigabyte Steam/Lutris game installations are excluded from system rollbacks, preventing snapshot exhaustion during kernel or package restorations.
- **Btrfs Mount Flags**:
  - *Decision*: `rw,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2`.
  - *Rationale*:
    - `noatime`: Eliminates metadata write overhead on read operations.
    - `compress=zstd:3`: Strikes the optimal sweet spot between disk bandwidth amplification and CPU overhead.
    - `discard=async`: Performs TRIM operations asynchronously in the background, avoiding synchronous blocking stalls associated with synchronous `discard`.
- **Btrfs Maintenance Timers**:
  - *Decision*: Enable `btrfs-balance.timer` (monthly `dusage=50 -musage=50`), `btrfs-scrub@-.timer` (monthly data integrity scrub), and `timeshift-hourly.timer`.
  - *Rationale*: Balances lightly allocated block groups to prevent early "No space left on device" errors, detects silent bit rot via journal scrubbing, and guarantees hourly rollback snapshots.
- **Bootloader & Snapshot Integration**:
  - *Decision*: GRUB with `grub-btrfsd --syslog --timeshift-auto` drop-in override; `31_efi_bootnext` made non-executable.
  - *Rationale*: Automatically generates bootable GRUB menu entries whenever Timeshift creates a snapshot. Disabling `31_efi_bootnext` eliminates redundant and cluttered firmware menu entries.
- **NVMe I/O Scheduling**:
  - *Decision*: Force queue scheduler to `none` for NVMe devices via udev (`/etc/udev/rules.d/60-iosched.rules`).
  - *Rationale*: NVMe SSDs utilize hardware-level multi-queue submission (`blk-mq`) directly on controller silicon. Kernel software schedulers (`mq-deadline`, `bfq`) add unnecessary CPU scheduling overhead and latency.

### 1.3 Memory & Sysctl Tuning
- **ZRAM vs Physical Swap**:
  - *Decision*: Standardize on compressed in-RAM swap (`zram-generator`) using `zstd` algorithm and `swap-priority = 100`, while disabling kernel `zswap` (`zswap.enabled=0`).
  - *Rationale*: Eliminates SSD swap wear and latency spikes. `zstd` provides a 2.6:1–3.0:1 compression ratio, expanding available effective memory without disk I/O penalties. Disabling kernel `zswap` prevents redundant double-compression and CPU overhead between the page cache compressor and ZRAM.
- **Memory Management Sysctls**:
  - *Repository Configuration (`/etc/sysctl.d/99-swappiness.conf`)*:
    - `vm.swappiness = 150`: Instructs the kernel to aggressively swap cold anonymous pages into fast ZRAM, preserving physical RAM for game assets and filesystem caches.
    - `vm.page-cluster = 0`: Disables multi-page read-ahead on swap; reads single 4KB pages to avoid wasted decompression cycles on random memory access.
    - `vm.max_map_count = 2147483642`: Required by modern memory-mapped Windows titles running through Proton (e.g. *Star Citizen*, *Hogwarts Legacy*, *DayZ*).
    - `vm.watermark_scale_factor = 125`: Widens the distance between memory watermarks, causing background `kswapd` to wake up proactively before processes face blocking direct memory reclamation.
  - *Upstream CachyOS Defaults (`cachyos-settings`)*:
    - `vm.watermark_boost_factor = 0`: Completely disables kswapd watermark boosting to prevent sudden, jitter-inducing "swap storms".
    - `vm.vfs_cache_pressure = 50`: Retains directory and inode caches longer in RAM.
    - `vm.dirty_bytes = 268435456` (256MB) / `vm.dirty_background_bytes = 67108864` (64MB): Replaces percentage-based dirty ratios with absolute byte limits, preventing gigabyte-sized write flushes on fast storage.

### 1.4 Networking & Connectivity
- **iwd as NetworkManager Backend**:
  - *Decision*: Configure `wifi.backend=iwd` in `/etc/NetworkManager/conf.d/wifi_backend.conf` and `Country=GB` in `/etc/iwd/main.conf`.
  - *Rationale*: `iwd` (Intel Wireless Daemon) uses fewer CPU cycles, connects up to 4x faster on boot, roams seamlessly, and eliminates `wpa_supplicant` legacy bloat.
- **Wi-Fi Power Save Policy**:
  - *Decision*: Disable Wi-Fi power saving on interface up via `/etc/NetworkManager/dispatcher.d/disable-wifi-powersave` (`iw dev $1 set power_save off`).
  - *Rationale*: 802.11 power save modes put the wireless radio into sleep states between beacon intervals, producing periodic 50–150ms latency spikes that degrade game streaming.
- **TCP BBR & Network Queuing (`/etc/sysctl.d/99-bbr.conf`)**:
  - *Decision*: `net.core.default_qdisc = fq`, `net.ipv4.tcp_congestion_control = bbr`, 16MB max buffers (`rmem_max`, `wmem_max`), `net.core.netdev_max_backlog = 10000`, and `net.ipv4.tcp_slow_start_after_idle = 0`.
  - *Rationale*: TCP BBRv3 (integrated into CachyOS) model-based pacing eliminates bufferbloat. BBR strictly requires Fair Queueing (`fq`) for packet pacing. `netdev_max_backlog = 10000` expands packet input queue depth to prevent frame drops during bursty network transfers. Disabling slow start after idle prevents bitrate dips when streaming resumes.
- **Tailscale Hardware Offloading & Forwarding**:
  - *Decision*: Dispatcher `/etc/NetworkManager/dispatcher.d/99-tailscale-gro` applies `ethtool -K $1 rx-udp-gro-forwarding on rx-gro-list off`. Sysctl `/etc/sysctl.d/99-tailscale.conf` enables IPv4/IPv6 forwarding.
  - *Rationale*: UDP Generic Receive Offload (GRO) offloads WireGuard packet assembly to network card hardware, drastically cutting CPU usage and maximizing VPN throughput.
- **Bluetooth Experimental Features**:
  - *Decision*: `Experimental = true` in `/etc/bluetooth/main.conf`.
  - *Rationale*: Enables modern BlueZ experimental D-Bus interfaces for Bluetooth peripheral battery level reporting, fast reconnects, and LE Audio support.

### 1.5 Security, Privileges & Group Access
- **Sudo Policy & User Isolation**:
  - *Decision*: Wheel group requires passwords (`%wheel ALL=(ALL:ALL) ALL`), with custom prompt string `Defaults passprompt="Enter sudo password to continue: "`. Temporary passwordless sudo drop-ins (`zz_temp_yay`) are strictly purged after installations.
  - *Rationale*: Preserves administrative boundaries against unverified scripts while avoiding default prompt ambiguities.
- **Group Memberships & Realtime Privileges**:
  - *Decision*: Provision primary user with groups `wheel`, `input`, `render`, `video`, `storage`, `gamemode`, `libvirt`, `realtime`, and `media`. Install `realtime-privileges`.
  - *Rationale*: Grants fine-grained device node access (direct rendering, input events, KVM virtualization, and elevated PAM realtime scheduling limits) without needing root elevation for desktop tasks.

### 1.6 Desktop Environment & Theming
- **Papirus Dark + Breeze Accent**:
  - *Decision*: Enforce Papirus-Dark with Breeze dark folder colors (`papirus-folders -C breeze --theme Papirus-Dark`), custom Kate icons, and novelWriter internal asset replacement.
  - *Rationale*: Eliminates inconsistent third-party application icons and aligns visual identity across the desktop.

### 1.7 System Automation & Lifecycle Hooks
- **Automated Initramfs & Bootloader Rebuild Hooks**:
  - *Decision*: `/etc/pacman.d/hooks/98-rebuild-initramfs.hook` triggers `mkinitcpio -P` upon updates to CPU microcodes (`amd-ucode`, `intel-ucode`), `btrfs-progs`, `mkinitcpio-firmware`, or `linux-cachyos-headers`. `/etc/pacman.d/hooks/99-update-grub.hook` triggers `grub-mkconfig` upon updates to `linux-cachyos`.
  - *Rationale*: Eliminates manual post-update kernel and initramfs synchronization errors, guaranteeing bootloader menus and RAM disks stay current with running kernels.
- **Icon Integrity Hooks**:
  - *Decision*: Pacman hooks for `novelwriter` and `sunshine` automatically restore custom dark Papirus branding and Web UI assets following upstream package updates.
  - *Rationale*: Prevents upstream package updates from overwriting local visual customizations.
- **Reflector Automation**:
  - *Decision*: `/etc/xdg/reflector/reflector.conf` targets HTTPS mirrors across GB, IE, NL, DE, and FR, sorted by download score, automated via `reflector.timer`.
  - *Rationale*: Keeps pacman mirrorlists fresh and resilient without manual intervention.

---

## 2. Desktop Profile Decisions (Ryzen 7800X3D + RX 7900 XT)

Targeted for heavy gaming, Sunshine remote streaming, and continuous media serving.

### 2.1 CPU & Power Scaling
- **`amd_pstate=active`**:
  - *Decision*: Explicitly configure `amd_pstate=active` on the kernel command line.
  - *Rationale*: Enables hardware-autonomous CPPC v3 frequency scaling on the Zen 4 processor, adjusting clock speeds every millisecond at hardware level.
- **EPP `performance` vs `balance_performance`**:
  - *Decision*: Set `/etc/tmpfiles.d/amd-epp.conf` to `performance` across all logical CPU cores.
  - *Rationale*:
    - While `balance_performance` lowers idle package power from ~45W to ~15W, practical evaluation in latency-sensitive environments demonstrated observable frame-pacing degradation, audio jitter, and responsiveness penalties during low-to-mid load transitions and concurrent remote game streaming (Sunshine).
    - `performance` eliminates core wake-up latency and frequency ramp lag, keeping the 7800X3D's 8 cores immediately responsive to unpredictable burst workloads.
    - System-level thermal and power constraints (LACT board power cap at 310W, custom junction fan curve, `scx_bpfland` vruntime fair scheduling, and aggressive memory reclamation watermarks) prevent CPU and GPU overheating or resource contention, rendering the idle energy savings of `balance_performance` a counterproductive trade-off for this dedicated high-performance desktop.
- **Mitigations Policy**:
  - *Decision*: Omit `mitigations=off` from GRUB command line, relying on standard hardware-level silicon mitigations.
  - *Rationale*: Zen 4 features hardware-level silicon mitigations for Spectre/Meltdown. Real-world benchmarks show **0% gaming uplift** with mitigations disabled, while unnecessarily exposing the host to browser and Proton exploits.
- **Split Lock Mitigation**:
  - *Decision*: Apply `split_lock_detect=off` in GRUB.
  - *Rationale*: Prevents the Linux kernel from penalizing and throttling Windows games (*Ghost of Tsushima*, *Far Cry 6*, Unreal Engine titles) that execute split locks across cache lines.

### 2.2 Sched-ext: `scx_bpfland` Selection
- **Scheduler Choice**:
  - *Decision*: Set `default_sched = "scx_bpfland"` in `/etc/scx_loader/config.toml`.
  - *Rationale*:
    - The 7800X3D's single-CCD architecture provides uniform 96MB L3 cache access with zero cross-CCD penalty.
    - While `scx_lavd` excels at isolated single-game frame pacing, it can starve concurrent background real-time tasks.
    - This desktop acts as a Sunshine host running concurrent game rendering, KMS frame capture, VA-API video encoding, and audio streaming. `scx_bpfland` (eBPF `vruntime` scheduler) delivers superior fairness and consistency across concurrent streaming workloads.

### 2.3 GPU Power & Graphics Acceleration (RX 7900 XT)
- **Power Cap & Fan Tuning (LACT)**:
  - *Decision*: Cap board power at 310.0W and apply custom junction curve (40°C: 20% -> 95°C: 100%) with `zero_rpm: false`.
  - *Rationale*: Operates the Navi 31 GPU within its peak efficiency curve. Disabling Zero RPM prevents memory thermal soak (keeping GDDR6 at ~46°C idle).
- **Voltage Undervolting**:
  - *Decision*: **Rejected.** Maintain factory stock voltage tables.
  - *Rationale*: RDNA 3 silicon exhibits voltage sensitivity; negative offsets produce driver timeouts and ring crashes during rapid transient load changes.
- **Driver Environment Clean-up**:
  - *Decision*: Configure `LIBVA_DRIVER_NAME=radeonsi` and omit `VDPAU_DRIVER`.
  - *Rationale*: VDPAU was officially removed from upstream Mesa in Mesa 24/25 (`mesa-vdpau` dropped from Arch). Setting the environment variable creates broken library calls. VA-API is the exclusive video acceleration standard.
- **AMD XHCI Power Fix**:
  - *Decision*: `/etc/udev/rules.d/99-xhci-fix.rules` sets `power/control="on"` for AMD USB controller `0x1022:0x43f7`.
  - *Rationale*: Prevents the motherboard USB controller from entering aggressive power-saving sleep that causes USB disconnects on Logitech wireless receivers.
- **MediaTek MT7922 Wi-Fi ASPM**:
  - *Decision*: `/etc/modprobe.d/mt7921e.conf` sets `options mt7921e disable_aspm=Y`.
  - *Rationale*: Prevents PCIe link-state wake timeouts that cause MT7922 firmware crashes and network dropouts.
- **Solaar & Logitech Peripheral Access**:
  - *Decision*: Install `/etc/udev/rules.d/42-solaar-uinput.rules` assigning `uaccess` to `/dev/uinput` and Logitech HID++ devices.
  - *Rationale*: Allows seated userspace processes (Solaar) to manage battery indicators, DPI shifts, and gesture mapping without running as root.
- **Global Proton Wayland Avoidance**:
  - *Decision*: Remove `PROTON_ENABLE_WAYLAND=1` from `/etc/environment`.
  - *Rationale*: Forcing Wayland Proton globally breaks gamescope nested sessions, older Wine binaries, and titles without Wayland driver support. Wayland Proton is configured on a per-game basis via Steam launch options or Lutris.

### 2.4 Streaming Architecture (Sunshine & nftables)
- **User Linger for Headless Streaming**:
  - *Decision*: Enable systemd user lingering (`/var/lib/systemd/linger/$USER`).
  - *Rationale*: Allows the Sunshine streaming server and user background services to start immediately on system boot before an interactive Wayland session is opened.
- **Custom Firmware EDID Injection**:
  - *Decision*: Embed `custom_sunshine.bin` in initramfs `FILES` and kernel command line (`drm.edid_firmware=DP-2:edid/custom_sunshine.bin`).
  - *Rationale*: Injects a custom virtual display topology (3440x1440@60, 2560x1440@120, 2560x1600@120) onto display port `DP-2`. This allows headless streaming without physical monitor attachment or HDMI dummy plugs.
- **Sunshine User Service Override**:
  - *Decision*: `override.conf` restarts Sunshine automatically (`Restart=always`, `RestartSec=3s`) after `graphical-session.target` and `plasma-workspace.target`.
  - *Rationale*: Prevents Sunshine from crashing during display resolution switches or Wayland compositor restarts.
- **nftables QoS (CS4 DSCP Tagging)**:
  - *Decision*: `/etc/nftables.conf` mangles Sunshine UDP/TCP packets on ports `47984-48010` with DSCP `cs4`.
  - *Rationale*: Signals upstream network switches and routers to prioritize video streaming packets over bulk downloads, preventing stream frame drops when media automation is active.

### 2.5 Media Server & Storage (`/mnt/Media`)
- **Filesystem & Mount Parameters**:
  - *Decision*: Dedicated 1.8TB Btrfs partition mounted at `/mnt/Media` with `rw,nosuid,nodev,noatime,nofail,x-gvfs-hide,x-systemd.automount,compress=zstd:3,discard=async`.
  - *Rationale*: Automount prevents boot delays if storage is unready; `x-gvfs-hide` prevents cluttering the desktop file manager sidebar.
- **Copy-on-Write (CoW) Disabling (`chattr +C`)**:
  - *Decision*: Apply `nocow` to `/var/lib/jellyfin` and `/mnt/Media/Downloads`.
  - *Rationale*: Heavy random write patterns from BitTorrent and SQLite databases cause massive Btrfs fragmentation and write amplification. Disabling CoW on these directories maintains sequential read speeds.
- **RAM Disk Transcoding**:
  - *Decision*: `/etc/tmpfiles.d/jellyfin-transcode.conf` provisions `/dev/shm/jellyfin` (RAM disk) for Jellyfin transcodes.
  - *Rationale*: Eliminates SSD write wear and I/O bottlenecks when transcoding multi-stream 4K HDR media.
- **Permissions & Group Isolation**:
  - *Decision*: Enforce group `media` (GID 962) with SGID bit (`chmod 2775`) and POSIX default ACLs (`g:media:rwX`). Service drop-ins enforce `UMask=0002` and `RequiresMountsFor=/mnt/Media`.
  - *Rationale*: Ensures all daemons (`sonarr`, `radarr`, `prowlarr`, `transmission`, `jellyfin`) and the primary user can read, modify, and delete downloaded files without permission deadlocks. Services are blocked from starting until `/mnt/Media` is successfully mounted.
- **Automated Media Maintenance**:
  - *Decision*: Enable `media-optimizer.timer` (`OnCalendar=*-*-* 01:00:00`) running `/usr/local/bin/media_optimizer`.
  - *Rationale*: Executes daily maintenance at 01:00 to verify file integrity, trigger Btrfs deduplication/scrubbing, and ensure media folders conform to permission policies.

---

## 3. Laptop Profile Decisions (Dell XPS 9550)

Targeted for maximum power efficiency, battery longevity, and silent operation.

### 3.1 GPU Architecture: ACPI Hard-Off
- **NVIDIA dGPU Power Cut**:
  - *Decision*: Completely power off the NVIDIA GTX 960M dGPU using `\_SB.PCI0.PEG0.PEGP._OFF` via `acpi_call-dkms`. Blacklist all NVIDIA and Nouveau kernel modules.
  - *Rationale*:
    - The legacy Maxwell GPU lacks modern RTD3 (Runtime D3) power management. Standard driver blacklisting leaves the PCIe power rails energized, burning 15–25W of continuous idle battery power.
    - Calling the ACPI method cuts electrical power at the hardware bus level, dropping idle battery drain from ~28W to ~7W.
- **Sleep & Wake Safety Hook**:
  - *Decision*: `/usr/lib/systemd/system-sleep/nvidia-acpi-off` calls `_ON` pre-suspend and `_OFF` post-resume.
  - *Rationale*: Putting the machine to sleep with the dGPU bus powered off causes ACPI firmware kernel panics on resume. Powering the bus on right before sleep and powering it down immediately upon resume ensures flawless S3 sleep cycles.

### 3.2 Power Management (TLP)
- **TLP Enforcement**:
  - *Decision*: Manage power via `tlp`. Explicitly purge `power-profiles-daemon` and mask `systemd-rfkill.service` and socket.
  - *Rationale*: TLP provides granular control over PCIe ASPM, SATA link power, and audio power management. `power-profiles-daemon` conflicts directly with TLP rules. Masking `systemd-rfkill` prevents race conditions with TLP's radio state management.
- **Conservative Battery Link Policies**:
  - *Decision*: In `/etc/tlp.conf`:
    - `WIFI_PWR_ON_BAT=off`
    - `PCIE_ASPM_ON_BAT=default`
    - `NVM_ENERGY_PERF_POLICY_ON_BAT=default`
  - *Rationale*:
    - Enforcing aggressive ASPM and NVMe power saving on the XPS 9550 causes PCIe link dropouts and NVMe controller disconnects. Leaving ASPM and NVMe on `default` maintains stability.
    - Disabling Wi-Fi power saving prevents network latency jitter.

### 3.3 Battery Health
- **Charge Threshold Enforcement**:
  - *Decision*: `/etc/udev/rules.d/99-battery-threshold.rules` sets `charge_control_start_threshold=75` and `charge_control_end_threshold=90` on `BAT0`.
  - *Rationale*: Operating lithium-ion cells at 100% continuous float voltage accelerates chemical degradation. Stopping charge at 90% and starting at 75% prolongs battery lifespan significantly.

### 3.4 Intel Graphics & Video Acceleration
- **Intel iHD VA-API**:
  - *Decision*: Force `LIBVA_DRIVER_NAME=iHD` for Intel Skylake HD Graphics 530.
  - *Rationale*: The modern `intel-media-driver` (iHD) provides superior hardware decoding support and lower CPU usage than the legacy `i965` driver.
- **Kernel Command Line Parameters**:
  - *Decision*: `i915.enable_fbc=1`, `i915.enable_guc=3`, `rcutree.enable_rcu_lazy=1`, `mem_sleep_default=deep`, `hugepages=512`.
  - *Rationale*:
    - `enable_fbc=1`: Framebuffer compression reduces memory bandwidth power draw.
    - `enable_guc=3`: Offloads graphics scheduling and video parsing to Intel GuC/HuC firmware.
    - `rcu_lazy=1`: Batches RCU callbacks to keep CPU cores in low C-states on battery.
    - `mem_sleep_default=deep`: Enforces true S3 deep sleep, preventing connected-standby battery drain while in a laptop bag.
    - `hugepages=512`: Preallocates 1GB of 2MB hugepages for virtualization and memory efficiency.

### 3.5 Wi-Fi, Audio & Boot Optimization
- **Intel Wi-Fi Aggregation & Power Scheme (`/etc/modprobe.d/iwlwifi.conf`)**:
  - *Decision*: `options iwlwifi 11n_disable=8`, `options iwlmvm power_scheme=1`.
  - *Rationale*: `11n_disable=8` enables Tx AMSDU aggregation to maximize throughput; `power_scheme=1` disables aggressive link power-down that causes Wi-Fi ping spikes.
- **Boot Acceleration & Thermals**:
  - *Decision*: Disable `NetworkManager-wait-online.service`; enable `thermald` and `mkinitcpio-numlock`.
  - *Rationale*: Eliminates boot stalling waiting on network links; `thermald` controls DPTF thermal throttling on Skylake; `mkinitcpio-numlock` guarantees NumLock state on console boot.

### 3.6 Explored & Rejected Laptop Optimisations
1. **Panel Self Refresh (PSR)**:
   - *Attempt*: `i915.enable_psr=1`.
   - *Result*: **Rejected.** Caused severe hardware screen flickering on the 1080p display panel.
2. **CPU Undervolting**:
   - *Attempt*: `-100mV` undervolt offset via `intel-undervolt`.
   - *Result*: **Rejected.** Motherboard BIOS permanently locked CPU voltage MSRs (Plundervolt microcode mitigation).
3. **Sched-ext `scx_rusty`**:
   - *Attempt*: `default_sched = "scx_rusty"`.
   - *Result*: **Rejected.** Suffered a fatal BPF compatibility crash on modern kernels (`kptr already had cpumask`). Replaced with `scx_bpfland`.

---

## 4. Architectural Summary Matrix

| Domain | Baseline Common | Desktop Profile (Zen 4) | Laptop Profile (XPS 9550) |
| :--- | :--- | :--- | :--- |
| **Package Arch** | Microarchitecture tuned | `x86_64_v4` / `cachyos-znver4` | `x86_64_v3` / `cachyos-v3` |
| **Btrfs Layout** | `@`, `@home`, `@pkg`, `@log`, `@.snapshots` | Dedicated `@games` + `/mnt/Media` (nocow) | Standard isolated subvolumes |
| **ZRAM Capacity** | `zstd` compressed swap | 100% of RAM (32GB virtual swap) | 50% of RAM (16GB virtual swap) |
| **CPU Driver / EPP** | `amd-pstate` / autonomous | `performance` (Zero-latency ramp) | Dynamic via TLP / thermald |
| **Scheduler** | Sched-ext managed | **`scx_bpfland`** (Streaming + Gaming) | **`scx_bpfland`** (Low-overhead eBPF) |
| **GPU Policy** | VA-API enabled | 310W Cap, Custom Curve, ReBAR | **ACPI Hard-off (`_OFF` power cut)** |
| **Power Management** | Disabled Wi-Fi power save | EPP profile, Solaar uinput, XHCI fix | **TLP**, 75-90% charge thresholds |
| **Streaming** | Tailscale GRO offloading | **Sunshine Host** + EDID + nft QoS | **Moonlight Client** (`moonlight-qt`) |
| **Media Automation** | None | Full Arr Stack, Jellyfin `/dev/shm` | None |
