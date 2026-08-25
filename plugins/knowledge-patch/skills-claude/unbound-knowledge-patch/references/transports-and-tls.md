# Transports and TLS

## DNS over QUIC

Build DoQ support against libngtcp2 and a QUIC-capable OpenSSL with
`--with-libngtcp2=path --with-ssl=path` (1.22.0), then configure:

```conf
server:
    quic-port: 853
    quic-size: 8m
```

A build without DoQ support ignores configured QUIC ports and warns when
`quic-port` is set. Statistics include `num.query.quic` and `mem.quic`.

The QUIC TLS context is initialized before chroot and privilege drop, and a
QUIC listening context is created only when necessary (1.23.0).

Adding HTTPS or QUIC ports to `interface-automatic-ports` initializes the
corresponding protocol (1.24.0).

`pad-responses` applies to DoQ responses (1.26.0). QUIC builds probe the ngtcp2
early-data API and fail explicitly if `ngtcp2_crypto_ossl` is missing; they
also build with OpenSSL 4.0.1.

## Listener isolation

DoT and DoH use separate SSL contexts and can therefore advertise different
ALPN values (1.23.0). Unbound avoids opening an unencrypted channel alongside
an encrypted one on the same port.

## Upstream transport selection

### Per-forward-zone overrides

`forward-tcp-upstream` and `forward-tls-upstream` override global
`tcp-upstream` and `tls-upstream` for one forward zone (1.22.0):

```conf
server:
    tcp-upstream: no
    tls-upstream: no

forward-zone:
    name: "."
    forward-tcp-upstream: yes
    forward-tls-upstream: yes
```

### TLS port after referrals

`tls-upstream` continues using `tls-port` after a referral (1.26.0).

### Name-bound connection reuse

An upstream TLS connection is reused only when its TLS name matches the next
destination, even if both names resolve to the same IP address (1.25.0).

## TLS protocol compatibility

`tls-protocols` explicitly selects supported TLS versions (1.25.0). The
short-lived `tls-use-system-versions` and configure-time
`--enable-system-tls` controls were removed before release in favor of this
runtime option.

Unbound 1.24.0 disabled TLS 1.2, while 1.24.1 permitted it again (1.24.0).
Deployments that require TLS 1.2 must not stay on 1.24.0.

## Certificate-aware reloads

Reload detects changed certificate files and rebuilds TLS contexts for DoT,
DoH, DoQ, and outgoing DoT (1.25.0), so normal certificate renewal does not
require a full restart. `fast_reload` handles `tls-service-key`,
`tls-service-pem`, and `tls-cert-bundle` changes.

## Protocol error and connection behavior

Malformed errors receive a response without reflecting query fragments, and
CHAOS queries do not echo incoming EDNS extended RCODEs (1.25.0). A TCP client
EOF cancels pending replies and closes the connection.

## DoH client interoperability

The `dohclient` utility includes `content-length` on POST requests (1.26.0),
preventing strict DoH resolvers from rejecting them with HTTP 400.
