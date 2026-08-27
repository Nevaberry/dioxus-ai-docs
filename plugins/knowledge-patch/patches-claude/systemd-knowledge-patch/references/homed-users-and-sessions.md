# Homed, Users, and Sessions

## Sleep and inhibitors

### Session freezing and sleep selection (256)

Sleep and locking a homed home freeze its user sessions. Driver packages may
set `SYSTEMD_SLEEP_FREEZE_USER_SESSIONS=false` on sleep services or
`SYSTEMD_HOME_LOCK_FREEZE_SESSION=false` on `systemd-homed.service` through
environment drop-ins.

`systemctl sleep` asks logind to select suspend-then-hibernate, suspend, hybrid
sleep, or hibernate according to `SleepOperation=` and support.
`MemorySleepMode=` in `sleep.conf` separately chooses the kernel mode.

### Inhibitors apply to privileged callers (257)

Ordinary `block` locks affect their owner and root. Bypass them explicitly
with `--force` or `--check-inhibitors=no`; `block-weak` retains the former
same-caller/root behavior. Remote users may take inhibitors through Polkit.

`HibernateOnACPower=no` suppresses the hibernate phase of
suspend-then-hibernate while AC remains connected and permits it after a
switch to battery.

### Capability results and listing (260)

Logind's `CanPowerOff()`, `CanReboot()`, `CanSuspend()`, and related calls may
return `inhibited`, `inhibitor-blocked`, or
`challenge-inhibitor-blocked`; clients must distinguish policy from temporary
locks. `systemd-inhibit --list` supports JSON and `--what=`, `--who=`,
`--why=`, and `--mode=` filters.

## PAM and session lifetime

### Lightweight session classes (258)

Root or system-account background sessions and non-root system-user sessions
default to `background-light` or `user-light`; these do not start the per-user
manager. Set PAM `class=` or `XDG_SESSION_CLASS` when a full manager is
required. `user-early-light` is also lightweight; `class=none` suppresses
logind session allocation.

### Pidfd-tied sessions (258)

Logind tracks a session with its leader pidfd. The descriptor returned by
`CreateSession()` is unused and no longer controls lifetime; leader exit ends
the session immediately.

### Scheduled maintenance and secure attention (257)

`DesignatedMaintenanceTime=` schedules shutdown. Ctrl-Alt-Shift-Esc emits
`org.freedesktop.login1.SecureAttentionKey` unless disabled, and logind can
provide session-scoped hidraw fds to unprivileged clients.

## Homed records and provisioning

### Assets, first boot, and offline updates (256)

JSON user records can reference public-blob assets such as avatars and login
backgrounds and record languages, preferred session type, and launcher.
`homectl --avatar=` and `--login-background=` manage assets;
`homectl firstboot` provisions from credentials or prompts, and
`homectl --offline` changes supported fields without unlocking the home.

### Self-service record fields and shell presentation (257)

Records declare which fields their owner may change without administrator
authentication. Ask-password has a per-user scope. Credentials
`shell.prompt.prefix`, `shell.prompt.suffix`, and `shell.welcome` become
`SHELL_PROMPT_PREFIX`, `SHELL_PROMPT_SUFFIX`, and `SHELL_PROMPT_WELCOME`.

### Quotas, aliases, and home areas (258)

Users receive per-user quotas on `/dev/shm` and tmpfs-backed `/tmp`, defaulting
to 80%; record fields `tmpLimit*`/`devShmLimit*` and homectl limit switches
customize them. `aliases`, optionally realm-qualified, are equivalent login
names.

For example, `homectl --tmp-limit=20%` changes the tmpfs quota.

Areas live below `~/Areas/`; logging in as `user%area` changes `$HOME` and
`$XDG_RUNTIME_DIR`. Use `defaultArea`, `homectl --default-area=`, or
`run0 --area=`. Areas do not isolate files from the owner UID and do not yet
support full graphical sessions or `%area` SSH syntax.

### Portable records and credential-provisioned users (258)

Homectl manages record-signing keys and can `adopt`, `register`, or
`unregister` homes. `home.add-signing-key.*` and `home.register.*` credentials
provision at boot. `userdbctl load-credentials` converts `userdb.user.*` and
`userdb.group.*` JSON credentials to static records below `/run/userdb/`.

### Recovery keys and first-boot prompts (259)

`homectl update --recovery-key=` adds a key to an existing user. Homed first
boot no longer asks for shell and supplementary groups unless prompt controls
enable those questions.

### Stable UUID lookup (259)

Records may carry a UUID; `userdbctl --uuid=` and the userdb Varlink API query
it directly.

## Privileged commands

### Run0 terminal and lightweight modes (258)

Interactive `run0` defaults to `--pty-late`, avoiding password-prompt races
before activation. It also supports `--lightweight=`, `--via-shell`,
`--chdir=~`, and `--area=`.

### Empower without changing identity (259)

`run0 --empower` retains UID and home, grants the full ambient capability set,
and joins Polkit's `empower` group. This avoids root-owned home files, but
software authorizing only UID may still reject the caller.
