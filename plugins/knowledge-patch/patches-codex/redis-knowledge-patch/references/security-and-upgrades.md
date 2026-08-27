# Security, Upgrades, and Access Control

Use this reference before patching, migrating, or changing authentication and
authorization. Choose maintenance releases by the deployed minor line.

## Integrated components and supported upgrade sources

Redis 8.0 makes Search, JSON, Time Series, Bloom, Cuckoo, Count-min sketch,
Top-k, and t-digest integral and includes them in binary distributions.
`redis-full.conf` loads all components, while Vector Set is marked preview.

Replication or persistence upgrades are supported from module-free Redis,
Redis using the former standalone modules, and Redis Stack 7.2 or 7.4. Treat
component packaging and ACL expansion as part of the same migration. These
integration changes are attributed to source batch `8.0-8.6`.

## ACL category expansion

Starting in 8.0, broad categories such as `@read` and `@write` include Search,
JSON, Time Series, and probabilistic commands. An old rule can therefore grant
or remove more access than before. Audit custom ACLs and prefer `@search`,
`@json`, `@timeseries`, `@bloom`, `@cuckoo`, `@cms`, `@topk`, and `@tdigest`
when narrower control is required.

## Search and Time Series key-pattern scope

An ACL user can create, modify, or read a Search index only if the user's key
patterns cover a superset of the index prefixes.

`TS.MGET`, `TS.MRANGE`, and `TS.MREVRANGE` fail if any matching key is
unreadable. `TS.QUERYINDEX` reads metadata only, so it does not require read
access to the matched keys.

## Security patch floors

Do not compare patch suffixes across minor lines. Select the fixed release for
the deployed minor series.

| Fixed release or releases | Security issue |
| --- | --- |
| 8.0.2 | `redis-check-aof` stack overflow with RCE impact |
| 8.0.3 | HyperLogLog out-of-bounds writes |
| 8.0.4 | Four Lua memory and isolation CVEs |
| 8.0.5 | Probabilistic-filter memory-safety failures |
| 8.0.6 | CRLF error-reply injection |
| 8.2.3 | `XACKDEL` stack overflow with RCE impact |
| 8.2.5, 8.4.2, or 8.6.1 | Response injection |
| 8.2.6, 8.4.3, or 8.6.3 | Five RCE-capable use-after-free or invalid-memory paths |
| 8.6.2 | Module-string reply-copy use-after-free |
| 8.2.8, 8.4.5, or 8.6.5 | Stream consumer-group `RESTORE` use-after-free with RCE impact |
| 8.4.4 | `MSETEX` ACL key-pattern bypass |
| 8.6.4 | Configuration injection through `SENTINEL SET` |

The five-path RCE group spans client unblock, `RESTORE`, Lua, Time Series, and
probabilistic structures.

## Log privacy hardening

Redis 8.2.4 and 8.4.1 redact personally identifiable information from JSON
and Time Series server logs. Treat the maintenance floors in the table as
separate from these log-privacy releases.

## Crafted `RESTORE` payloads in RedisBloom and TDigest

Redis 8.8.1 fixes out-of-bounds writes triggered by crafted `RESTORE` payloads
in RedisBloom and TDigest. The writes could lead to remote code execution, so
security-sensitive deployments must not remain below this fix.

## Security floor from batch 8.10.0

Use at least Redis 8.10.1 on the 8.10 line. It fixes memory-safety issues in:

- CMSketch RDB loading;
- TopK cleanup;
- the TLS pending-data list;
- `SLOT_INFO` RDB loading;
- three Vector Set paths; and
- blocked-client reprocessing.

The crafted `SLOT_INFO` case may allow remote code execution. Redis 8.10.1
also fixes a TLS client-certificate authentication bypass caused by an
embedded NUL byte in the certificate Common Name.

## Certificate-based TLS authentication

For client connections, Redis 8.6 can automatically authenticate a certificate
as the user configured by `tls-auth-clients-user`. Failed certificate-based
attempts increment `acl_access_denied_tls_cert`.

Redis 8.10 adds peer certificate-based authentication for TLS connections
between servers. Treat this as a separate server-to-server trust decision from
client certificate-to-user mapping.

## Tested Redis 8.8 platforms

Redis 8.8 is tested on:

- Ubuntu 22.04, 24.04, and 26.04;
- Rocky Linux and AlmaLinux 8.10, 9.7, and 10.1;
- Debian 12.13 and 13.4;
- Alpine 3.23; and
- macOS 14.8.4, 15.7.4, and 26.3 on Intel and ARM.
