# Resolution, Observability, and IPC

## Journal and coredump workflows

### Journal socket forwarding (256)

`ForwardToSocket=` and `MaxLevelSocket=` emit Journal Export Format to
AF_INET, AF_INET6, AF_UNIX, or AF_VSOCK; the destination may come from the
`journald.forward_to_socket` credential. Journal-remote receives UNIX/VSOCK,
and vmspawn `--forward-journal=` forwards guest logs over VSOCK.

### Invocation queries (257)

`journalctl --list-invocation` lists unit invocations; `--invocation=`/`-I`
selects one invocation's records.

### Container-aware coredumps (257)

`EnterNamespace=yes` lets coredump enter a crashed process's mount namespace
to locate debug symbols. It improves container backtraces but remains off by
default.

### Reliable following (258)

`journalctl --follow` exits successfully on SIGINT, SIGTERM, or disconnected
output. `--synchronize-on-exit=yes` waits after SIGINT until journald confirms
all previously queued messages. Journal upload/remote negotiate compression
and accept additional HTTP `Header=` values.

### Journal retrieval through Varlink (260)

Journalctl exposes `GetEntries()` through Varlink for programmatic retrieval.

### Point-release journal restrictions (258.10-261.2)

All covered point releases reject match filters while listing field values;
list with `journalctl --field=_SYSTEMD_UNIT` and no matches or use a normal
filtered query. V260.4 and v261.2 journal-remote no longer create
`/var/log/journal/remote`; packaging must provision it.

## DNS and local name resolution

### Readiness, refusal, and delegate zones (258)

`systemd-networkd-wait-online --dns` waits for resolved configuration.
`RefuseRecordTypes=` blocks RR types. Files in
`/etc/systemd/dns-delegate.d/*.dns-delegate` define independent
domain-specific servers and routing/search domains.

### Extensible local lookup (259)

Machined resolves local VM/container names; networkd DHCP server supplies a
leased-hostname resolver hook, on by default for host-side nspawn/vmspawn
networks. A privileged service can bind below `/run/systemd/resolve.hook/` to
answer, deny, or pass through lookups. `DumpDNSConfiguration()` and
`resolvectl --json=` return the complete configuration.

### Delegation marks and NSS interface scope (260)

DNS delegate files accept `FirewallMark=`. Set
`SYSTEMD_NSS_RESOLVE_INTERFACE` to restrict nss-resolve to an interface.
Passing ifindex 0 to `BrowseServices` browses every mDNS interface.

## Public APIs and command-line IPC

### Public JSON, Varlink, and device monitor APIs (257)

Libsystemd publicly exposes typed `sd-json` and `sd-varlink`. Sd-device monitor
accessors expose fd, events, timeout, and receive so foreign event loops can
drive monitoring; device-ID and driver-subsystem getters are public.

### Varlink over SSH (257)

`ssh-exec:` starts a remote executable and speaks Varlink over SSH.
`ssh-unix:` tunnels to a remote UNIX socket; old `ssh:` remains accepted.

### Descriptor passing from shell (258)

`varlinkctl --push-fd=` sends descriptors with AF_UNIX calls. `--exec` runs a
command after reply, provides JSON on stdin, and exposes returned descriptors
through `LISTEN_FDS`.

### Manager APIs and transaction diagnostics (259)

Manager Varlink exposes execution settings, cgroup/invocation filtering for
`Unit.List()`, and `Reload()`/`Reexecute()`. Activation transactions have
logged 64-bit IDs; ordering-cycle transactions appear in D-Bus
`TransactionsWithOrderingCycle`.

### Varlink loop behavior (259)

Passing zero to `sd_varlink_set_relative_timeout()` restores the default.
`SD_VARLINK_SERVER_HANDLE_SIGTERM` and `_SIGINT` make
`sd_varlink_server_loop_auto()` exit cleanly; `sd_varlink_is_connected()`
reports state, and `varlinkctl --more` sends `READY=1` after its first reply.

### Sd-event child watches and idle exit (259)

`sd_event_add_child()` and `_pidfd()` accept `WNOWAIT` to observe without
reaping. `sd_event_set_exit_on_idle()`/`get_exit_on_idle()` control exit when
no enabled non-exit sources remain.

### Registry and pluggable transports (260)

Link public sockets below `/run/varlink/registry/` and enumerate with
`varlinkctl list-registry`. `SD_VARLINK_ANY` represents wildcard-typed fields.
For an unknown URL scheme, `sd_varlink_connect_url()` launches
`/usr/lib/systemd/varlink-bridges/<scheme>` with a socket in `LISTEN_FDS`.

### System reports (260)

Publish endpoints below `/run/systemd/report/`; `systemd-report` combines
them as JSON. The schema is experimental and may change incompatibly.

### Interactive authorization (260)

Sysext and varlinkctl can request interactive Polkit authorization. Authorized
unprivileged callers may also use systemd-ask-password.
