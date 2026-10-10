from io import StringIO
from pathlib import Path
from pyinfra.operations import files, server
from System.config import get_config

cfg = get_config()
profile = cfg["DEVICE_PROFILE"]
hostname = cfg["HOSTNAME"]

# 1. Timezone & Clock
files.link(
    name="Set timezone to Europe/London",
    path="/etc/localtime",
    target="/usr/share/zoneinfo/Europe/London",
    symbolic=True,
)
server.shell(
    name="Sync hardware clock",
    commands=["hwclock --systohc"],
)

# 2. Locale & Console
files.line(
    name="Ensure en_GB.UTF-8 in /etc/locale.gen",
    path="/etc/locale.gen",
    line="en_GB.UTF-8 UTF-8",
)
files.line(
    name="Ensure en_US.UTF-8 in /etc/locale.gen",
    path="/etc/locale.gen",
    line="en_US.UTF-8 UTF-8",
)
server.shell(
    name="Generate locales",
    commands=["locale-gen"],
)
files.put(
    name="Configure /etc/locale.conf",
    dest="/etc/locale.conf",
    src=StringIO("LANG=en_GB.UTF-8\n"),
)
files.put(
    name="Configure /etc/vconsole.conf",
    dest="/etc/vconsole.conf",
    src=StringIO("KEYMAP=uk\nXKBLAYOUT=gb\nXKBMODEL=pc105\nXKBOPTIONS=terminate:ctrl_alt_bksp\n"),
)

# 3. Hostname & Hosts
files.put(
    name="Configure /etc/hostname",
    dest="/etc/hostname",
    src=StringIO(f"{hostname}\n"),
)
hosts_content = f"""127.0.0.1   localhost
::1         localhost
127.0.1.1   {hostname}.localdomain {hostname}
"""
files.put(
    name="Configure /etc/hosts",
    dest="/etc/hosts",
    src=StringIO(hosts_content),
)

# 4. Makepkg Tuning
server.shell(
    name="Normalize multiline CFLAGS in /etc/makepkg.conf",
    commands=[
        r"""python3 -c '
from pathlib import Path
import re
p = Path("/etc/makepkg.conf")
if p.exists():
    content = p.read_text()
    new_content = re.sub(r"^#*CFLAGS=\".*?(?<!\\)\"", "CFLAGS=\"-march=native -O2 -pipe -fno-plt -fexceptions -Wp,-D_FORTIFY_SOURCE=3 -Wformat -Werror=format-security -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer\"", content, flags=re.MULTILINE | re.DOTALL)
    if new_content != content:
        p.write_text(new_content)
'"""
    ],
)
files.line(
    name="Tune makepkg native architecture",
    path="/etc/makepkg.conf",
    line=r"^#*CFLAGS=.*",
    replace='CFLAGS="-march=native -O2 -pipe -fno-plt -fexceptions -Wp,-D_FORTIFY_SOURCE=3 -Wformat -Werror=format-security -fstack-clash-protection -fcf-protection -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer"',
)
files.line(
    name="Tune makepkg multi-core flags",
    path="/etc/makepkg.conf",
    line=r"^#*MAKEFLAGS=.*",
    replace='MAKEFLAGS="-j$(nproc)"',
)
files.line(
    name="Tune makepkg zstd compression",
    path="/etc/makepkg.conf",
    line=r"^#*COMPRESSZST=.*",
    replace="COMPRESSZST=(zstd -c -z -q -T0 -3 -)",
)
files.line(
    name="Tune makepkg native rust target",
    path="/etc/makepkg.conf",
    line='RUSTFLAGS="-C target-cpu=native"',
)
files.line(
    name="Tune makepkg build directory to tmpfs",
    path="/etc/makepkg.conf",
    line=r"^#*BUILDDIR=.*",
    replace="BUILDDIR=/tmp/makepkg",
)

# 5. Pacman & CachyOS Repositories
parallel_dl = "10" if profile == "desktop" else "5"
arch_v = "x86_64_v4" if profile == "desktop" else "x86_64_v3"

files.line(
    name="Configure pacman parallel downloads",
    path="/etc/pacman.conf",
    line=r"^#*ParallelDownloads\s*=.*",
    replace=f"ParallelDownloads = {parallel_dl}",
)
files.line(
    name="Enable pacman color output",
    path="/etc/pacman.conf",
    line=r"^#*Color",
    replace="Color",
)
files.line(
    name="Configure pacman architecture target",
    path="/etc/pacman.conf",
    line=r"^#*Architecture\s*=.*",
    replace=f"Architecture = auto {arch_v}",
)
server.shell(
    name="Enable multilib repository in /etc/pacman.conf",
    commands=[
        "sed -i '/\\[multilib\\]/,/Include/s/^#//' /etc/pacman.conf"
    ],
)

# CachyOS & LizardByte Repositories block
cachy_block = """
[cachyos-znver4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist

[cachyos-core-znver4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist

[cachyos-extra-znver4]
Include = /etc/pacman.d/cachyos-v4-mirrorlist

[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist
""" if profile == "desktop" else """
[cachyos-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist

[cachyos-core-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist

[cachyos-extra-v3]
Include = /etc/pacman.d/cachyos-v3-mirrorlist

[cachyos]
Include = /etc/pacman.d/cachyos-mirrorlist
"""

lizardbyte_block = """
[lizardbyte]
SigLevel = Optional
Server = https://github.com/LizardByte/pacman-repo/releases/latest/download
"""

server.shell(
    name="Normalize existing CachyOS and LizardByte repository blocks in /etc/pacman.conf",
    commands=[
        r"""python3 -c '
from pathlib import Path
import re
p = Path("/etc/pacman.conf")
if p.exists():
    text = p.read_text()
    parts = re.split(r"(# BEGIN (?:CACHYOS REPOSITORIES|LIZARDBYTE REPOSITORY))", text, maxsplit=1)
    unmanaged = parts[0]
    managed = "".join(parts[1:]) if len(parts) > 1 else ""
    unmanaged = re.sub(r"\[lizardbyte\][^\[]*", "", unmanaged, flags=re.MULTILINE)
    unmanaged = re.sub(r"\[cachyos(?:-[^\]]+)?\][^\[]*", "", unmanaged, flags=re.MULTILINE)
    new_text = unmanaged.rstrip() + "\n\n" + managed.lstrip()
    if new_text != text:
        p.write_text(new_text)
'"""
    ],
)

files.block(
    name="Ensure CachyOS repositories in /etc/pacman.conf",
    path="/etc/pacman.conf",
    content=cachy_block.strip(),
    marker="# {mark} CACHYOS REPOSITORIES",
)

files.block(
    name="Ensure LizardByte repository in /etc/pacman.conf",
    path="/etc/pacman.conf",
    content=lizardbyte_block.strip(),
    marker="# {mark} LIZARDBYTE REPOSITORY",
)

