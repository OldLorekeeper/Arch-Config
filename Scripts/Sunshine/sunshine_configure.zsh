#!/bin/zsh
# ------------------------------------------------------------------------------
# 3. Utility. Sunshine HDR/Resolution Configurator
# Updates monitor and mode settings in local Sunshine helper scripts.
# ------------------------------------------------------------------------------

# region Init
setopt ERR_EXIT NO_UNSET PIPE_FAIL EXTENDED_GLOB
SCRIPT_DIR=${0:a:h}
print -P "\n%K{green}%F{black} STARTING SUNSHINE CONFIGURATION %k%f\n"
# endregion

# ------------------------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------------------------

# Purpose: Locate target scripts relative to this script.

# region 1. Paths
print -P "%K{blue}%F{black} 1. PATHS %k%f\n"
HDR_SCRIPT="$SCRIPT_DIR/sunshine_hdr.zsh"
RES_SCRIPT="$SCRIPT_DIR/sunshine_res.zsh"
LAPTOP_SCRIPT="$SCRIPT_DIR/sunshine_laptop.zsh"

if [[ ! -f "$HDR_SCRIPT" || ! -f "$RES_SCRIPT" || ! -f "$LAPTOP_SCRIPT" ]]; then
    print -P "%F{red}Error: Target Sunshine scripts not found in $SCRIPT_DIR%f"
    exit 1
fi
print -P "Scripts: %F{green}Found all target scripts%f"
# endregion

# ------------------------------------------------------------------------------
# 2. Input
# ------------------------------------------------------------------------------

# Purpose: Gather monitor configuration from user.

# region 2. Input
print -P "\n%K{blue}%F{black} 2. INPUT %k%f\n"
print -P "%K{yellow}%F{black} CURRENT CONFIGURATION %k%f\n"
kscreen-doctor -o
print ""

print -P "%K{yellow}%F{black} USER ENTRY %k%f\n"
print -P "%F{yellow}Enter Monitor ID:%f"
print -P "%F{cyan}ℹ e.g. DP-1, HDMI-A-1%f\n"
read "MON_ID?Value: "

print -P "%F{yellow}Enter Target Streaming Mode Index:%f"
print -P "%F{cyan}ℹ e.g. 9%f\n"
read "STREAM_IDX?Value: "

print -P "%F{yellow}Enter Default Desktop Mode Index:%f"
print -P "%F{cyan}ℹ e.g. 1%f\n"
read "DEFAULT_IDX?Value: "

print -P "%F{yellow}Enter Laptop Streaming Mode Index [default: 13]:%f"
read "LAPTOP_IDX?Value: "
LAPTOP_IDX=${LAPTOP_IDX:-13}
# endregion

# ------------------------------------------------------------------------------
# 3. Configuration
# ------------------------------------------------------------------------------

# Purpose: Save variables to untracked display.env file.

# region 3. Configuration
print -P "\n%K{blue}%F{black} 3. CONFIGURATION %k%f\n"
if [[ -n "$MON_ID" && -n "$STREAM_IDX" && -n "$DEFAULT_IDX" ]]; then
    CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/sunshine"
    mkdir -p "$CONFIG_DIR"
    cat <<EOF > "$CONFIG_DIR/display.env"
SUNSHINE_MONITOR="$MON_ID"
SUNSHINE_STREAM_MODE="$STREAM_IDX"
SUNSHINE_DEFAULT_MODE="$DEFAULT_IDX"
SUNSHINE_LAPTOP_MODE="$LAPTOP_IDX"
EOF
    print -P "Configuration saved to: %F{cyan}$CONFIG_DIR/display.env%f"
    print -P "Status: %F{green}Configuration complete%f"
else
    print -P "%F{red}Error: Missing input.%f"
    exit 1
fi
# endregion

# ------------------------------------------------------------------------------
# End
# ------------------------------------------------------------------------------

# region End
print -P "\n%K{green}%F{black} PROCESS COMPLETE %k%f\n"
# endregion
