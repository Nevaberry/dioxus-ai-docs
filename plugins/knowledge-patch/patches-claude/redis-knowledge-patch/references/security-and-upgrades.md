# Security, Upgrades, and Access Control

## Security patch floors

The `8.0-8.6` extraction batch identifies the following minimum fixes. Choose
the release on the deployed minor line; a larger patch number on another minor
line is not evidence that the fix is present.

| Issue area | Fixed release or releases |
| --- | --- |
| `redis-check-aof` stack overflow with RCE impact | 8.0.2 |
| HyperLogLog out-of-bounds writes | 8.0.3 |
| Four Lua memory and isolation CVEs | 8.0.4 |
| Probabilistic-filter memory-safety failures | 8.0.5 |
| CRLF error-reply injection | 8.0.6 |
| `XACKDEL` stack overflow with RCE impact | 8.2.3 |
| Response injection | 8.2.5, 8.4.2, or 8.6.1 |
| Five RCE-capable use-after-free or invalid-memory paths | 8.2.6, 8.4.3, or 8.6.3 |
| Module-string reply-copy use-after-free | 8.6.2 |
| Stream consumer-group `RESTORE` use-after-free with RCE impact | 8.2.8, 8.4.5, or 8.6.5 |
| `MSETEX` ACL key-pattern bypass | 8.4.4 |
| `SENTINEL SET` configuration injection | 8.6.4 |

The five-path RCE group covers client unblock, `RESTORE`, Lua, Time Series,
and probabilistic structures.

## Crafted `RESTORE` payloads

Redis 8.8.1 fixes out-of-bounds writes caused by crafted `RESTORE` payloads in
RedisBloom and TDigest. Treat affected deployments as exposed to remote code
execution until upgraded.

## Redis 8.10 security floor

The `8.10.0` batch records Redis 8.10.1 as the security floor for the 8.10
line. It fixes memory-safety defects in CMSketch RDB loading, TopK cleanup, the
TLS pending-data list, `SLOT_INFO` RDB loading, three Vector Set paths, and
blocked-client reprocessing. A crafted `SLOT_INFO` payload may permit remote
code execution.

Redis 8.10.1 also fixes TLS client-certificate authentication bypass caused by
an embedded NUL byte in a certificate Common Name. Security-sensitive 8.10
deployments should use at least 8.10.1.

## Log privacy and ACL hardening

Redis 8.2.4 and 8.4.1 redact personally identifiable information from JSON and
Time Series server logs. Redis 8.4.4 fixes the `MSETEX` ACL key-pattern bypass,
and Redis 8.6.4 fixes configuration injection through `SENTINEL SET`.

## Integrated component distribution

Beginning in Redis 8.0, Search, JSON, Time Series, Bloom, Cuckoo, Count-min
sketch, Top-k, and t-digest are integral components included in binary
distributions. `redis-full.conf` loads all components. Vector Set is preview
functionality.

Replication or persistence upgrades are supported from:

- Redis without modules;
- Redis using the former standalone modules; and
- Redis Stack 7.2 or 7.4.

Treat integrated packaging, configuration loading, and ACL expansion as one
migration concern.

## Expanded ACL categories

From Redis 8.0, broad categories such as `@read` and `@write` include Search,
JSON, Time Series, and probabilistic commands. An older ACL rule may therefore
grant or remove more access after an upgrade.

Audit custom users and prefer narrower categories where appropriate:

- `@search`
- `@json`
- `@timeseries`
- `@bloom`
- `@cuckoo`
- `@cms`
- `@topk`
- `@tdigest`

## Search and Time Series ACL scope

A user may create, modify, or read a Search index only when the user's key
patterns cover a superset of that index's prefixes.

`TS.MGET`, `TS.MRANGE`, and `TS.MREVRANGE` fail if any matching key is not
readable by the user. `TS.QUERYINDEX` reads metadata only and does not require
read permission for the matched keys.

## TLS certificate authentication

Redis 8.6 supports automatic client authentication from TLS certificates.
Configure the mapped user with `tls-auth-clients-user`. Failed certificate
authentication attempts increment `acl_access_denied_tls_cert`.

Redis 8.10 adds peer certificate-based authentication for server-to-server
TLS connections. Keep this separate from the client mapping behavior and apply
the 8.10.1 embedded-NUL security fix.

## Tested Redis 8.8 platforms

Redis 8.8 is tested on:

- Ubuntu 22.04, 24.04, and 26.04;
- Rocky Linux and AlmaLinux 8.10, 9.7, and 10.1;
- Debian 12.13 and 13.4;
- Alpine 3.23; and
- macOS 14.8.4, 15.7.4, and 26.3 on Intel and ARM.

Treat this as the tested-platform matrix, not a claim that other platforms are
unsupported.
