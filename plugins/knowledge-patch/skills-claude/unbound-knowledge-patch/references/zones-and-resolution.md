# Zones and Resolution

## Local zones and local data

### Dynamic always_nxdomain zones

An `always_nxdomain` zone added with `unbound-control` locates its parent
correctly (1.21.0), restoring reliable dynamic blocking.

### Default special-use zones

`resolver.arpa` and `service.arpa` are served locally by default (1.23.0).
Upgrades can therefore change whether queries for these names are forwarded.

### Address-family blocking

`block_aaaa` suppresses AAAA lookups as `block_a` suppresses A lookups
(1.26.0). `block_a_wdata` and `block_aaaa_wdata` serve matching local data,
recurse transparently for other data, and deny the chosen address family:

```conf
server:
    local-zone: "v4-only.example." block_aaaa_wdata
    local-data: "v4-only.example. 300 IN A 192.0.2.10"
```

### Exact record removal

`local_data_remove` accepts a complete record (1.26.0), allowing removal of
one RR without deleting all local data at its owner:

```sh
unbound-control local_data_remove \
  'host.example. 300 IN A 192.0.2.10'
```

### Local-zone diagnostics

`unbound-checkconf` warns when a `nodefault` declaration has no effect
(1.25.0). An `always_refuse` zone also blocks DS queries (1.25.0).

## Response Policy Zones

Tags on tagged RPZ zones are honored (1.21.0), correcting the regression that
ignored them after an upgrade from 1.19.3 to 1.20.0.

When an RPZ local-CNAME rewrite introduces an alias, resolution follows the
CNAME chain (1.24.0) rather than stopping at the rewritten CNAME.

RESPIP and RPZ apply to DNS64-synthesized answers with this order (1.24.0):

```conf
server:
    module-config: "respip dns64 validator iterator"
```

Inserting cachedb as `"respip dns64 validator cachedb iterator"` is explicitly
not known to work.

ZONEMD is ignored as an RPZ policy type while a zone is loaded (1.25.0),
preventing the record from breaking root-key priming.

## Auth zones

### Status and timestamps

Status reporting is available for auth zones (1.24.0). The acquired timestamp
is set only after the zonefile has actually been read.

### HTTP-downloaded origins

An HTTP-downloaded auth-zone file can use an empty-label `$ORIGIN` (1.24.0).

### Notification names

Hostname entries in `allow-notify` retain resolved IPv4 and IPv6 addresses and
are resolved even when an auth zone has only URL transfer sources (1.25.0).
Configured notification addresses and netblocks are available from server
startup (1.26.0).

### Failed loads

The daemon remains up when a secondary zone cannot load or a zonefile-only
primary is missing its file (1.26.0). A failed secondary load clears that zone
instead of retaining partial data and continues update attempts. A failed
`auth_zone_reload` likewise stops answers from the unreadable zone.

### File boundaries and destination collisions

Secondary zonefiles may not use `$INCLUDE` (1.26.0). Auth-zone and RPZ loads
discard records outside the zone apex. `unbound-checkconf` detects colliding
destination filenames for auth-zone downloads.

### Transfer bounds and primary endpoints

`max-transfer-size` and `max-transfer-time` bound auth-zone and RPZ transfers
(1.26.0); both are disabled by default. Primary transfer hostnames can resolve
through CNAME chains.

## DNS64 and NAT64

NAT64-synthesized target addresses are attached at the delegation point so
the infra cache can operate correctly (1.24.0).

The `do-nat64` and `do-not-query-address` interaction is applied consistently
during retry processing (1.25.0).

With DNSSEC enabled, the AAAA query used for DNS64 synthesis must validate
successfully (1.26.0). Synthesis preserves `rpz-passthru` decisions and keeps
ECS-scoped answers out of the global cache.

## Forward and stub zones

Hostnames used instead of IP addresses for stub- or forward-zone name servers
can create a circular resolution dependency (1.24.0). Unbound detects this and
logs a warning.

Forwarder checks consider configured auth zones (1.23.0).

## EDNS Client Subnet resolution failures

Failure to create an ECS subquery yields `SERVFAIL`, not `FORMERR` (1.24.0).
For `0.0.0.0/0`, untreated data uses the global cache, while configured subnet
treatment uses the subnet cache.

## RESINFO

RESINFO RR type 261 is supported with `LDNS_RR_TYPE_RESINFO` and a TXT-like
representation (1.23.0).
