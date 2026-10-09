from io import StringIO
from pyinfra.operations import files, server
from System.config import get_config

cfg = get_config()
target_user = cfg["TARGET_USER"]

# 1. Groups
for grp in ["polkit", "media", "gamemode", "realtime"]:
    server.group(
        name=f"Ensure group {grp}",
        group=grp,
        present=True,
    )

# 2. Target User
user_groups = ["wheel", "input", "render", "video", "storage", "gamemode", "libvirt", "realtime", "media"]

server.user(
    name=f"Ensure user {target_user}",
    user=target_user,
    shell="/bin/zsh",
    groups=user_groups,
    present=True,
)

# Passwords (applied during fresh install if secrets loaded)
root_pass = cfg.get("ROOT_PASS")
user_pass = cfg.get("USER_PASS")
if root_pass:
    server.shell(
        name="Set root password",
        commands=[f'echo "root:{root_pass}" | chpasswd'],
    )
if user_pass:
    server.shell(
        name=f"Set password for {target_user}",
        commands=[f'echo "{target_user}:{user_pass}" | chpasswd'],
    )


# 3. Sudoers
files.put(
    name="Configure wheel sudo permissions",
    dest="/etc/sudoers.d/wheel",
    src=StringIO("%wheel ALL=(ALL:ALL) ALL\n"),
    mode="0440",
)

files.put(
    name="Configure custom sudo password prompt",
    dest="/etc/sudoers.d/custom_prompt",
    src=StringIO('Defaults passprompt="Enter sudo password to continue: "\n'),
    mode="0440",
)

# 4. Games Directory
files.directory(
    name="Ensure Games directory exists",
    path=f"/home/{target_user}/Games",
    user=target_user,
    group=target_user,
    mode="0755",
    present=True,
)
