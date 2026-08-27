# Configuration and transports

## Listener and upstream transports

### DNS over QUIC

DoQ requires a build against libngtcp2 and a QUIC-enabled OpenSSL using
`--with-libngtcp2=path --with-ssl=path` (since 1.22.0). Configure
`quic-port: 853` and, for example, `quic-size: 8m`. Statistics include
`num.query.quic` and `mem.quic`. A build without DoQ ignores configured QUIC
ports and warns when `quic-port` is set.

### Per-forward-zone transport

`forward-tcp-upstream` and `forward-tls-upstream` override global
`tcp-upstream` and `tls-upstream` for one forward zone (since 1.22.0).

### Encrypted listener separation

DoT and DoH use separate SSL contexts and can advertise different ALPN values
(since 1.23.0). Unbound also avoids opening an unencrypted channel alongside
an encrypted channel on the same port.

### QUIC initialization and confinement

The QUIC SSL context is created before chroot and privilege drop, and a QUIC
listening context is created only when needed (since 1.23.0).

### Automatic encrypted-port activation

HTTPS and QUIC ports listed in `interface-automatic-ports` initialize their
protocol automatically (since 1.24.0).

### Name-bound upstream TLS reuse

An existing upstream TLS connection is reused only when its TLS name matches
the new destination, even when both names resolve to one address (since
1.25.0).

### Encrypted-transport corrections

`pad-responses` covers DoQ replies (since 1.26.0). `tls-upstream` continues to
use `tls-port` after a referral. The `dohclient` utility sends
`content-length` on POST requests, avoiding HTTP 400 from strict DoH servers.

## TLS configuration and reload

### TLS 1.2 patch-release behavior

Unbound 1.24.0 disabled TLS 1.2, while 1.24.1 permits it again. A deployment
that requires TLS 1.2 must not remain on 1.24.0.

### Explicit protocol selection

Use `tls-protocols` to select supported TLS versions (since 1.25.0). The
transient `tls-use-system-versions` and `--enable-system-tls` controls were
removed before release.

### TLS-aware reloads

Reload detects changed certificate files and rebuilds contexts for DoT, DoH,
DoQ, and outgoing DoT (since 1.25.0). `fast_reload` handles
`tls-service-key`, `tls-service-pem`, and `tls-cert-bundle`; it also propagates
`iter-scrub-ns`, `iter-scrub-cname`, and `max-global-quota` changes.

## Module configuration

### Explicit subnet cache

`module-config` defaults to `"validator iterator"` regardless of
`--enable-subnet` (since 1.23.0). Configure
`"subnetcache validator iterator"` explicitly when needed.

### RESPIP and RPZ with DNS64

Use `module-config: "respip dns64 validator iterator"` so RESPIP and RPZ apply
to DNS64-synthesized answers (since 1.24.0). The order
`"respip dns64 validator cachedb iterator"` is explicitly not known to work.

## Resource and request limits

### Wait limits and quota

Loopback addresses are exempt from `wait-limit` (since 1.23.0).
`wait-limit-netblock` and `wait-limit-cookie-netblock` accept their
two-argument forms, and statistics expose wait-limit and discard-timeout
activity. `max-global-quota` defaults to 200 rather than 128, while retaining
a bounded amplification factor.

### Zero values and discard behavior

`wait-limit: 0` disables all wait limits and `wait-limit-cookie: 0` can disable
cookie-validated limits (since 1.24.0). Exceeding a wait limit returns
`SERVFAIL`. `discard-timeout` drops UDP requests, not stream connections.

### Socket-buffer warning

Unbound warns when the operating system rejects the requested `so-sndbuf`
`setsockopt` value (since 1.24.0).

## Reporting, tracing, and backends

### Dnstap sampling

`dnstap-sample-rate` emits one of every N messages (since 1.21.0), reducing
high-volume dnstap output:

```conf
dnstap:
    dnstap-sample-rate: 100
```

### DNS Error Reporting

Enable RFC 9567 reporting with `dns-error-reporting` (since 1.23.0). Sent
reports are counted by `num.dns_error_reports`.

### Redis read-only replicas

The Redis cachedb backend provides `redis-replica-*` options for read-only
replicas (since 1.23.0).

## Remote-control listeners

### Per-interface control port

`control-interface` accepts `IP@port` (since 1.25.0), allowing each listener
to select its own port:

```conf
remote-control:
    control-interface: 127.0.0.1@8953
```
