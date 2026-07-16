# Resolution, Observability, and IPC

## Forward and query the journal

- Journald's `ForwardToSocket=` sends Journal Export Format records to AF_INET, AF_INET6, AF_UNIX, or AF_VSOCK. `MaxLevelSocket=` filters priority; the `journald.forward_to_socket` credential can provide the destination (since 256).
- `systemd-journal-remote` receives AF_UNIX and VSOCK streams (since 256).
- `journalctl --list-invocation` lists a unit's invocations; `--invocation=` or `-I` selects one invocation (since 257).
- The default `Storage=` changed from `auto` to `persistent`, independent of whether `/var/log/journal` already exists. Override the build default with `-Djournal-storage-default=` (since 259).
- Journalctl exposes a Varlink `GetEntries()` method for programmatic retrieval (since 260).

## Follow and export logs reliably

- `journalctl --follow` exits successfully on SIGINT, SIGTERM, or output-pipe disconnect. `--synchronize-on-exit=yes` waits after SIGINT until journald confirms all previously queued messages were written (since 258).
- Journal upload and remote negotiate compression and accept extra HTTP `Header=` values (since 258).
- `systemctl start --verbose` and related verbs stream unit logs until the operation completes (since 258).

## Retain and symbolize coredumps

- The default coredump retention horizon is two weeks rather than three days (since 256).
- `EnterNamespace=yes` lets systemd-coredump enter a crashed process's mount namespace to locate debug symbols. It is useful for application containers that cannot handle coredumps internally and remains disabled by default (since 257).

## Resolve names and inspect DNS

- `systemd-networkd-wait-online --dns` waits for resolved DNS configuration as well as connectivity (since 258).
- `RefuseRecordTypes=` rejects selected DNS RR types (since 258).
- `/etc/systemd/dns-delegate.d/*.dns-delegate` defines domain-specific lookup scopes with independent servers and routing/search domains. Delegates support `FirewallMark=` for all traffic in that scope (since 258 and 260).
- Machined can resolve local VM/container names. Networkd's DHCP server supplies a resolver hook for leased hostnames, enabled by default on host-side nspawn and vmspawn networks (since 259).
- A privileged service can bind below `/run/systemd/resolve.hook/` to answer, deny, or pass through each lookup (since 259).
- `resolvectl --json=` exposes resolved's `DumpDNSConfiguration()` Varlink result (since 259).
- `SYSTEMD_NSS_RESOLVE_INTERFACE` limits an nss-resolve query to one interface. Ifindex 0 to `BrowseServices` browses all mDNS interfaces (since 260).

## Build with public JSON, Varlink, and device-monitor APIs

- `libsystemd` publicly exposes `sd-json` for typed JSON and `sd-varlink` for Varlink IPC (since 257).
- `sd-device` monitor accessors expose its fd, events, timeout, and receive operation for integration with a foreign event loop. Public accessors also expose device IDs and driver subsystems (since 257).
- `varlinkctl --push-fd=` sends descriptors with an AF_UNIX call. `--exec` runs a command after the reply, puts JSON on standard input, and exposes returned descriptors through `LISTEN_FDS` (since 258).

## Connect and discover Varlink services

- `varlinkctl` uses `ssh-exec:` to launch a remote executable and speak Varlink over SSH. `ssh-unix:` tunnels to a remote AF_UNIX socket; the old `ssh:` spelling remains accepted (since 257).
- Public sockets can be linked below `/run/varlink/registry/` and listed with `varlinkctl list-registry`. `SD_VARLINK_ANY` describes wildcard-typed fields (since 260).
- For an unknown URL scheme, `sd_varlink_connect_url()` launches `/usr/lib/systemd/varlink-bridges/<scheme>` and passes a socket with `LISTEN_FDS` (since 260).
- Passing zero to `sd_varlink_set_relative_timeout()` restores the default. `SD_VARLINK_SERVER_HANDLE_SIGTERM` and `SD_VARLINK_SERVER_HANDLE_SIGINT` make `sd_varlink_server_loop_auto()` exit cleanly; `sd_varlink_is_connected()` reports state (since 259).
- `varlinkctl --more` sends `READY=1` after its first reply (since 259).

## Inspect manager state and transactions

- The manager Varlink API exposes execution settings; filters `Unit.List()` by cgroup or invocation ID; and provides `Reload()` and `Reexecute()` (since 259).
- Activation transactions receive logged 64-bit IDs. Ordering-cycle transactions are exposed through the `TransactionsWithOrderingCycle` D-Bus property (since 259).
- Process-spawning units expose `OOMKills` and `ManagedOOMKills`, distinguishing kernel OOM kills from systemd-oomd actions (since 259).

## Publish reports and drive event loops

- Components publish report endpoints below `/run/systemd/report/`; `systemd-report` combines them as JSON. The schema remains experimental and may change incompatibly (since 260).
- `sd_event_add_child()` and `sd_event_add_child_pidfd()` accept `WNOWAIT` for observation without reaping. `sd_event_set_exit_on_idle()` and `sd_event_get_exit_on_idle()` control loop exit when no enabled non-exit sources remain (since 259).
