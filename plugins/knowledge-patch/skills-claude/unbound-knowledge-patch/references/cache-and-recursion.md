# Cache and Recursion

## Recursive cache fill and failure handling

### Named forwarder addresses

With a nonzero `target-fetch-policy`, cache fill fetches and caches addresses
for forward-host names (1.21.0). Negative AAAA cache entries now stop the
associated recursion correctly.

### Limit-triggered failures

More resolver-limit failures cache their `SERVFAIL` briefly (1.21.0). An
immediate retry may therefore observe the cached failure instead of starting
the expensive work again.

### Missing AAAA glue

`harden-unverified-glue` governs missing AAAA lookups initiated by cache fill
(1.22.0), making the hardening choice consistent on this recursion path.

### Auth-zone-aware forwarder checks

Forwarder checks account for configured auth zones (1.23.0). Do not diagnose a
forwarding decision without checking whether an auth zone covers the name.

## TTL and prefetch behavior

### Cachedb NSEC TTL limits

NSEC records restored from cachedb have their TTL limited (1.22.0) rather than
retaining an excessive externally cached value.

### CNAME-aware prefetch

Prefetch TTL is limited after a short-TTL CNAME (1.22.0), so prefetched target
data cannot outlive the short-lived alias path.

### Serve-expired defaults and refresh

`serve-expired-ttl` defaults to `86400` and
`serve-expired-client-timeout` to `1800` (1.23.0), following the secure
serve-stale behavior of RFC 8767. Pin older policy explicitly if required.

Not-yet-validated updates can refresh the cache again (1.23.0), correcting the
extra upstream work seen after the earlier regression. Current delegation and
validation-recursion data may replace expired state; as a consequence, less
older DNSSEC-validated expired data can remain available later.

### Zero-TTL and expired replies

Cached records expire when they reach TTL 0, and upstream TTL-0 records are not
stored in cachedb (1.24.0). `serve-expired-reply-ttl` is capped by the original
record TTL. High-order-bit TTL values are decoded as positive per RFC 8767
section 4 instead of being treated as zero.

### DNAME and synthesized CNAME policy

Cache TTL policy applies to DNAME and synthesized CNAME data on the wire path
(1.25.0). A response synthesized from a TTL-0 DNAME can be reused internally
for a one-second grace period to prevent repeated recursion, while clients
still receive TTL 0. Out-of-zone DNAME records are excluded from CNAME
synthesis.

## Redis cachedb behavior

### Read-only replicas

The Redis backend provides `redis-replica-*` options for reads from read-only
replicas (1.23.0).

### Reload independence

A reload does not fail merely because Redis cannot connect or respond
(1.23.0). Unbound logs the error and checks expiration capabilities only when
the server is available.

### Case-insensitive keys

Cachedb hashing ignores DNS-name letter case (1.23.0), so case variants share
the same Redis-backed records.

### Outage reconnect throttling

The Redis backend detects a down server and throttles reconnect attempts
(1.24.0), reducing repeated connection pressure during an outage.

## External cachedb policy and validation

`forward-no-cache` and `stub-no-cache` block both lookup and storage in an
external cachedb, including applicable EDNS Client Subnet paths (1.25.0).
Expired bogus data is no longer returned as non-bogus, and aggressive-negative
answers restored from cache carry the RA flag.

## EDNS Client Subnet cache semantics

A failure to create an ECS subquery returns `SERVFAIL`, not `FORMERR`
(1.24.0). For `0.0.0.0/0`, data without configured subnet treatment enters the
global cache; configured subnet treatment uses the subnet cache.

The subnet module is no longer enabled implicitly by a subnet-capable build
(1.23.0). Configure it explicitly when needed:

```conf
server:
    module-config: "subnetcache validator iterator"
```

## Quota behavior

`max-global-quota` defaults to `200` instead of `128` while keeping a bounded
amplification factor (1.23.0). Re-evaluate explicit tuning and monitoring
thresholds when upgrading.
