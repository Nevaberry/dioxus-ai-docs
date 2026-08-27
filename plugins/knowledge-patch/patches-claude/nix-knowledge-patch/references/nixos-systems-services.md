# NixOS Systems and Services

## Rebuild, system entry points, and images

### Rebuild implementations

The Python `nixos-rebuild-ng` was opt-in through `system.rebuild.enableNg` in
nixos-25.05 and became the default in nixos-25.11. Its temporary
`system.rebuild.enableNg = false` escape hatch was scheduled to disappear.
System switching is Rust-only; remove the obsolete `system.switch.enableNg`
setting because the Perl implementation is gone.

`nixos-rebuild build-image` builds the platform-specific image defined by the
configuration. Image builders have customizable `image.baseName`,
`image.extension`, and `image.fileName`; `image.filePath` exposes the relative
output path at evaluation time. Do not hard-code older default filenames.

`nixos-option` supports flake configurations, nested `attrsOf`/`listOf`
submodules, and `--show-trace`.

### Channel-free system evaluation

In nixos-26.05, `/etc/nixos/system.nix` may evaluate directly to one system
derivation or to an attribute set selected by `nixos-rebuild --attr`. Use
`--file` for another file or directory; when `--attr` is present, a
`system.nix` in the current directory is also considered. This supports pinned
evaluation without a channel.

### Switch inhibitors and activation

Switch inhibitors can reject a generation when configured comparison strings
differ (nixos-26.05); `NIXOS_NO_CHECK=1` forces the switch. The switch program
reloads a unit whose only change is `ExecReload=`, does nothing when
`ExecReload=` is removed, and deprecates activation scripts that directly
request unit reloads or restarts.

## Boot, initrd, filesystems, and containers

### Systemd stage 1

The initrd uses systemd by default in nixos-26.05. Scripted stage 1 is
deprecated and can temporarily be retained with:

```nix
boot.initrd.systemd.enable = false;
```

Name the LUKS source and mapped root consistently, replace `/dev/root` with a
stable path, and give complex LVM-on-LUKS device discovery an infinite systemd
device timeout where needed.

The earlier Rust `nixos-init` made a bashless systemd initrd possible in
nixos-25.11 through `system.nixos-init.enable = true`.

### Filesystems and the Nix store mount

NixOS-provided `fileSystems` entries use `lib.mkDefault` from nixos-25.05, so a
configuration can replace them wholesale. When overriding only `fsType` or
`options`, restate `device` if the override would discard it. Every
`fileSystems.<name>.fsType` is mandatory in nixos-26.05.

`boot.readOnlyNixStore` was removed in nixos-25.11. Set bind-mount behavior
through `boot.nixStoreMountOpts`.

### Containers and integration tests

`boot.enableContainers` is automatic only when declarative `containers` are
present (nixos-25.11). Hosts using imperative `nixos-container` must enable it
explicitly. NixOS integration tests can use `systemd-nspawn` instead of QEMU in
nixos-26.05, including on VM builders without KVM and in tests that bind-mount
host devices such as GPUs.

## systemd and service ordering

### Network readiness

Since nixos-25.05, `multi-user.target` is not ordered after
`network-online.target`. A service that cannot start offline needs both:

```nix
systemd.services.example = {
  wants = [ "network-online.target" ];
  after = [ "network-online.target" ];
};
```

### Structured settings

In nixos-25.11, system manager configuration moves from `systemd.extraConfig`
and `boot.initrd.systemd.extraConfig` to the corresponding
`systemd.settings.Manager` attributes. Watchdogs become
`RuntimeWatchdogSec`, `WatchdogDevice`, `RebootWatchdogSec`, and
`KExecWatchdogSec` there; replace `systemd.enableCgroupAccounting` with the
individual `*Accounting` manager settings.

Also move:

- `services.dwm-status.extraConfig` to `services.dwm-status.settings`, nesting
  `order` there.
- `services.traccar.settings.loggerConsole` to
  `services.traccar.settings.logger.console`.
- `services.logind.extraConfig` to `services.logind.settings.Login`.

In nixos-26.05, use `systemd.coredump.settings.Coredump`,
`systemd.sleep.settings.Sleep`, and `services.pdns-recursor.settings` in place
of the old free-form options. The resolved and Dovecot modules likewise use
RFC 42-style settings.

### PostgreSQL readiness

`postgresql.target` means PostgreSQL is writable and initialization and ensure
scripts have completed (nixos-25.11). `postgresql.service` promises only a
read-only connection. Choose the dependency matching the consumer's need.

### ACME ordering and renewal

Depend on `acme-{certname}.service` when a service needs a syntactically valid
certificate (nixos-25.11). Initial self-signed certificates are always
generated; `security.acme.preliminarySelfsigned` was removed. Replace
dependencies on `acme-finished-{certname}.target` with
`acme-order-renew-{certname}.service`.

From nixos-26.05, an unset `security.acme.defaults.validMinDays` derives the
renewal point from lifetime: two thirds for certificates valid at least ten
days and one half for shorter certificates.

## Networking, firewalling, and wireless

### Firewall backends and logging

NixOS supports FirewallD as `services.firewalld` or as the backend for
`networking.firewall`; select through `networking.firewall.backend`
(nixos-25.11). In nixos-26.05,
`networking.firewall.logRefusedConnections` defaults to `false`; enable it
explicitly when refusal logs are required.

NAT forward-port rules are restricted to packets targeting
`networking.nat.externalIP` or `externalIPv6` when either is set
(nixos-25.05).

### NetworkManager, WireGuard, and resolver behavior

`networking.wireguard` can use networkd (nixos-25.05), selected automatically
with `networking.useNetworkd` or explicitly through
`networking.wireguard.useNetworkd`. The scripted and networkd backends differ
in some option semantics.

NetworkManager has no default VPN plugin set from nixos-25.11; enumerate every
required package in `networking.networkmanager.plugins`.

The scripted backend in nixos-26.05 has no `network-setup.service`; interface
addresses, routes, and gateways appear asynchronously, and DNS setup runs in
`network-local-commands.service`. `networking.resolvconf.enable` always
defaults to `true`, so configurations that own `/etc/resolv.conf` must set it
to `false`.

### Hardened wireless

In nixos-26.05, `wpa_supplicant` runs unprivileged and keeps generated and
imperative configuration below `/etc/wpa_supplicant`. Credential files must be
readable by that user. Remove `networking.wireless.userControlled.group` and
rename `.userControlled.enable` to `.userControlled`.

NetworkManager now relies on `networking.wireless`, so remove an explicit
`networking.wireless.enable = false`. Use
`networking.wireless.enableHardening` only as a compatibility escape hatch.
`iw` and `wirelesstools` are no longer installed implicitly.

## OpenSSH and access control

`services.openssh.settings.AcceptEnv` is a list in nixos-26.05, not a string.
Host keys may be generated with `services.openssh.generateHostKeys = true`
while the daemon is disabled. Disable the curated algorithm set only with
`enableRecommendedAlgorithms = false`. Replace removed
`services.openssh.banner` with `services.openssh.settings.Banner`.

VSFTPD no longer creates a PAM service automatically (nixos-26.05); local
users need explicit PAM or a virtual-user database. Cgit must explicitly set
whether `gitHttpBackend.checkExportOkFiles` is enabled instead of inheriting an
export-all backend that can bypass cgit access controls.

## Security policy and secrets

### AppArmor and earlyoom

Replace removed `security.apparmor.policies.<name>.enable` and `.enforce` with
the `state` tristate option (nixos-25.05).

The earlyoom module uses upstream's hardened unit. A `killHook` needing home or
filesystem access may require a `ProtectSystem` override. Each
`services.earlyoom.extraArgs` element is shell-escaped separately, so express
arguments as list elements rather than relying on word splitting.

### Secret-file migrations

Nextcloud secret files use systemd credentials from nixos-25.05, so
`nextcloud-occ` needs root or an existing `$CREDENTIALS_DIRECTORY`.

In nixos-26.05, replace OAuth2 Proxy's `clientSecret` and `cookie.secret` with
`clientSecretFile` and `cookie.secretFile`. Grafana's
`settings.security.secret_key` has no default; retain or deliberately rotate
the existing key and inject it through Grafana variable expansion rather than
the Nix store.

Yggdrasil removes `configFile` and `persistentKeys` in favor of structured
`settings`. Put the persistent private key in a PKCS #8 PEM file and point
`settings.PrivateKeyPath` to it. A literal `PrivateKey` is rejected to prevent
store disclosure.

## Database and application services

### Nextcloud

`services.nextcloud.config.dbtype` has no SQLite default in nixos-25.05; select
the database explicitly. In nixos-25.11, `configureRedis` defaults to `true`
and state version 25.05 selects Nextcloud 32. Upgrade installations on 30 or
older through Nextcloud 31 rather than skipping a major.

State version 26.05 selects Nextcloud 33 and removes 31. An installation on 31
or older must pin `pkgs.nextcloud32`, complete that upgrade, and then choose 33.

### PostgreSQL, Mattermost, and Immich

New state-version 25.11 systems default to PostgreSQL 17; older systems retain
their state-selected version. Mattermost defaults to version 11 in
nixos-26.05 and drops MySQL. Remove the upstream 250-user limit only by
overriding its package with `removeUserLimit` (and optionally
`removeFreeBadge`).

Immich always uses VectorChord in nixos-26.05; `database.enableVectors` and
`database.enableVectorchord` were removed. Completely remove pgvecto.rs from
an existing database before upgrading.

### Stateful data migrations

At state version 26.05, TaskChampion Sync Server enables `DynamicUser` and uses
`/var/lib/private/taskchampion-sync-server`; migrate the old directory when
opting in manually. The renamed `services.stalwart` has its own `stateVersion`
and changes user, group, data path, and tracer defaults only at 26.05.

### Forgejo, rsyncd, and BorgBackup

Forgejo dump retention defaults to `4w` from nixos-25.11. Override
`services.forgejo.dump.age` to retain older dumps.

`services.rsyncd.settings` accepts only `sections` and `globalSection` from
nixos-25.05. Move named sections below `settings.sections` and old
`settings.global` values below `settings.globalSection`.

BorgBackup job `extraArgs` and other `extra*Args` are Bash arrays. Hook code
must append array elements, for example
`extraCreateArgs+=("--exclude" "/some/path")`, not concatenate a string.

## Hardware, graphics, and kernel behavior

### Graphics and NVIDIA

`hardware.graphics.package` selects the global Mesa version without a mass
rebuild (nixos-25.05).

In nixos-26.05, `hardware.nvidia.branch` selects a driver branch unless
`hardware.nvidia.package` overrides it. `hardware.nvidia.moduleParams` writes
kernel module parameters. Branches include `production`, `new_feature`, and
`beta`; proprietary modules moved to `nvidia_x11.mod`. Maxwell and older GPUs
must pin `config.boot.kernelPackages.nvidiaPackages.legacy_580`.

Unknown `services.xserver.videoDriver` or `videoDrivers` values now fail
evaluation instead of being ignored.

### Removed facilities

Nixos-26.05 removes `profiles/hardened`, `linux_hardened`, `linux-rt`, ReiserFS,
and eCryptfs support. Systemd no longer starts units installed by
`nix-env -i`. Replace `post-resume.target` ordering with `sleep.target` and an
`ExecStop=` action.

XFS created by xfsprogs 6.18 may enable parent pointers and exchange-range
features. Such filesystems need a 6.18-or-newer kernel, and GRUB 2 may not boot
from them.

## Users, desktop, and compatibility packages

### User sessions and legacy tools

`users.users.<name>.linger` defaults to `null` in nixos-25.11, leaving current
loginctl state unchanged. Set `users.manageLingering = false` to disable NixOS
lingering management globally.

The legacy `nettools` commands are not installed by default. Use `iproute2`
and `ethtool`, or explicitly install `nettools` where required.

`gnome-keyring` no longer supplies an SSH agent. Use
`services.gnome.gcr-ssh-agent.enable`; its default follows
`services.gnome.gnome-keyring.enable` for migration compatibility.

### D-Bus

`dbus-broker` is the default implementation in nixos-26.05. Switching
implementations inhibits live switching and requires a reboot. Pin the
reference daemon with:

```nix
services.dbus.implementation = "dbus";
```

## Module renames and removals

For nixos-25.11, migrate:

- `programs.river` to `programs.river-classic`
- `services.nixseparatedebuginfod` to `services.nixseparatedebuginfod2`
- `services.dnscrypt-proxy2` to `services.dnscrypt-proxy`
- `services.pds` to `services.bluesky-pds`
- `virtualisation.lxd` to `virtualisation.incus` because the LXD module is gone

Postfix's `sslCert` and `sslKey` are removed. Configure server chains with
`services.postfix.settings.main.smtpd_tls_chain_files` and client chains with
`services.postfix.settings.main.smtp_tls_chain_files`.

## Kubernetes DNS

In nixos-26.05, `services.kubernetes.addons.dns.coredns` becomes
`corednsImage` and accepts an image package rather than attributes. Its default
is built locally from `pkgs.coredns` with `dockerTools.buildImage`; pass a
`dockerTools.pullImage` derivation to keep an upstream image.

## State-version discipline

`system.stateVersion` must be a valid `"YY.MM"` NixOS release string from
nixos-25.05. Do not bump it as a routine package update: it gates PostgreSQL,
Nextcloud, service users, data locations, and other migration-sensitive
defaults described above.
