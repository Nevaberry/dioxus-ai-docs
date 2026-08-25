# Platforms and Builds

## Build compatibility

### OpenSSL and dnstap independence

Unbound builds with OpenSSL 3 installations compiled with
`OPENSSL_NO_DEPRECATED` (1.21.0). Dnstap and `unbound-dnstap-socket` can also
link without OpenSSL.

### QUIC dependencies and probes

DNS over QUIC requires libngtcp2 and a QUIC-capable OpenSSL (1.22.0). Supply
both paths at configure time:

```sh
./configure --with-libngtcp2=/path/to/ngtcp2 --with-ssl=/path/to/openssl
```

QUIC configuration probes the available ngtcp2 early-data API and fails
clearly when the `ngtcp2_crypto_ossl` header is absent (1.26.0). Unbound also
compiles with OpenSSL 4.0.1.

### Reproducible timestamps

Builds prefer `SOURCE_DATE_EPOCH` over wall-clock time (1.23.0). The variable
is documented in `--help`.

### QNX

Unbound can be built for QNX (1.25.0).

## Windows

### Module startup

Module startup initializes `module-config` on Windows (1.21.0), so configured
processing modules are no longer silently skipped.

### OpenSSL configuration isolation

Windows builds initialize OpenSSL without loading `openssl.cnf` (1.25.0),
preventing a local configuration file from becoming a privilege-escalation
path. Move any behavior that depended on implicit loading into an explicit,
controlled configuration.

## BSD PF tables

The ipset integration supports BSD PF tables (1.21.0), enabling the
response-ip/ipset workflow on PF-based systems.

## Linux service integration

### Network readiness

The contributed `unbound.service` and `unbound_portable.service` templates
start after `network-online.target` (1.21.0). Locally installed copies inherit
this ordering only when updated from those templates.

### Network administration capability

Generated service units allow `CAP_NET_ADMIN` (1.24.0), supporting features
that require network-administration privilege.

### Control-key group access

Members of the `unbound` group can access the control key (1.23.0). Keep group
membership narrowly scoped because it conveys resolver-control capability.

## Contributed cryptography

RFC 9558 ECC-GOST12 support is supplied as `contrib/gost12.patch` (1.25.0).
It replaces the older GOST integration for deployments that intentionally
apply the contributed patch.

## Hook execution

`ipsecmod` hooks are launched with `execv`, not `system` (1.26.0). A hook must
be a directly executable program and scripts need an interpreter line:

```sh
#!/bin/sh
exit 0
```
