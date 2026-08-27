# Operations and Observability

## Reload behavior

### Fast reload

`unbound-control fast_reload` reads changed configuration in a separate thread
and pauses service threads only briefly (1.23.0), keeping DNS interruption
below a second under normal conditions.

```sh
unbound-control fast_reload
```

Dnstap changes are copied from the daemon to worker threads after a fast
reload (1.24.0).

Certificate-file changes rebuild TLS contexts for DoT, DoH, DoQ, and outgoing
DoT (1.25.0). Fast reload recognizes `tls-service-key`, `tls-service-pem`, and
`tls-cert-bundle`, and propagates `iter-scrub-ns`, `iter-scrub-cname`, and
`max-global-quota` changes.

Key-file configuration errors during fast reload no longer terminate the
daemon (1.26.0). Reloads also safely coexist with in-progress ZONEMD checks and
auth-zone primary-name lookups or removals, without retaining stale callbacks
or results.

## Cache control and diagnostics

### Targeted lookup

`cache_lookup <domains>` prints cached RRsets and messages for selected names,
including matching subnet-cache entries (1.24.0). `+t` permits TLD and root
names.

```sh
unbound-control cache_lookup example.com
unbound-control cache_lookup +t .
```

### Responsive full dump

`dump_cache` periodically releases cache locks and separates file-descriptor
activity from lookups (1.24.0), helping the server remain responsive during a
long dump.

### Negative-cache flush result

`unbound-control flush_negative` reports removed data correctly (1.23.0).

## Dnstap

`dnstap-sample-rate` emits one of every N messages to limit high-volume output
(1.21.0):

```conf
dnstap:
    dnstap-sample-rate: 100
```

Fast reload propagates dnstap configuration to workers as described above.

## Error reporting and statistics

### DNS Error Reporting

Enable RFC 9567 DNS Error Reporting with `dns-error-reporting` (1.23.0). Sent
reports are counted in `num.dns_error_reports`.

### Wait-limit and discard activity

Loopback addresses are exempt from `wait-limit` (1.23.0).
`wait-limit-netblock` and `wait-limit-cookie-netblock` accept their documented
two-argument forms, and statistics expose wait-limit and discard-timeout
activity.

`wait-limit: 0` disables all wait limits, while `wait-limit-cookie: 0` can
disable the limit for COOKIE-validated clients (1.24.0). Exceeding a wait limit
returns `SERVFAIL`. `discard-timeout` drops UDP queries but does not drop stream
connections.

### Mesh reply counters

`num.queries.replyaddr_limit` and `requestlist.current.replies` expose reply
pressure (1.24.0). A packet dropped by `discard-timeout` also decrements the
mesh reply-address-in-use accounting.

### QUIC statistics

When DoQ is available, use `num.query.quic` and `mem.quic` to observe query
volume and memory (1.22.0).

## Control interface and command handling

### Explicit listener ports

`control-interface` accepts `IP@port`, allowing each listener to select its
port directly (1.25.0):

```conf
remote-control:
    control-interface: 127.0.0.1@8953
```

### Strict arguments

Commands that accept no arguments reject extraneous arguments (1.24.0). Fix
automation that previously appended harmless-looking values.

### Exact local-data removal

`local_data_remove` accepts a complete RR (1.26.0), so one record can be
removed without deleting all local data at the owner:

```sh
unbound-control local_data_remove \
  'host.example. 300 IN A 192.0.2.10'
```

## Logging and warnings

On Linux, `log-thread-id: yes` selects the system-wide thread ID instead of
Unbound's internal counter (1.25.0), improving correlation with system tools.

```conf
server:
    log-thread-id: yes
```

Unbound warns when the operating system does not grant the requested
`so-sndbuf` size (1.24.0). Treat the warning as evidence that effective socket
buffering differs from configuration.

`unbound-checkconf` warns when a `nodefault` local-zone declaration has no
effect (1.25.0).
