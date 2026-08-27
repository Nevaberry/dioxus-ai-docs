# Policy and auth zones

## Local-zone policy

### COOKIE-aware IP rate limiting

`ip-ratelimit-cookie` is enforced as configured (since 1.21.0). An upgrade can
therefore activate a COOKIE-client rate limit that was present but previously
not applied.

### Dynamic always_nxdomain zones

`always_nxdomain` zones added with `unbound-control` locate their parent
correctly (since 1.21.0), restoring reliable dynamic blocking.

### Default local zones

`resolver.arpa` and `service.arpa` are served locally by default (since
1.23.0). An upgrade may therefore stop those names from reaching forwarders.

### DS in always_refuse

An `always_refuse` local zone rejects DS queries as well as other types (since
1.25.0).

### Ineffective nodefault warnings

`unbound-checkconf` warns when a `nodefault` local-zone declaration has no
effect (since 1.25.0).

### Address-family blocking

`block_aaaa` suppresses AAAA as `block_a` suppresses A (since 1.26.0).
`block_a_wdata` and `block_aaaa_wdata` can serve matching `local-data`, recurse
for other data, and deny the selected address family.

## RPZ and response policy

### Tagged RPZ matching

Tags on tagged RPZ zones are honored (since 1.21.0), correcting the regression
that ignored them after upgrading from 1.19.3 to 1.20.0.

### RPZ local-CNAME chains

Resolution follows a CNAME chain introduced by an RPZ local-CNAME rewrite
(since 1.24.0), rather than stopping at the rewritten alias.

### RESPIP and RPZ with DNS64

RESPIP and RPZ apply to DNS64-synthesized answers with module order
`"respip dns64 validator iterator"` (since 1.24.0). Adding cachedb as
`"respip dns64 validator cachedb iterator"` is not known to work.

### ZONEMD in RPZ data

RPZ loading ignores ZONEMD as a policy type (since 1.25.0), preventing a
ZONEMD-bearing zone from breaking root-key priming.

## Auth zones and forwarding

### Forwarder checks

Forwarder checks account for configured auth zones (since 1.23.0).

### Auth-zone status

Auth-zone status reporting is available (since 1.24.0). The acquired
timestamp is set only after the zonefile is read.

### HTTP-downloaded origins

Auth-zone files downloaded over HTTP may use an empty-label `$ORIGIN` (since
1.24.0).

### Hostname dependency warnings

Nameserver hostnames in stub or forward zones can create circular resolution
dependencies; Unbound detects and warns about the configuration (since
1.24.0).

### Hostnames in allow-notify

Hostname-valued `allow-notify` entries retain resolved IPv4 and IPv6 addresses
and are resolved even when an auth-zone has only URL transfer sources (since
1.25.0).

### Load failure isolation

The daemon stays up when a secondary cannot load or a zonefile-only primary is
missing its file (since 1.26.0). A failed secondary load clears the zone and
continues update attempts. Failed `auth_zone_reload` likewise stops answers
from the unreadable zone rather than retaining partial data.

### Zonefile boundaries and collisions

Secondary zonefiles cannot use `$INCLUDE` (since 1.26.0). Auth-zone and RPZ
loads discard records outside the apex, and `unbound-checkconf` detects
download destinations whose filenames collide.

### Transfer limits and endpoints

`max-transfer-size` and `max-transfer-time` bound auth-zone and RPZ transfers
(since 1.26.0); both default to disabled. Primary hostnames can resolve through
CNAME chains. Configured `allow-notify` addresses and netblocks are available
from server startup.

## Record-type support

### RESINFO

Unbound supports RESINFO RR type 261 (since 1.23.0), exposed as
`LDNS_RR_TYPE_RESINFO` with a TXT-like representation.
