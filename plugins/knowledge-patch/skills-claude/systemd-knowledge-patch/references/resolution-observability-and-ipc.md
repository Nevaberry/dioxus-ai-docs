# Resolution, Observability, and IPC

## Journal and coredumps

### Socket forwarding and retention (256)

Journald's `ForwardToSocket=` and `MaxLevelSocket=` send Journal Export Format
to AF_INET, AF_INET6, AF_UNIX, or AF_VSOCK; the destination may come from the
`journald.forward_to_socket` credential. `systemd-journal-remote` accepts UNIX/VSOCK,
and vmspawn forwards guest journals with `--forward-journal=`. Coredumps are
retained for two weeks by default rather than three days.

### Invocation queries and container symbols (257)

Use `journalctl --list-invocation` to list a unit's invocations and
`--invocation=`/`-I` to select one. `EnterNamespace=yes` lets coredump enter a
crashed process's mount namespace for container debug symbols; it defaults
off.

### Reliable following and HTTP transfer (258)

`journalctl --follow` exits successfully on SIGINT, SIGTERM, or a disconnected
pipe. `--synchronize-on-exit=yes` waits for journald to commit messages queued
before SIGINT. Upload and remote negotiate compression and accept HTTP
`Header=` fields.

### Persistent storage and Varlink entries (259, 260)

Journald defaults `Storage=` to `persistent` regardless of pre-existing
`/var/log/journal`; builds can set `-Djournal-storage-default=`. Journalctl's
Varlink `GetEntries()` provides programmatic retrieval.

### Point-release journal changes (258.10-261.2)

In v260.4 and v261.2, journal-remote does not create
`/var/log/journal/remote`; provision it. All four point releases reject match
filters while `journalctl` lists field values, so use `--field=` without
filters or perform a normal filtered query.

## Resolution hooks and DNS inspection

### Local resolver extension (259)

Machined resolves local machine names, and networkd's DHCP server provides a
leased-hostname hook enabled on host-side nspawn/vmspawn networks. A privileged
service may bind below `/run/systemd/resolve.hook/` to answer, deny, or pass
through lookups.

Resolved's `DumpDNSConfiguration()` returns the complete configuration and is
available through `resolvectl --json=`.

### Delegated routing (258, 260)

DNS delegate files define independent domain-specific servers and routing or
search domains. They support `FirewallMark=`; NSS may use
`SYSTEMD_NSS_RESOLVE_INTERFACE`, and `BrowseServices` ifindex 0 covers all
mDNS interfaces.

## JSON, Varlink, and D-Bus APIs

### Public JSON and device monitoring (257)

`libsystemd` exposes `sd-json` for typed JSON and `sd-varlink` for Varlink IPC.
Public sd-device monitor accessors expose fd, events, timeout, and receive for
foreign event loops, plus device-ID and driver-subsystem getters.

### Shell descriptor passing (258)

`varlinkctl --push-fd=` sends fds with AF_UNIX calls. `--exec` runs a command
after a reply, supplies JSON on stdin, and exports returned fds using
`LISTEN_FDS`.

### Manager API and unit diagnostics (259)

Manager Varlink exposes execution settings, filters `Unit.List()` by cgroup or
invocation, and provides `Reload()` and `Reexecute()`. Unit activation
transactions have logged 64-bit IDs, with ordering cycles exposed through
`TransactionsWithOrderingCycle` on D-Bus.

### Varlink event-loop controls (259)

Passing zero to `sd_varlink_set_relative_timeout()` restores the default.
`SD_VARLINK_SERVER_HANDLE_SIGTERM` and `SD_VARLINK_SERVER_HANDLE_SIGINT` make
`sd_varlink_server_loop_auto()` exit on those signals;
`sd_varlink_is_connected()` reports state, and `varlinkctl --more` sends
`READY=1` after its first reply.

### ABI rebuild after v260-rc1 (260)

Programs built against v260-rc1 headers must be rebuilt because that release
candidate temporarily changed numeric `sd_varlink_field_type_t` values; rc2
restored them.

### Registry, bridges, and reports (260)

Link public sockets below `/run/varlink/registry/` and enumerate them with
`varlinkctl list-registry`; `SD_VARLINK_ANY` represents wildcard-typed fields.
Unknown URL schemes cause `sd_varlink_connect_url()` to launch
`/usr/lib/systemd/varlink-bridges/<scheme>` with a `LISTEN_FDS` socket.

Components publish report endpoints below `/run/systemd/report/`, and
`systemd-report` combines them as JSON. The report schema is experimental and
may change incompatibly.

## Event loops and process supervision

### Non-reaping child watches (259)

`sd_event_add_child()` and `sd_event_add_child_pidfd()` accept `WNOWAIT` to
observe without reaping. `sd_event_set_exit_on_idle()` and
`sd_event_get_exit_on_idle()` control
loop exit when no enabled non-exit sources remain.

### OOM observability (259, 260)

Units distinguish kernel `OOMKills` from oomd `ManagedOOMKills`. Components
can register a synchronous Varlink pre-kill hook in oomd's designated hook
directory.
