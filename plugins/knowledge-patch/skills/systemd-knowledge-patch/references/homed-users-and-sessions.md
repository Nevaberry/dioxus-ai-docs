# Homed, Users, and Sessions

## Provision and update homed accounts

- JSON user records can refer to public blob directories for avatars and login backgrounds. `homectl --avatar=` and `--login-background=` manage them; records can also store extra languages and preferred session type or launcher (since 256).
- `homectl firstboot` provisions accounts from credentials or interactive prompts. `homectl --offline` changes supported fields without unlocking the home (since 256).
- A record can declare which fields its owner may change without administrator authentication; homed enforces that self-service allowlist (since 257).
- Homectl can manage record-signing keys and `adopt`, `register`, or `unregister` an existing home. Boot credentials named `home.add-signing-key.*` and `home.register.*` provision keys and records (since 258).
- `userdbctl load-credentials` converts `userdb.user.*` and `userdb.group.*` JSON credentials into static records under `/run/userdb/` (since 258).
- Existing accounts can add a recovery key through `homectl update --recovery-key=`. Homed first boot no longer asks for a login shell or supplementary groups unless its prompt controls enable those questions (since 259).
- User records can carry a stable UUID. Find it with `userdbctl --uuid=`; the userdb Varlink API supports server-side UUID queries (since 259).

## Use aliases, quotas, and home areas

- User records can expose `aliases`, optionally qualified by `realm`, as equivalent login names (since 258).
- Users receive per-user quotas on `/dev/shm` and tmpfs-backed `/tmp`, defaulting to 80%. Record fields `tmpLimit*` and `devShmLimit*`, or switches such as `homectl --tmp-limit=20%`, customize them (since 258).
- Alternate environments live below `~/Areas/` and are selected by logging in as `user%area`. They change both `$HOME` and `$XDG_RUNTIME_DIR`; `defaultArea`, `homectl --default-area=`, and `run0 --area=` select them (since 258).
- Areas do not isolate data from the owning UID and do not yet support complete graphical sessions or `%area` SSH login syntax.

## Manage sessions and PAM classes

- Locking a homed-managed home freezes associated sessions. If a driver cannot tolerate this, set `SYSTEMD_HOME_LOCK_FREEZE_SESSION=false` in a `systemd-homed.service` environment drop-in (since 256).
- Homed homes can be unlocked during SSH login through userdb authorized-key integration (since 256).
- Root or system-account background sessions and non-root system-user sessions default to `background-light` or `user-light`. Cron- and FTP-style PAM sessions no longer start a per-user manager unless `class=` or `XDG_SESSION_CLASS` requests it (since 258).
- Logind tracks a session with the leader's pidfd; the descriptor returned by `CreateSession()` is unused, and leader exit immediately stops the session. `user-light` and `user-early-light` avoid a user manager; `class=none` suppresses logind allocation (since 258).

## Work with inhibitors and power actions

- Ordinary `block` inhibitors affect the process that took the lock and root callers. Bypass explicitly with `--force` or `--check-inhibitors=no`; `block-weak` retains the earlier same-caller/root behavior. Remote users may take inhibitors subject to Polkit (since 257).
- Logind's `CanPowerOff()`, `CanReboot()`, `CanSuspend()`, and related methods can return `inhibited`, `inhibitor-blocked`, or `challenge-inhibitor-blocked`; clients must handle all results and distinguish policy from temporary locks (since 260).
- `systemd-inhibit --list` supports JSON and filters `--what=`, `--who=`, `--why=`, and `--mode=` (since 260).
- `DesignatedMaintenanceTime=` schedules shutdown at a maintenance window (since 257).
- Ctrl-Alt-Shift-Esc emits `org.freedesktop.login1.SecureAttentionKey` for a trusted login UI unless disabled in logind configuration (since 257).

## Select sleep behavior

- `systemctl sleep` asks logind to choose suspend-then-hibernate, suspend, hybrid sleep, or hibernate according to support and `SleepOperation=`. `MemorySleepMode=` independently chooses the kernel memory-sleep mode (since 256).
- Sleep freezes user sessions. A driver package can set `SYSTEMD_SLEEP_FREEZE_USER_SESSIONS=false` on the sleep services through environment drop-ins (since 256).
- `HibernateOnACPower=no` in `sleep.conf` prevents the hibernate phase of suspend-then-hibernate while AC remains connected, then allows it after switching to battery (since 257).

## Run commands as another user

- Interactive `run0` defaults to `--pty-late`, delaying terminal forwarding until activation so password prompts do not race for the TTY. It also supports `--lightweight=`, `--via-shell`, and `--chdir=~` (since 258).
- `run0 --empower` keeps the caller's UID and home, grants the full ambient capability set, and adds the process to the `empower` group recognized by Polkit. UID-only authorization checks may still reject it (since 259).
- `run0 --same-root-dir` reuses the caller's root tree, and `run0 --area=` enters a homed area (since 259 and 258).
- The ask-password mechanism has a per-user scope (since 257).
- Login credentials `shell.prompt.prefix`, `shell.prompt.suffix`, and `shell.welcome` become `SHELL_PROMPT_PREFIX`, `SHELL_PROMPT_SUFFIX`, and `SHELL_PROMPT_WELCOME` for customized prompts and welcome text (since 257).
