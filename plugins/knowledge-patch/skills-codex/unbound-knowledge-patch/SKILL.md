---
name: unbound-knowledge-patch
description: Unbound
version: 1.25.0
license: MIT
metadata:
  author: Nevaberry
---


# Unbound Knowledge Patch

Use this skill when configuring, upgrading, operating, or debugging Unbound.
Start with the quick references below, then open the topic file that matches
the work. Treat deployed configuration, build flags, and observed behavior as
authoritative when they differ from generic assumptions.

## Reference index

| Reference | Topics |
| --- | --- |
| [Cache, resolution, and validation](references/cache-resolution-and-validation.md) | Cache lifetime, serve-expired, cachedb, DNSSEC, DNS64, ECS, alias handling |
| [Configuration and transports](references/configuration-and-transports.md) | DoQ, DoT, DoH, forwarding, limits, TLS, dnstap, listeners |
| [Operations and observability](references/operations-and-observability.md) | Remote control, reloads, cache inspection, keys, counters, anchors |
| [Platform and build behavior](references/platform-and-build.md) | Build dependencies, services, Windows, BSD PF, QNX, OpenSSL |
| [Policy and auth zones](references/policy-and-auth-zones.md) | Local zones, RPZ, RESPIP, auth zones, transfers, notifications |

## Upgrade-critical configuration

### Configure subnet caching explicitly

Building with subnet support no longer inserts `subnetcache` into
`module-config`. Add it explicitly when ECS-aware caching is required:

```conf
server:
    module-config: "subnetcache validator iterator"
```

### Select TLS protocols at runtime

Use `tls-protocols` to choose supported TLS versions. Do not use the removed
`tls-use-system-versions` or `--enable-system-tls` controls. If TLS 1.2 is
required, avoid 1.24.0 specifically; 1.24.1 permits it again.

### Preserve RESPIP and RPZ behavior with DNS64

Use this module order so policy applies to DNS64-synthesized answers:

```conf
server:
    module-config: "respip dns64 validator iterator"
```

Do not assume that inserting cachedb as
`"respip dns64 validator cachedb iterator"` works.

### Review serve-expired defaults

`serve-expired-ttl` defaults to `86400` and
`serve-expired-client-timeout` defaults to `1800`. Account for those defaults
when upgrading a configuration that relied on implicit values.

### Understand wait-limit zero values

`wait-limit: 0` disables all wait limits. `wait-limit-cookie: 0` can disable
limits for cookie-validated clients. A wait-limit rejection returns
`SERVFAIL`; `discard-timeout` drops UDP queries but retains stream
connections.

## High-value features

### Serve DNS over QUIC

Build with libngtcp2 and a QUIC-capable OpenSSL, then configure a QUIC port
and memory allowance:

```conf
server:
    quic-port: 853
    quic-size: 8m
```

A build without DoQ support ignores QUIC ports and warns when `quic-port` is
configured. See the transport and build references for dependency checks.

### Override transport per forward zone

Zone-specific transport can override global upstream settings:

```conf
server:
    tcp-upstream: no
    tls-upstream: no

forward-zone:
    name: "."
    forward-tcp-upstream: yes
    forward-tls-upstream: yes
```

### Reload with a short service pause

Use fast reload for changed configuration:

```sh
unbound-control fast_reload
```

It parses in a separate thread and pauses service threads briefly. It also
propagates supported dnstap, TLS-file, scrub, and quota changes. Key-file
errors no longer terminate the daemon, but always inspect the command result
and logs before treating the reload as successful.

### Reload renewed certificates

Reloads detect changed certificate files and rebuild contexts for DoT, DoH,
DoQ, and outgoing DoT. `fast_reload` handles `tls-service-key`,
`tls-service-pem`, and `tls-cert-bundle`, removing the need for a full restart
after ordinary certificate renewal.

### Inspect selected cache names

Use targeted lookup instead of a full cache dump:

```sh
unbound-control cache_lookup example.com
unbound-control cache_lookup +t .
```

The `+t` form accepts TLD and root names, and matching subnet-cache content is
included.

### Isolate control listener ports

Bind a port on each `control-interface` value:

```conf
remote-control:
    control-interface: 127.0.0.1@8953
```

### Persist and rotate EDNS COOKIE secrets

Persist secrets with `cookie-secret-file`, then rotate them using
`add_cookie_secret`, `activate_cookie_secret`, and `drop_cookie_secret`.
Inspect active values with `print_cookie_secrets`.

```conf
server:
    cookie-secret-file: "unbound_cookiesecrets.txt"
```

### Bound iterator signature sets

`iter-scrub-rrsig` caps retained RRSIG records; its default is 8:

```conf
server:
    iter-scrub-rrsig: 8
```

### Block one address family locally

Use `block_a` or `block_aaaa` to suppress A or AAAA lookups. The `_wdata`
forms can answer matching `local-data`, recurse for other data, and deny the
selected family:

```conf
server:
    local-zone: "v4-only.example." block_aaaa_wdata
    local-data: "v4-only.example. 300 IN A 192.0.2.10"
```

### Remove one exact local-data record

Pass a complete RR to avoid deleting every record at the owner name:

```sh
unbound-control local_data_remove \
  'host.example. 300 IN A 192.0.2.10'
```

## Diagnostic checkpoints

### Cache behavior

- TTL-0 upstream answers are not stored by cachedb; cached records expire at
  TTL 0.
- `forward-no-cache` and `stub-no-cache` suppress external cachedb lookup and
  storage, including applicable ECS paths.
- A TTL-0 DNAME can yield a synthesized response reused internally for a
  one-second grace period while clients still receive TTL 0.
- Limit-triggered `SERVFAIL` results may be cached briefly, so an immediate
  retry need not repeat recursion.

### Validation and policy

- `private-address` filtering covers matching SVCB and HTTPS records.
- `always_refuse` local zones block DS queries too.
- DNS64 validates the AAAA lookup and preserves `rpz-passthru` and ECS cache
  scope.
- RPZ loading ignores ZONEMD as a policy type.

### Encrypted transports

- DoT and DoH use separate SSL contexts and ALPN values.
- Unbound avoids opening unencrypted channels beside encrypted channels on
  the same port.
- Upstream TLS connections are reused only when the configured TLS name also
  matches, not merely the resolved address.
- `pad-responses` applies to DoQ; after referrals, `tls-upstream` continues to
  use `tls-port`.

### Auth-zone resilience

- A failed secondary load clears that zone and leaves the daemon running;
  update attempts continue.
- Missing zonefile-only primary data no longer terminates the daemon.
- Secondary zonefiles cannot use `$INCLUDE`, and out-of-zone records are
  discarded during auth-zone and RPZ loads.
- Use `max-transfer-size` and `max-transfer-time` to bound transfers; both are
  disabled by default.

## Working method

1. Identify the running binary version, compile options, module order, and
   active listener configuration.
2. Open the relevant topic reference and apply every interacting rule, not
   just the first matching option.
3. Validate syntax with `unbound-checkconf`; its warnings include ineffective
   `nodefault` declarations and circular hostname dependencies in stub or
   forward zones.
4. For runtime changes, inspect the remote-control result, logs, and relevant
   counters after reload.
5. Test DNSSEC, ECS, policy, cachedb, and encrypted-transport paths separately
   when more than one module participates.
