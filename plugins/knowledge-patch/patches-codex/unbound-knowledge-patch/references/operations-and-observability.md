# Operations and observability

## Secrets, trust anchors, and access

### Persistent EDNS COOKIE rollover

`cookie-secret-file` persists secrets for rollover (since 1.21.0). Rotate at
runtime with `add_cookie_secret`, `activate_cookie_secret`, and
`drop_cookie_secret`; inspect active values with `print_cookie_secrets`.

### Compiled root key

The default `unbound-anchor` root keys include key 38696 (since 1.21.0). Use
`unbound-anchor -l` to inspect compiled-in content.

### Control-key group access

Members of the `unbound` group can access the control key (since 1.23.0).
Account for that authorization when assigning group membership.

### Extended certificate bundle

The built-in `icannbundle.pem` contains ICANN keys covering 2009–2029 and
2025–2045 (since 1.26.0). Inspect built-in material with `unbound-anchor -l`;
use `-c /path/to/icannbundle.pem` for an externally updateable bundle.

## Reload behavior

### Fast reload

`unbound-control fast_reload` parses changed configuration in a separate
thread and pauses service threads briefly (since 1.23.0), keeping DNS
interruption below a second.

### Redis-independent reload

A reload continues when Redis cachedb cannot connect or respond (since
1.23.0). Unbound logs the failure and checks expiration features only when the
server is available.

### Dnstap propagation

Dnstap configuration changes are copied from the daemon into worker threads
after `fast_reload` (since 1.24.0).

### Failure containment

`fast_reload` no longer terminates the daemon on key-file configuration errors
(since 1.26.0). It safely handles in-progress ZONEMD checks and auth-zone
primary-name lookups or removals without stale callbacks or results.

## Cache commands

### Negative-cache flush reporting

`unbound-control flush_negative` reports removed data correctly (since
1.23.0).

### Targeted cache lookup

`unbound-control cache_lookup <domains>` prints selected cached RRsets and
messages (since 1.24.0). Prefix with `+t` for TLD or root names; matching
subnet-cache data is included.

### Responsive full dumps

`dump_cache` releases cache locks periodically and separates file-descriptor
activity from cache lookups (since 1.24.0), preserving responsiveness during
long dumps.

### Exact local-data removal

`unbound-control local_data_remove` accepts a complete RR (since 1.26.0), so
one record can be removed without deleting all local data at its owner.

## Counters and logging

### Mesh reply counters

Statistics expose `num.queries.replyaddr_limit` and
`requestlist.current.replies` (since 1.24.0). Packets dropped by
`discard-timeout` reduce the mesh reply-address-in-use count.

### Linux system thread IDs

On Linux, `log-thread-id: yes` selects the system-wide thread ID instead of
Unbound's internal counter (since 1.25.0), aiding correlation with system
tools.

## Command validation

### Strict argument checking

Remote-control commands that accept no arguments reject extras (since
1.24.0). Treat previous scripts that appended harmless arguments as invalid.
