---
name: unbound-knowledge-patch
description: Unbound
version: 1.25.0
license: MIT
metadata:
  author: Nevaberry
---


# Unbound Knowledge Patch

Use this skill when configuring, upgrading, operating, building, or debugging
Unbound. Start with the quick references below, then open the topic file that
matches the task. Treat the deployed binary, `unbound-checkconf`, service logs,
and runtime statistics as authoritative for build-time feature availability.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/cache-and-recursion.md](references/cache-and-recursion.md) | Cache TTLs, cachedb and Redis, serve-expired, recursion, ECS, quota |
| [references/operations-and-observability.md](references/operations-and-observability.md) | Reloads, control commands, dnstap, statistics, diagnostics |
| [references/platforms-and-builds.md](references/platforms-and-builds.md) | Build dependencies, Windows, BSD PF, systemd, QNX, reproducibility |
| [references/security-and-policy.md](references/security-and-policy.md) | DNSSEC, rate limits, COOKIE secrets, rebinding, validation policy |
| [references/transports-and-tls.md](references/transports-and-tls.md) | DoQ, DoH, DoT, TLS selection and reload, upstream transport |
| [references/zones-and-resolution.md](references/zones-and-resolution.md) | Auth zones, RPZ, local zones, DNS64/NAT64, forwarding, RESINFO |

## Upgrade-critical defaults and removals

### Configure subnetcache explicitly

`module-config` defaults to `"validator iterator"` even when Unbound was built
with subnet support. If EDNS Client Subnet caching is required, name it:

```conf
server:
    module-config: "subnetcache validator iterator"
```

### Review serve-expired defaults

The secure defaults are now:

```conf
server:
    serve-expired-ttl: 86400
    serve-expired-client-timeout: 1800
```

Pin explicit values when an older operational policy must remain unchanged.
The reply TTL remains bounded by the record's original TTL.

### Account for new local zones

`resolver.arpa` and `service.arpa` are served locally by default. Verify
forwarding expectations for these names after an upgrade.

### Select TLS protocols at runtime

Use `tls-protocols` to select supported TLS versions. Do not use the removed
transient controls `tls-use-system-versions` or `--enable-system-tls`.
Deployments that require TLS 1.2 must not remain on 1.24.0; 1.24.1 restored it.

### Recheck changed limit semantics

- `max-global-quota` defaults to `200` rather than `128`.
- `wait-limit: 0` disables all wait limits.
- `wait-limit-cookie: 0` can disable limits for COOKIE-validated clients.
- Exceeding a wait limit returns `SERVFAIL`.
- `discard-timeout` drops UDP queries, not stream connections.
- Loopback clients are exempt from `wait-limit`.

## Security-first configuration

### Bound signature sets

`iter-scrub-rrsig` caps RRSIG records retained by the iterator scrubber and
defaults to `8`:

```conf
server:
    iter-scrub-rrsig: 8
```

### Protect SVCB and HTTPS answers

`private-address` filtering applies to SVCB and HTTPS records as well as
address records. Keep private ranges complete when using rebinding protection.

### Harden glue lookups consistently

`harden-unverified-glue` also covers missing AAAA lookups started by cache
filling. Enable it when that hardened behavior is required on all glue paths.

### Apply DNS64 policy in the supported order

To apply RESPIP and RPZ to DNS64-synthesized answers, use:

```conf
server:
    module-config: "respip dns64 validator iterator"
```

Do not assume that inserting cachedb as
`"respip dns64 validator cachedb iterator"` works. DNS64 now also preserves
`rpz-passthru`, respects ECS cache scope, and validates the AAAA leg when
DNSSEC is enabled.

### Rotate EDNS COOKIE secrets without restart

Persist rollover material with `cookie-secret-file`, then use
`add_cookie_secret`, `activate_cookie_secret`, and `drop_cookie_secret` through
`unbound-control`. Use `print_cookie_secrets` to inspect the active values.

```conf
server:
    cookie-secret-file: "unbound_cookiesecrets.txt"
```

## High-value operational commands

### Reload with a short pause

```sh
unbound-control fast_reload
```

`fast_reload` parses changed configuration in a separate thread and briefly
pauses service threads. It handles relevant TLS files, dnstap changes, scrub
settings, quota changes, and auth-zone activity. Key-file configuration errors
no longer terminate the daemon, but always inspect the returned status and
logs.

### Inspect selected cache entries

```sh
unbound-control cache_lookup example.com
unbound-control cache_lookup +t .
```

`cache_lookup` returns cached RRsets and messages for selected domains and
includes matching subnet-cache content. `+t` permits TLD and root names.

### Remove one local-data RR

Pass a complete record to avoid deleting every local-data record at the owner:

```sh
unbound-control local_data_remove \
  'host.example. 300 IN A 192.0.2.10'
```

### Inspect trust-anchor material

```sh
unbound-anchor -l
unbound-anchor -c /etc/unbound/icannbundle.pem
```

`-l` prints built-in material; `-c` selects an external certificate bundle.

## Transport quick reference

### Enable DNS over QUIC only with build support

Build with libngtcp2 and a QUIC-capable OpenSSL, then configure:

```conf
server:
    quic-port: 853
    quic-size: 8m
```

A build without DoQ support ignores QUIC ports and warns when `quic-port` is
set. Check `num.query.quic` and `mem.quic` after enabling it.

### Override upstream transport by forward zone

```conf
server:
    tcp-upstream: no
    tls-upstream: no

forward-zone:
    name: "."
    forward-tcp-upstream: yes
    forward-tls-upstream: yes
```

`forward-tcp-upstream` and `forward-tls-upstream` override the global choices
for that forward zone.

### Give control listeners explicit ports

```conf
remote-control:
    control-interface: 127.0.0.1@8953
```

Each `control-interface` may use `IP@port`.

## Zone and blocking patterns

### Block one address family while serving local data

`block_aaaa` suppresses AAAA lookups like `block_a` suppresses A lookups. The
`_wdata` variants serve matching local data, recurse transparently for other
data, and deny the selected address family:

```conf
server:
    local-zone: "v4-only.example." block_aaaa_wdata
    local-data: "v4-only.example. 300 IN A 192.0.2.10"
```

### Avoid circular zone dependencies

Prefer IP addresses for stub- and forward-zone name servers. Hostnames can
create a circular resolution dependency; Unbound detects this and logs a
warning, but the configuration still needs correction.

### Bound zone transfers when needed

`max-transfer-size` and `max-transfer-time` limit auth-zone and RPZ transfers.
Both are disabled by default, so configure them explicitly for bounded
resource use.
