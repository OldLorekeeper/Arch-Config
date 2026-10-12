# ASUS AM5 UEFI Tuning Guide (ROG STRIX X670E-I)

This guide provides a step-by-step walkthrough to transition from factory defaults (`F5: Load Optimized Defaults`) to the fully verified hardware baseline. 

### Target Hardware Profile
- **Motherboard**: ASUS ROG STRIX X670E-I GAMING WIFI (Firmware 3881 / AGESA 1.2.0.2)
- **CPU**: AMD Ryzen 7 7800X3D (8 Cores / 16 Threads)
- **Memory**: 32 GB Corsair Vengeance DDR5-6000 CL36 (`16Gb Samsung B-die`)
- **Discrete GPU**: AMD Radeon RX 7900 XTX (PCIe Gen 4/5 $\times$16)

---

## 1. Initial Reset

1. Power on or reboot the machine and tap `Del` or `F2` to enter the UEFI interface.
2. Press `F5` $\rightarrow$ Select **OK** to load **Optimized Defaults** (clean baseline).
3. Press `F7` to switch from EZ Mode to **Advanced Mode**.

---

## 2. Menu Walkthrough: Default to Optimal

Follow each section by navigating across the top tabs and submenus in order.

### Tab 1: `Ai Tweaker` (Main Page)

| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **Ai Overclock Tuner** | `Auto` | `DOCP I` *(or `EXPO I`)* | Dynamically displays `DOCP I` for Intel XMP DIMMs (like this Corsair kit) or `EXPO I` for AMD EXPO DIMMs. Automatically populates rated primary timings (36-48-48-104) and DRAM voltages (1.40V VDD/VDDQ). |
| **Memory Frequency** | `Auto` | `DDR5-6000MHz` | Automatically set by DOCP I / EXPO I. |
| **FCLK Frequency** | `Auto` *(2000 MHz)* | `2133 MHz` | Located directly beneath Memory Frequency. Unlocks Infinity Fabric interconnect bandwidth. |
| **CPU SoC Voltage** | `Auto` | `Manual Mode` | Scroll down to the voltage section. |
| **- VDDCR SoC Voltage Override** | `Auto` | `1.22000` | Type `1.22000` into the numeric field. Optimal floor for 2133 MHz FCLK on Samsung ICs while safeguarding 3D V-Cache. |

---

### Tab 1, Submenu A: `Ai Tweaker` $\rightarrow$ `DRAM Timing Control`

Navigate to `DRAM Timing Control` from the main `Ai Tweaker` page:

| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **Memory Context Restore** | `Auto` | `Enabled` | Skips memory retraining on subsequent boots. Cuts POST time from ~45s to ~10s. |
| **Power Down Enable** | `Auto` | `Enabled` | Must match `Memory Context Restore`. Prevents sleep/resume training crashes on AM5. |
| **UCLK DIV1 MODE** | `Auto` | `UCLK=MEMCLK` | Locks memory controller to 1:1 mode (3000 MHz); avoids 1:2 latency penalties. |

*(Leave all primary, secondary, and turnaround timings on `Auto`—ASUS automatically trains safe Samsung B-die timings with maximum refresh interval `tREFI = 65535`.)*

Press `Esc` to return to `Ai Tweaker`.

---

### Tab 1, Submenu B: `Ai Tweaker` $\rightarrow$ `Precision Boost Overdrive`

Navigate to `Precision Boost Overdrive` from the main `Ai Tweaker` page:

| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **Precision Boost Overdrive** | `Auto` | `Enhancement` | Uncaps motherboard socket power limits (PPT, TDC, EDC) and reveals thermal targets. |
| **Thermal Limit** | `Level 2 (80°C)` | `Level 2 (80°C)` | Capped at 80°C to maintain high efficiency and silent acoustics. *(Select `Level 1 (90°C)` if cooler headroom permits)*. |

Now enter the nested **`Curve Optimizer`** submenu:

| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **Curve Optimizer** | `Auto` | `All Cores` | Enables undervolt offset across all 8 cores. |
| **All Core Curve Optimizer Sign** | `Positive` | `Negative` | Reduces voltage request across the entire V/F curve. |
| **All Core Curve Optimizer Magnitude** | `0` | `25` | Type `25`. Sustains ~5,050 MHz boost clock under load. |

Press `Esc` twice to return to the top-level menu bar.

---

### Tab 2: `Advanced`

Navigate to the **`Advanced`** tab:

#### Submenu A: `Advanced` $\rightarrow$ `NB Configuration`
| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **Integrated Graphics** | `Auto` *(Active)* | `Disabled` | Dedicated RX 7900 XTX is present. Disabling reclaims 512MB–2GB of system RAM and lowers SoC thermals. |

Press `Esc` to return to `Advanced`.

#### Submenu B: `Advanced` $\rightarrow$ `Onboard Devices Configuration`
| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **When system is in sleep, hibernate or soft off states** | `Onboard LED on` | `Onboard LED off` | Disables motherboard standby and decorative LEDs when the machine is shut down. |
| **USB power delivery in Soft Off state (S5)** | `Enabled` | `Disabled` | Cuts 5V power to USB ports when shut down; prevents keyboards, mice, and DACs from glowing. |

Press `Esc` to return to `Advanced`.

#### Submenu C: `Advanced` $\rightarrow$ `APM Configuration`
| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **ErP Ready** | `Disabled` | `Enable(S4+S5)` | Ensures European ErP standard compliance; drops shutdown power draw below 0.5W. |

Press `Esc` to return to the top-level menu bar.

---

---
 
### Tab 3: `Monitor` $\rightarrow$ `Q-Fan Configuration`
 
Navigate to the **`Monitor`** tab $\rightarrow$ `Q-Fan Configuration`:
 
| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **CPU Fan Profile** | `Standard` | `Silent` | Lowers baseline acoustic floor under ambient workloads. |
| **CPU Fan Step Up** | `Level 0` | `Level 4` | Adds delay hysteresis. Prevents rapid fan revving during transient Ryzen 7000 boost spikes. |
| **CPU Fan Step Down** | `Level 0` | `Level 2` | Smooths fan spin-down transitions. |
| **Chassis Fan Profile** | `Standard` | `Silent` | Reduces case fan noise floor. |
| **Chassis Fan Step Up** | `Level 0` | `Level 4` | Prevents case fan pulsing during momentary CPU loads. |
| **Chassis Fan Step Down** | `Level 0` | `Level 2` | Smooths fan spin-down transitions. |
| **AIO Pump Profile** | `Full Speed` | `Manual` | Permits custom thermal point mappings instead of running pump at 100% whine continuously. |
| **AIO Pump Step Up** | `Level 0` | `Level 4` | Dampens pump acoustic ramps during transient heat bursts. |
| **AIO Pump Step Down** | `Level 0` | `Level 2` | Smooths pump deceleration. |
| **AIO Pump Point 1** | `20°C / 80%` | `30°C / 20%` | Whisper-quiet idle operation. |
| **AIO Pump Point 2** | `N/A / 85%` | `N/A / 40%` | Moderate low-load curve. |
| **AIO Pump Point 3** | `60°C / 90%` | `70°C / 70%` | Smooth medium-load transition. |
| **AIO Pump Point 4** | `70°C / 100%` | `75°C / 100%` | Full cooling performance only engaged above 75°C. |

---

### Tab 4: `Boot`

Navigate to the **`Boot`** tab:

| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **POST Delay Time** | `3 sec` | `1 sec` | Eliminates unnecessary delay during bootloader handover. |
| **Wait For [F1] If Error** | `Enabled` | `Disabled` | Prevents boot hangs on minor non-fatal hardware warnings (e.g. low chassis fan RPM). |

#### Submenu: `Boot` $\rightarrow$ `Secure Boot`
| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **OS Type** | `Windows UEFI mode` | `Other OS` | Disables strict Microsoft key enforcement for native Linux systemd-boot compatibility. |

Press `Esc` to return to the top-level menu bar.

---

### Tab 5: `Tool`

Navigate to the **`Tool`** tab:

#### Submenu: `Tool` $\rightarrow$ `ASUS Armoury Crate`
| Setting Name | Default Value | Optimal Value | Notes |
| :--- | :--- | :--- | :--- |
| **Download & Install ARMOURY CRATE app** | `Enabled` | `Disabled` | Prevents the UEFI firmware from injecting Windows executable binaries into ACPI WPBT tables. |

#### Submenu: `Tool` $\rightarrow$ `ASUS User Profile`
1. Enter `ASUS User Profile`.
2. Under `Profile 1 status:`, enter `Profile Name: Stable-Baseline`.
3. Select `Save to Profile 1`.
> [!TIP]
> Saving to an internal CMOS profile slot allows instant recovery if settings are ever accidentally cleared or if testing future adjustments.

---

## 3. Save, Verification & Exit

1. Press `F10` to open the **Save Changes & Reset** dialogue.
2. Verify that the pending changes review list matches the following checklist:

```text
Ai Overclock Tuner: Auto -> DOCP I
Memory Frequency: Auto -> DDR5-6000MHz
FCLK Frequency: Auto -> 2133 MHz
Memory Context Restore: Auto -> Enabled
Power Down Enable: Auto -> Enabled
UCLK DIV1 MODE: Auto -> UCLK=MEMCLK
Tcl: Auto -> 36
Trcd: Auto -> 48
Trp: Auto -> 48
Tras: Auto -> 104
Precision Boost Overdrive: Auto -> Enhancement
Thermal Limit: Level 2 (80°C)
Curve Optimizer: Auto -> All Cores
All Core Curve Optimizer Sign: Positive -> Negative
All Core Curve Optimizer Magnitude: 0 -> 25
CPU SOC Voltage: Auto -> Manual Mode
- VDDCR SOC Voltage Override: Auto -> 1.22000
DRAM VDD Voltage: Auto -> 1.40000
DRAM VDDQ Voltage: Auto -> 1.40000
PMIC Voltages: Auto -> Sync All PMICs
Integrated Graphics: Auto -> Disabled
When system is in sleep, hibernate or soft off states: Onboard LED on -> Onboard LED off
USB power delivery in Soft Off state (S5): Enabled -> Disabled
ErP Ready: Disabled -> Enable(S4+S5)
CPU Fan Profile: Standard -> Silent
CPU Fan Step Up: Level 0 -> Level 4
CPU Fan Step Down: Level 0 -> Level 2
Chassis Fan Profile: Standard -> Silent
Chassis Fan Step Up: Level 0 -> Level 4
Chassis Fan Step Down: Level 0 -> Level 2
AIO Pump Profile: Full Speed -> Manual
AIO Pump Step Up: Level 0 -> Level 4
AIO Pump Step Down: Level 0 -> Level 2
AIO Pump Point4 Temperature: 70 -> 75
AIO Pump Point3 Temperature: 60 -> 70
AIO Pump Point3 Duty Cycle (%): 90 -> 70
AIO Pump Point2 Duty Cycle (%): 85 -> 40
AIO Pump Point1 Temperature: 20 -> 30
AIO Pump Point1 Duty Cycle (%): 80 -> 20
POST Delay Time: 3 sec -> 1 sec
Wait For [F1] If Error: Enabled -> Disabled
OS Type: Windows UEFI mode -> Other OS
Download & Install ARMOURY CRATE app: Enabled -> Disabled
```

3. Select **OK** / Press `Enter` to commit changes and reboot.

---

## 4. Post-Boot Linux Verification

Once booted into Arch Linux, verify that all settings took effect:

```bash
# 1. Verify Memory Speed (Should report 6000 MT/s)
sudo dmidecode --type memory | grep -E "Speed:|Configured Memory Speed:"

# 2. Verify SoC Voltage & Rail Status
sensors

# 3. Check Sustained Boost Clocks Under Load (~5,050 MHz)
watch -n 1 "grep 'cpu MHz' /proc/cpuinfo | sort -n"

# 4. Verify iGPU is completely disabled (Should only list Navi 31 [Radeon RX 7900 XTX])
lspci | grep -E "VGA|Display"
```
