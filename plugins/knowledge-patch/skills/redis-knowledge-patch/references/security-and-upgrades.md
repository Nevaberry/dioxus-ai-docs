# Security, Upgrades, and Access Control

Use this reference when selecting a maintenance release, moving from standalone
modules or Redis Stack, auditing ACLs, configuring client certificates, or
validating a deployment platform.

## Integrated distribution and supported upgrade paths

Starting with Redis 8.0, Search, JSON, Time Series, Bloom, Cuckoo, Count-min
sketch, Top-k, and t-digest are integral components included in Redis binary
distributions. `redis-full.conf` loads every component, while Vector Set is
marked preview. Replication or persistence upgrades are supported from these
starting points:

- module-free Redis;
- Redis with the former standalone modules; and
- Redis Stack 7.2 or 7.4.

These packaging and migration details are covered by batch `8.0-8.6`.

## ACL expansion and command scope

Existing ACL categories such as `@read` and `@write` include Search, JSON, Time
Series, and probabilistic commands starting in 8.0. An unchanged rule can
therefore grant or remove more access after an upgrade. Audit custom ACLs and
use component-specific categories when narrower control is required:

- `@search`
- `@json`
- `@timeseries`
- `@bloom`
- `@cuckoo`
- `@cms`
- `@topk`
- `@tdigest`

For Search, a user can create, modify, or read an index only when the user's key
patterns cover a superset of that index's prefixes.

Time Series multi-key reads enforce access differently by command:

- `TS.MGET`, `TS.MRANGE`, and `TS.MREVRANGE` return an error if any matching
  key is unreadable.
- `TS.QUERYINDEX` reads only metadata and does not require read access to the
  keys it matches.

## Security maintenance floors

Apply the fix on the deployed minor line. The named floors are issue-specific;
they are not interchangeable markers of general support status.

| Fixed release or releases | Security issue |
| --- | --- |
| 8.0.2 | `redis-check-aof` stack overflow with possible remote code execution |
| 8.0.3 | HyperLogLog out-of-bounds writes |
| 8.0.4 | Four Lua memory and isolation CVEs |
| 8.0.5 | Probabilistic-filter memory-safety failures |
| 8.0.6 | CRLF error-reply injection |
| 8.2.3 | `XACKDEL` stack overflow with possible remote code execution |
| 8.2.5, 8.4.2, and 8.6.1 | Response injection |
| 8.2.6, 8.4.3, and 8.6.3 | Five RCE-capable use-after-free or invalid-memory paths involving client unblock, `RESTORE`, Lua, Time Series, and probabilistic structures |
| 8.6.2 | Module-string reply-copy use-after-free |
| 8.2.8, 8.4.5, and 8.6.5 | Stream consumer-group `RESTORE` use-after-free with possible remote code execution |
| 8.4.4 | `MSETEX` ACL key-pattern bypass |
| 8.6.4 | Configuration injection through `SENTINEL SET` |

Redis 8.8.1 fixes out-of-bounds writes caused by crafted `RESTORE` payloads in
RedisBloom and TDigest. The writes could lead to remote code execution. This is
the security-critical item from batch `8.8.1`.

## Log privacy

Redis 8.2.4 and 8.4.1 redact personally identifiable information from JSON and
Time Series server logs. Do not treat older logs as having the same privacy
behavior.

## TLS certificate-based authentication

Redis 8.6 can automatically authenticate TLS clients by certificate. Configure
the mapped user with `tls-auth-clients-user`. Failed certificate authentication
attempts increment `acl_access_denied_tls_cert`.

## Redis 8.8 tested platforms

Redis 8.8 is tested on the following operating-system releases and processor
families:

| Platform | Tested releases |
| --- | --- |
| Ubuntu | 22.04, 24.04, and 26.04 |
| Rocky Linux | 8.10, 9.7, and 10.1 |
| AlmaLinux | 8.10, 9.7, and 10.1 |
| Debian | 12.13 and 13.4 |
| Alpine | 3.23 |
| macOS | 14.8.4, 15.7.4, and 26.3 on Intel and ARM |
