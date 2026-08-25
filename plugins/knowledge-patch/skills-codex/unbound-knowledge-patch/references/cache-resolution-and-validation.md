# Cache, resolution, and validation

## Cache fill, recursion, and aliases

### Named forwarder address fill

With nonzero `target-fetch-policy`, Unbound fetches and caches addresses for
forward-host names (since 1.21.0). A negative AAAA cache entry also stops its
associated recursion correctly.

### Limit-triggered failures

More resolver-limit failures are cached briefly as `SERVFAIL` (since 1.21.0).
Repeated queries can therefore observe the cached failure rather than
immediately repeating expensive work.

### Hardened missing-AAAA glue

`harden-unverified-glue` also controls missing AAAA lookups started by cache
fill (since 1.22.0), so enabling it hardens that path consistently.

### CNAME-aware prefetch lifetime

Prefetch lifetime is capped after a short-TTL CNAME (since 1.22.0), preventing
prefetched targets from outliving the alias path.

### DNAME and synthesized CNAME policy

Cache TTL policy applies to DNAME and synthesized CNAME data on the wire path
(since 1.25.0). A TTL-0 DNAME may provide a synthesized cached response for a
one-second grace period while clients still receive TTL 0. Out-of-zone DNAME
records do not participate in CNAME synthesis.

## Serve-expired and TTL handling

### Secure defaults

`serve-expired-ttl` defaults to `86400` and
`serve-expired-client-timeout` defaults to `1800` (since 1.23.0), following
RFC 8767 behavior.

### Refreshing expired entries

Not-yet-validated updates can refresh cache state again (since 1.23.0), fixing
the extra upstream traffic introduced in 1.22.0. Current delegation and
validation-recursion data may replace expired state, leaving less older,
DNSSEC-validated expired data for later use.

### Zero TTL and expired replies

Cached records expire at TTL 0 and upstream TTL-0 answers are not stored by
cachedb (since 1.24.0). `serve-expired-reply-ttl` cannot exceed the original
record TTL. High-order-bit TTL values are positive per RFC 8767 section 4,
not decoded as zero.

## External cachedb and Redis

### NSEC TTL limits

NSEC records restored from cachedb have their TTL limited (since 1.22.0)
instead of retaining an excessive cached value.

### Case-insensitive keys

Cachedb hashing ignores DNS-name case (since 1.23.0), so case variants share
the same Redis-backed records.

### Redis outage throttling

The Redis backend detects a down server and throttles reconnection attempts
(since 1.24.0).

### No-cache policy and validation

`forward-no-cache` and `stub-no-cache` prevent external cachedb lookup and
storage, including relevant ECS paths (since 1.25.0). Expired bogus data is no
longer returned as non-bogus, and aggressive-negative cached replies carry
the RA flag.

## EDNS Client Subnet

### Failure and cache selection

Failure to create an ECS subquery returns `SERVFAIL`, not `FORMERR` (since
1.24.0). For `0.0.0.0/0`, data without configured subnet treatment goes to
the global cache; configured treatment uses the subnet cache.

## DNS64 and NAT64

### Infra-cache attachment

NAT64-synthesized target addresses attach at the delegation point (since
1.24.0), allowing correct infra-cache operation.

### Retry exclusions

`do-nat64` and `do-not-query-address` interact consistently during retries
(since 1.25.0).

### Validation and policy preservation

DNSSEC-enabled DNS64 now checks successful validation of the AAAA query
(since 1.26.0). Synthesis preserves `rpz-passthru`, and ECS-scoped responses
stay out of the global cache.

## DNSSEC validation

### Iterator RRSIG cap

`iter-scrub-rrsig` limits RRSIGs retained by the iterator scrubber (since
1.25.0); the default is 8. Use it to bound oversized signature sets.

### Alias-chain checks

Validation accepts YXDOMAIN only with a DNAME, rejects signatures made by
revoked DNSKEYs, and applies stricter trust checks to DNAME-to-CNAME and
wildcard-CNAME chains (since 1.25.0).

### Proof and RSA-key handling

Libnettle builds accept noncanonical RSA DNSKEYs with leading-zero moduli and
calculate their size correctly (since 1.26.0). Negative caching handles
unsalted NSEC3. Signed wildcard NSEC records are checked before use as DS
proofs. Aggressive NSEC/NSEC3 rejects signer-zone mismatches, overreaching
next-owner names, and results outside the trust-anchor bailiwick.

## Reply safety

### Error and EOF behavior

Malformed requests receive error replies rather than silence, without
reflecting query fragments (since 1.25.0). CHAOS queries do not echo incoming
EDNS extended RCODEs. TCP EOF cancels pending replies and closes the
connection.

### Rebinding protection for service bindings

`private-address` filtering removes matching SVCB and HTTPS records as well as
address records (since 1.25.0), closing the non-address rebinding path.
