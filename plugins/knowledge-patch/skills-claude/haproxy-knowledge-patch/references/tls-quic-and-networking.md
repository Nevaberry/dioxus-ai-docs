# TLS, QUIC, and Networking

## Frontend certificate policy

### Per-certificate TLS settings (since 3.2.0)

The frontend `ssl-f-use` directive references a certificate from a
`crt-store` independently of `bind`. It can attach per-certificate TLS
versions, ALPN, ciphers, and signature algorithms without an external
crt-list.

```haproxy
crt-store my_files
    load crt "foo.com.crt" key "foo.com.key" alias "foo"

frontend mysite
    bind :443 ssl
    ssl-f-use crt "@my_files/foo" ssl-min-ver TLSv1.2
```

### Passphrase-protected keys (since 3.3.0)

The global `ssl-passphrase-cmd` directive names a script that returns the
passphrase for a protected TLS key. Previously retrieved passphrases are tried
before the script runs again.

```haproxy
global
    ssl-passphrase-cmd /usr/local/bin/tls-key-passphrase
```

### Experimental Encrypted Client Hello (since 3.3.0)

The `ech` argument on a TLS `bind` enables Encrypted Client Hello and requires
`expose-experimental-directives`. Clients must be able to retrieve the
corresponding public key from DNS.

### Automatic backend SNI (since 3.3.0)

For server-side TLS, HAProxy derives SNI automatically from the HTTP `host`
header. `sni-auto` and `no-sni-auto` control this for traffic;
`check-sni-auto` and `no-check-sni-auto` control it for health checks.

Combining `strict-sni` with `default-crt` on a frontend `bind` warns.

## ACME automation

### Experimental HTTP-01 flow (since 3.2.0)

The built-in ACME implementation is experimental, requires
`expose-experimental-directives`, and is intended for a single load balancer.
An `acme` section defines the directory, account, HTTP-01 challenge, and
virtual challenge map. A `crt-store` load associates a certificate and its
domains with that account.

```haproxy
global
    expose-experimental-directives

acme letsencrypt-staging
    directory https://acme-staging-v02.api.letsencrypt.org/directory
    account-key /etc/haproxy/account.key
    contact admin@example.com
    challenge HTTP-01
    map virt@acme

crt-store my_files
    crt-base /etc/haproxy/
    key-base /etc/haproxy/
    load crt "example.com.pem" acme letsencrypt-staging domains "example.com" alias "example"
```

The HTTP frontend must serve `/.well-known/acme-challenge/` from the ACME map.
`acme renew @my_files/example` starts issuance and `acme status` lists tasks.
The resulting certificate exists only in running memory until
`dump ssl cert @my_files/example` is saved to a file.

### DNS-01 through the Data Plane API (since 3.3.0)

ACME supports DNS-01 challenges through HAProxy Data Plane API 3.3. The API
communicates with the DNS provider and saves issued certificates to the load
balancer's filesystem. This remains intended for a single load balancer;
multiple instances require manual certificate synchronization.

## TLS controls

### TLS tracing (since 3.2.0)

The Runtime API `trace` command has an `ssl` source for TLS-related events.

### TLS 1.3 KeyUpdate rate limiting (since 3.4.3)

`tune.ssl.keyupdate-rate-limit` rate-limits TLS 1.3 KeyUpdate processing and
provides an explicit bound for peer-triggered key updates.

### Kernel TLS support (since 3.3.0)

The default `linux-glibc` build target requires Linux 4.17 to support Kernel
TLS.

## QUIC handshake policy

### Initial rules (since 3.1.0)

`quic-initial` rules run during the QUIC handshake and support `reject`,
`accept`, `dgram-drop` for a silent drop, and `send-retry`. They allow abuse
prevention and source filtering before a client completes a handshake.

```haproxy
quic-initial dgram-drop if { src 192.0.2.0/24 }
```

## QUIC pacing and memory

### Frontend controls (since 3.2.0)

Selecting `quic-cc-algo` enables transmit pacing automatically, and `bbr` no
longer requires experimental directives. `tune.quic.disable-tx-pacing`
disables pacing.

QUIC upload streams may use 90% of connection memory by default. Adjust that
ratio with `tune.quic.frontend.stream-data-ratio` in 3.2.0.
`tune.quic.frontend.max-tx-mem` adds an optional global transmit-buffer cap.
`haproxy -vv` reports socket-owner and GSO support.

The `tune.quic.frontend.*` namespace is deprecated as of 3.3.0; use
`tune.quic.fe.*` for those global directives.

### Backend controls (since 3.3.0)

Backend QUIC tuning is under `tune.quic.be.*` for congestion control, idle
timeouts, glitch thresholds, streams, pacing, and UDP GSO. The process-wide
transmit-memory cap is `tune.quic.mem.tx-max`.

### Per-side congestion control and connection lifetime (since 3.4.0)

`quic-cc-algo` is valid on `server` as well as `bind`, allowing frontend and
backend congestion control to differ. This change was also backported to 3.3.

`tune.quic.fe.stream.max-total` caps total requests handled by one QUIC
connection. At the limit HAProxy sends an HTTP/3 GOAWAY and closes the
connection after remaining transfers finish.

## HTTP/3 and QMux backends

### Experimental HTTP/3 backends (since 3.3.0)

Prefix a backend server address with `quic4@` to connect over HTTP/3 and QUIC.
This requires `expose-experimental-directives` and the normal backend TLS
verification settings.

```haproxy
global
    expose-experimental-directives

backend webservers
    server web1 quic4@172.16.0.11:443 check ssl verify required ca-file /etc/haproxy/ssl/myca.pem
```

### Experimental QMux over TCP (since 3.4.0)

QMux carries QUIC frames over an ordered reliable byte stream, allowing
HTTP/3 between HAProxy endpoints where UDP is unavailable. It requires
`expose-experimental-directives` and `alpn h3` on the relevant TCP `bind` or
`server` line.

```haproxy
global
    expose-experimental-directives

backend webservers
    server web1 127.0.0.1:443 ssl verify none alpn h3,h2
```

## Transport and socket controls

### TCP MD5 signatures (since 3.3.0)

The `tcp-md5sig` argument on `bind` and `server` lines supports the TCP MD5
Signature Option required by many BGP peers when HAProxy proxies their
sessions.

### TCP congestion control (since 3.3.0)

The `cc` argument on a `bind` or `server` line selects the TCP
congestion-control algorithm for that listener or upstream server.

### Kernel send-buffer limits (since 3.2.0)

The global `tune.notsent-lowat.client` and `tune.notsent-lowat.server`
directives can minimize kernel-side socket buffers and unacknowledged data to
reduce memory use.

### Global QUIC listener switch (since 3.3.0)

The global `no-quic` directive is replaced by `tune.quic.listen`. Its `on` and
`off` values enable or disable QUIC on all frontend listeners.
