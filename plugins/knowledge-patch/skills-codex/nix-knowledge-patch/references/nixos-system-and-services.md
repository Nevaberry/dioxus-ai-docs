# NixOS System and Service Migrations

## Rebuild, evaluation, and switching

### Rebuild command transition (since nixos-25.05, nixos-25.11)

The Python `nixos-rebuild-ng` was initially selected with
`system.rebuild.enableNg = true` or installed in `environment.systemPackages`
beside the old command. It is the default in 25.11;
`system.rebuild.enableNg = false` is only a temporary opt-out. The option was
expected to disappear in 26.05. `nixos-rebuild build-image` builds the
platform image exposed by the selected configuration, and both
implementations support it.

### Flake-aware option inspection (since nixos-25.05)

`nixos-option` supports flake configurations, descent into `attrsOf` and
`listOf` submodules, and `--show-trace`.

### Valid state-version syntax (since nixos-25.05)

`system.stateVersion` must use a NixOS release string in `"YY.MM"` form. Do
not advance it merely to adopt a newer Nixpkgs revision.

### Rust-only switching (since nixos-25.11)

The Perl `switch-to-configuration` implementation is gone. Remove
`system.switch.enableNg`; every switchable system uses the Rust rewrite.

### Channel-free system entry points (since nixos-26.05)

`/etc/nixos/system.nix` may evaluate directly to one NixOS system derivation
or to an attribute set selected by `nixos-rebuild --attr`. `--file` selects
another file or directory, and `--attr` also considers `./system.nix`. This
supports a pinned entry point without `nix-channel`.

### Switch inhibitors and unit activation (since nixos-26.05)

Switch inhibitors reject a generation when configured comparison strings
differ; `NIXOS_NO_CHECK=1` forces the switch. A unit is reloaded when its only
change is `ExecReload=`, while removing `ExecReload=` causes no action.
Activation-script-driven reloads and restarts are deprecated.

## Boot, initrd, filesystems, and images

### Overriding module filesystems (since nixos-25.05)

NixOS-provided `fileSystems` entries use `lib.mkDefault`, so they can be
replaced wholesale. Overriding only `fsType` or `options` can discard the
required `device`; restate it explicitly.

### Image file names (since nixos-25.05)

Default filenames from `system.build` image builders changed. Customize them
with `image.baseName`, `image.extension`, and `image.fileName`;
`image.filePath` exposes the evaluation-time output-relative path.

### System Mesa selection (since nixos-25.05)

`hardware.graphics.package` selects the global Mesa version without forcing a
mass rebuild.

### Bashless systemd initrd initialization (since nixos-25.11)

`system.nixos-init.enable = true` selects the Rust `nixos-init`, allowing a
systemd initrd without an interpreter.

### Nix store mount options (since nixos-25.11)

`boot.readOnlyNixStore` was removed. Configure the `/nix/store` bind mount
with `boot.nixStoreMountOpts`.

### Systemd stage 1 by default (since nixos-26.05)

The systemd initrd is the default; scripted stage 1 is deprecated for removal
and can be retained temporarily with `boot.initrd.systemd.enable = false`.
LUKS roots should name `/dev/mapper/...`, `/dev/root` must become a stable
device path, and complex LVM-on-LUKS layouts may need an infinite systemd
device timeout.

## Networking, firewall, and name resolution

### Explicit online ordering (since nixos-25.05)

`multi-user.target` is not ordered after `network-online.target`. A service
that requires connectivity must declare both `wants` and `after` for
`network-online.target`.

### NAT address filtering (since nixos-25.05)

When `networking.nat.externalIP` or `externalIPv6` is set, `forwardPorts`
under `networking.nat` matches only packets addressed to that external
address.

### Networkd WireGuard backend (since nixos-25.05)

`networking.wireguard` selects its networkd backend automatically when
`networking.useNetworkd` is enabled, or explicitly with
`networking.wireguard.useNetworkd`. Its option semantics can differ from the
scripted backend.

### FirewallD and backend selection (since nixos-25.11)

Use `services.firewalld` directly or select FirewallD as the backend for
`networking.firewall` with `networking.firewall.backend`.

### Explicit NetworkManager VPN plugins (since nixos-25.11)

The NetworkManager module has no default VPN plugin set. List every required
plugin in `networking.networkmanager.plugins`.

### Hardened wireless configuration (since nixos-26.05)

`wpa_supplicant` runs unprivileged and its generated or imperative files move
under `/etc/wpa_supplicant`; referenced credentials must be readable by that
user. Remove `networking.wireless.userControlled.group` and rename
`.userControlled.enable` to `.userControlled`. NetworkManager relies on
`networking.wireless`, so remove an explicit `networking.wireless.enable =
false`. `networking.wireless.enableHardening` is a temporary escape hatch;
`iw` and `wirelesstools` are no longer implicit packages.

### Asynchronous network setup and resolvconf (since nixos-26.05)

The scripted backend no longer has `network-setup.service`; addresses, routes,
and gateways are applied as devices appear. Name-server setup runs in
`network-local-commands.service`. `networking.resolvconf.enable` always
defaults to `true`, so systems that provide `/etc/resolv.conf` must disable it.

### Firewall refusal logging (since nixos-26.05)

`networking.firewall.logRefusedConnections` defaults to `false`. Enable it
explicitly when refused-packet logs are required.

## Core system services and settings

### Locale configuration (since nixos-25.05)

Prefer `i18n.extraLocales` to install additional locales.
`i18n.supportedLocales` still works but is an implementation detail and warns
when required locales are absent. Use `i18n.defaultCharset` and
`i18n.localeCharsets` for per-locale character-set selection.

### Structured settings migrations (since nixos-25.11, nixos-26.05)

Move free-form or flat configuration into typed settings:

- `services.dwm-status.extraConfig` becomes `services.dwm-status.settings`,
  with `order` nested.
- `services.traccar.settings.loggerConsole` becomes
  `services.traccar.settings.logger.console`.
- `services.logind.extraConfig` becomes `services.logind.settings.Login`.
- `systemd.extraConfig` and `boot.initrd.systemd.extraConfig` become the
  corresponding `systemd.settings.Manager` values.
- Watchdogs use `RuntimeWatchdogSec`, `WatchdogDevice`, `RebootWatchdogSec`,
  and `KExecWatchdogSec`; replace `systemd.enableCgroupAccounting` with the
  individual `*Accounting` manager settings.
- `systemd.coredump.extraConfig` becomes
  `systemd.coredump.settings.Coredump`, and `systemd.sleep.extraConfig`
  becomes `systemd.sleep.settings.Sleep`.
- `services.pdns-recursor.yaml-settings` becomes
  `services.pdns-recursor.settings`; resolved and Dovecot likewise expose RFC
  42-style settings.

### D-Bus broker default (since nixos-26.05)

`services.dbus.implementation` defaults to `dbus-broker`. Switching the
implementation is inhibited during live activation and requires a reboot;
set it to `"dbus"` to retain the reference daemon.

### Container-backed NixOS tests (since nixos-26.05)

The integration-test driver can use `systemd-nspawn` instead of QEMU. This
works on VM builders without KVM and for tests bind-mounting host devices such
as GPUs.

### Stricter core option types (since nixos-26.05)

`services.openssh.settings.AcceptEnv` is a list, every
`fileSystems.<name>.fsType` must be explicit, and unknown
`services.xserver.videoDriver(s)` values fail evaluation.

## Security, identity, and certificates

### AppArmor policy state (since nixos-25.05)

The `enable` and `enforce` fields below `security.apparmor.policies.<name>`
were removed. Use the `state` tristate.

### Earlyoom hardening and argument escaping (since nixos-25.05)

The module uses upstream's hardened systemd unit. A `killHook` needing home or
filesystem access may require a `ProtectSystem` override. Each `extraArgs`
element is escaped independently; it is not word-split.

### OpenSSH module updates (since nixos-26.05)

`services.openssh.generateHostKeys = true` can generate keys while the daemon
is disabled. Set `enableRecommendedAlgorithms = false` to opt out of the
curated algorithms. Replace `services.openssh.banner` with
`services.openssh.settings.Banner`.

### ACME dependencies and renewal (since nixos-25.11, nixos-26.05)

Services requiring a syntactically valid certificate should depend on
`acme-{certname}.service`; initial self-signed certificates are always made,
`security.acme.preliminarySelfsigned` is removed, and dependencies on
`acme-finished-{certname}.target` move to
`acme-order-renew-{certname}.service`. When `validMinDays` is unset,
certificates lasting at least ten days renew after two thirds of their
lifetime and shorter certificates halfway through.

### Secret-file migrations (since nixos-26.05)

Replace `services.oauth2-proxy.clientSecret` and `.cookie.secret` with
`.clientSecretFile` and `.cookie.secretFile`. Grafana's
`settings.security.secret_key` has no default; deliberately retain or rotate
the old key and inject it via Grafana variable expansion, outside the store.

### Secure Yggdrasil keys (since nixos-26.05)

`services.yggdrasil.configFile` and `persistentKeys` were removed. Use
structured `settings` and point `settings.PrivateKeyPath` at a PKCS #8 PEM
file. Literal `PrivateKey` content in settings is rejected to prevent store
disclosure.

### Explicit VSFTPD and cgit access control (since nixos-26.05)

VSFTPD no longer creates a PAM service, so `localUsers` requires an enabled
PAM service or virtual-user database. Cgit must explicitly choose
`gitHttpBackend.checkExportOkFiles` rather than inherit an export-all backend
that bypasses cgit access controls.

## Databases and stateful applications

### Nextcloud database and credentials (since nixos-25.05)

`services.nextcloud.config.dbtype` has no SQLite default and must be selected.
Secret files use systemd credentials, so `nextcloud-occ` requires root or an
existing `$CREDENTIALS_DIRECTORY`.

### PostgreSQL default and readiness (since nixos-25.11)

New systems at state version 25.11 default to PostgreSQL 17; existing systems
retain their state-selected version. Depending on `postgresql.target`
guarantees writable service plus completed initialization and ensure scripts;
`postgresql.service` guarantees only a read-only connection.

### Nextcloud cache and stepped upgrades (since nixos-25.11, nixos-26.05)

`services.nextcloud.configureRedis` defaults to `true`. State version 25.05
or newer selected Nextcloud 32, and releases 30 or older must pass through 31.
State version 26.05 selects Nextcloud 33 and removes 31; installations on 31
or older must pin and pass through `pkgs.nextcloud32` before 33.

### Forgejo dump retention (since nixos-25.11)

`services.forgejo.dump.age` defaults to `4w`; older dumps are deleted unless
the setting is overridden.

### State-gated service directories (since nixos-26.05)

At state version 26.05, TaskChampion Sync Server enables `DynamicUser` and
moves data to `/var/lib/private/taskchampion-sync-server`; migrate the old
directory if opting in manually. The renamed `services.stalwart` module has
its own `stateVersion`; user, group, directory, and tracer defaults change
only when it reaches 26.05.

### Mattermost 11 (since nixos-26.05)

Mattermost defaults to version 11 and no longer supports MySQL. Remove the
upstream 250-user limit only by overriding the selected package with
`removeUserLimit`, optionally `removeFreeBadge`.

### Immich VectorChord migration (since nixos-26.05)

`database.enableVectors` and `database.enableVectorchord` are removed;
VectorChord is always used. Completely remove an existing pgvecto.rs extension
from the database before upgrade.

## Other service-module migrations

### Rsyncd settings shape (since nixos-25.05)

`services.rsyncd.settings` accepts only `sections` and `globalSection`. Move
named sections below `settings.sections` and former `settings.global` values
below `settings.globalSection`.

### BorgBackup hook arrays (since nixos-25.05)

`services.borgbackup.jobs.*.extraArgs` and other `extra*Args` values are Bash
arrays. Hooks must append array elements instead of concatenating a string.

### Imperative containers (since nixos-25.11)

`boot.enableContainers` is automatic only when declarative `containers`
exist. Hosts managed with `nixos-container` must set it explicitly.

### Postfix certificate chains (since nixos-25.11)

Replace removed `services.postfix.sslCert` and `sslKey` with
`services.postfix.settings.main.smtpd_tls_chain_files` for server chains and
`smtp_tls_chain_files` for client chains.

### Renamed and removed modules (since nixos-25.11)

Rename `programs.river` to `programs.river-classic`,
`services.nixseparatedebuginfod` to `services.nixseparatedebuginfod2`,
`services.dnscrypt-proxy2` to `services.dnscrypt-proxy`, and `services.pds` to
`services.bluesky-pds`. The LXD module is removed; migrate
`virtualisation.lxd` to `virtualisation.incus`.

### GNOME SSH agent (since nixos-25.11)

`gnome-keyring` no longer supplies an SSH agent. Enable the `gcr_4`
replacement with `services.gnome.gcr-ssh-agent.enable`; for transition it
defaults to the GNOME keyring enable value.

### Default tools and user lingering (since nixos-25.11)

Nettools commands (`ifconfig`, `arp`, `mii-tool`, `netstat`, and `route`) are
absent from default installations; use `iproute2` and `ethtool` or install
`nettools`. `users.users.<name>.linger` defaults to `null`, preserving
existing loginctl state; `users.manageLingering` can turn off NixOS lingering
management globally.

### NVIDIA driver configuration (since nixos-26.05)

`hardware.nvidia.branch` selects a branch unless `hardware.nvidia.package`
overrides it, and `hardware.nvidia.moduleParams` writes modprobe options. Branches include
`production`, `new_feature`, and `beta`; proprietary modules moved to
`nvidia_x11.mod`. Maxwell-or-older GPUs must pin
`nvidiaPackages.legacy_580`.

### Removed system facilities (since nixos-26.05)

`profiles/hardened`, `linux_hardened`, `linux-rt`, ReiserFS, and eCryptfs were
removed. Systemd cannot start units installed with `nix-env -i`.
`post-resume.target` users should order resume work with `sleep.target` and
`ExecStop=`.

### Kubernetes CoreDNS images (since nixos-26.05)

`services.kubernetes.addons.dns.coredns` became `corednsImage` and takes an
image package, not attributes. The default is built locally from
`pkgs.coredns` via `dockerTools.buildImage`; provide a `dockerTools.pullImage`
derivation to keep an upstream image.
