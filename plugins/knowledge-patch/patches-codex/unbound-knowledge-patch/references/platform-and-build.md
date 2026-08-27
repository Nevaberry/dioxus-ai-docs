# Platform and build behavior

## Service integration

### Network-online ordering

The contributed `unbound.service` and `unbound_portable.service` start after
`network-online.target` (since 1.21.0). Locally installed copies of these
templates inherit that boot ordering when updated.

### Network-administration capability

Generated service units allow `CAP_NET_ADMIN` (since 1.24.0), supporting
features that require network-administration privileges.

## Build dependencies and reproducibility

### OpenSSL and dnstap compatibility

Builds support OpenSSL 3 compiled with `OPENSSL_NO_DEPRECATED` (since 1.21.0).
Dnstap and `unbound-dnstap-socket` can link without OpenSSL.

### QUIC dependencies

DoQ builds use libngtcp2 and a QUIC-enabled OpenSSL with
`--with-libngtcp2=path --with-ssl=path` (since 1.22.0). Runtime configuration
cannot add DoQ support to a binary built without it.

### Reproducible timestamps

Builds prefer `SOURCE_DATE_EPOCH` to the wall-clock build time (since 1.23.0),
and `--help` documents the variable.

### QUIC and OpenSSL checks

Unbound compiles with OpenSSL 4.0.1 (since 1.26.0). QUIC configuration probes
the available ngtcp2 early-data API and fails explicitly if the
`ngtcp2_crypto_ossl` header is absent.

## Operating-system behavior

### Windows module initialization

Windows startup initializes `module-config` and configured processing modules
(since 1.21.0), instead of silently skipping module setup.

### BSD PF tables

The ipset integration supports BSD PF tables (since 1.21.0), enabling the
response-ip/ipset workflow on PF-based systems.

### Windows OpenSSL isolation

Windows builds initialize OpenSSL without loading `openssl.cnf` (since
1.25.0), preventing local configuration from becoming a privilege-escalation
path. Move any behavior that relied on that implicit file to explicit
configuration.

### QNX support

Unbound can be built for QNX (since 1.25.0).

## Contributed integrations

### ECC-GOST12

RFC 9558 ECC-GOST12 support is supplied as `contrib/gost12.patch` (since
1.25.0), replacing the older GOST integration for deployments that apply the
contributed patch.

### Executable ipsecmod hooks

`ipsecmod` launches its hook with `execv`, not `system` (since 1.26.0). The
hook must be executable and begin with an interpreter line, for example
`#!/bin/sh`.
