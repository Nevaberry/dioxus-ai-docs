# System administration

## Configure networking and address assignment

Rocky Linux 10.0 removes the `ifcfg-rh` format,
`/etc/sysconfig/network-scripts/ifcfg-*`, `ifup`, `ifdown`, and hooks such as
`ifup-local`. Use NetworkManager through `nmcli`, `nmtui`, or `nmstate`.
Persistent profiles live in `/etc/NetworkManager/system-connections/`.

NetworkManager's internal DHCP client replaces the removed `dhcp-client`
package. Kea replaces the end-of-life ISC DHCP server. NIC teaming is removed;
migrate existing teams to bonds.

Rocky Linux 10.2 updates FRRouting (`frr`) to 10.4.1.

## Manage storage and crash handling

- GFS2 is unsupported on Rocky Linux 10.0.
- Device Mapper Multipath cannot be enabled for NVMe devices in 10.0.
- Cryptsetup 2.7 supports `kdump` with LUKS-encrypted devices in 10.0.
- Cockpit can configure Stratis file-system size limits in 10.0.
- Rocky Linux 9.8 improves kernel crash handling and `kdump` awareness of
  LUKS-encrypted storage.

## Work with kernel behavior and diagnostics

Rocky Linux 10.0 ships kernel 6.12 and replaces CFS scheduling with EEVDF.
Features disabled as unmaintained, insecure, or deprecated can be explicitly
re-enabled with the `rh_waived` kernel command-line argument.

In 9.8, `perf` adds `debuginfod` support, newer Intel core, uncore, C-state, and
package events, and AMD IBS Load-Latency Filtering. In 10.2, kernel tooling adds
threshold-overflow actions to `rtla`, Python bindings for `cpupower`, and an
updated `rteval`. Driver and device-ID coverage expands for Intel EDAC and QAT
hardware and for Intel and AMD accelerator and cryptographic devices.

## Query and install packages

Rocky Linux 10.0 DNF no longer downloads repository file-list metadata by
default, although commands that require it generally fetch it on demand.
AppStream modules and `dnf module` are phased out. Query ordinary packages and
install or remove versioned RPM names instead:

```console
$ dnf repoquery nginx
$ sudo dnf install nginx-1.26.3
$ sudo dnf remove nginx-1.26.3
```

RPM 4.19 includes `rpmsort`, which understands RPM version strings where
lexical `sort` does not:

```console
$ rpm -q kernel | rpmsort
```

For example, lexical sorting can place `6.12.0-130` before `6.12.0-13`.

Rocky Linux 10.2 repositories contain PHP 8.3 and 8.4. An unqualified
dependency can select a package for the wrong PHP version. Query providers,
then install the result that matches the installed PHP version:

```console
$ dnf provides php-json
```

## Operate infrastructure services

Rocky Linux 10.0 replaces Redis with Valkey 8.0; `valkey-compat-redis` is
available from the Plus repository. It removes Sendmail in favor of Postfix and
moves SpamAssassin to EPEL. The `tuned-ppd` compatibility layer replaces
`power-profiles-daemon` for consumers of that interface. Varnish Cache 7.6 and
Squid 6.10 are additional server baselines.

Rocky Linux 10.2 updates `chrony` to 4.8 and adds the `capnproto` package for
Cap'n Proto zero-copy serialization and RPC.

## Use web administration interfaces

- Install `cockpit-files` on Rocky Linux 9.5 to browse, copy, move, delete,
  download, and upload files and directories through the web console.
- Treat Cockpit's multi-host switcher as deprecated and disabled by default for
  security on 10.0.
- Use the preview of FreeIPA's Cockpit-based modern UI at `/ipa/modern-ui` on
  9.8; only portions of the new interface are included.

