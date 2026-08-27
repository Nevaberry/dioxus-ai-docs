# Homed, Users, and Sessions

## Session lifecycle and sleep

### Freeze behavior for sleep and homed (256)

Sleep and locking a homed-managed home freeze associated user sessions.
Drivers that cannot tolerate freezing can set
`SYSTEMD_SLEEP_FREEZE_USER_SESSIONS=false` on sleep services or
`SYSTEMD_HOME_LOCK_FREEZE_SESSION=false` on homed via environment drop-ins.

### Policy-driven sleep (256, 257)

`systemctl sleep` asks logind to select suspend-then-hibernate, suspend,
hybrid sleep, or hibernate according to `SleepOperation=` and availability;
`MemorySleepMode=` independently selects the kernel memory sleep mode.
`HibernateOnACPower=no` delays the hibernate phase of suspend-then-hibernate
until AC is disconnected.

### Lightweight PAM sessions (258)

Root/system-account background sessions and non-root system-user sessions use
`background-light` or `user-light`, so cron/FTP-like PAM sessions do not start
a user manager. Set PAM `class=` or `XDG_SESSION_CLASS` when one is required.
`user-early-light` is also available; `class=none` suppresses logind session
allocation.

### Pidfd-tied logind sessions (258)

The descriptor returned by `CreateSession()` is unused. Logind tracks the
leader by pidfd and ends the session immediately when that leader exits; do
not use the old descriptor as a lifetime anchor.

## Inhibitors and privilege

### Block inhibitors apply to everyone (257)

Ordinary `block` locks affect their own holder and root. Privileged callers
must use `--force` or `--check-inhibitors=no` to bypass them. `block-weak`
retains the former same-caller/root exception. Remote users can acquire locks
subject to Polkit.

### Power capability results and listings (260)

Logind `CanPowerOff()`, `CanReboot()`, `CanSuspend()`, and related methods may
return `inhibited`, `inhibitor-blocked`, or `challenge-inhibitor-blocked`;
clients must distinguish policy and temporary locks. `systemd-inhibit --list`
supports JSON and `--what=`, `--who=`, `--why=`, and `--mode=` filters.

### `run0` late PTYs and execution modes (258)

Interactive run0 defaults to `--pty-late`, avoiding activation/password prompt
races. It also supports `--lightweight=`, `--via-shell`, and `--chdir=~`.

### Empower without changing identity (259)

`run0 --empower` keeps the caller's UID and home, grants the full ambient
capability set, and joins the Polkit-recognized `empower` group. This avoids
root-owned home files, though UID-only authorization may still reject it.

## Homed records and provisioning

### Provisioning and richer records (256)

User records can reference public blob directories for avatars/backgrounds
and record languages and preferred session type/launcher. Use
`homectl --avatar=` and `--login-background=`. `homectl firstboot` provisions
from credentials or prompts; `homectl --offline` changes supported properties
without unlocking the home.

### User-controlled fields (257)

Records can declare an allowlist of fields that their owner may change without
administrator authentication; homed enforces it.

### Per-user prompts and shell presentation (257)

Ask-password supports per-user scope. Credentials `shell.prompt.prefix`,
`shell.prompt.suffix`, and `shell.welcome` become `SHELL_PROMPT_PREFIX`,
`SHELL_PROMPT_SUFFIX`, and `SHELL_PROMPT_WELCOME` at login.

### Home areas and aliases (258)

Alternate environments live below `~/Areas/` and are selected as `user%area`,
with `defaultArea`/`homectl --default-area=` or `run0 --area=`. An area changes
`$HOME` and `$XDG_RUNTIME_DIR` but is not UID-level isolation; full graphical
sessions and `%area` SSH syntax are unsupported. Records also support aliases,
optionally realm-qualified.

### Per-user tmpfs quotas (258)

Users receive 80%-default per-user quotas on `/dev/shm` and tmpfs `/tmp`.
Customize through `tmpLimit*`/`devShmLimit*` record fields or homectl options
such as `--tmp-limit=20%`.

### Portable records and boot credentials (258)

Homectl manages signing keys and can `adopt`, `register`, or `unregister`
existing homes. Credentials named `home.add-signing-key.*` and
`home.register.*` provision at boot. `userdbctl load-credentials` materializes
`userdb.user.*` and `userdb.group.*` JSON credentials in `/run/userdb/`.

### Stable UUID lookup (259)

User records can carry UUIDs. Query with `userdbctl --uuid=`; userdb Varlink
also performs server-side UUID queries.

### Recovery keys and first-boot prompts (259)

`homectl update --recovery-key=` adds a key to an existing user. First-boot
homed asks about shell and supplementary groups only when its prompt controls
enable those questions.
