# Security and Policy

## EDNS COOKIE controls

### Persistent secret rollover

`cookie-secret-file` stores COOKIE secrets across restarts (1.21.0):

```conf
server:
    cookie-secret-file: "unbound_cookiesecrets.txt"
```

Use the remote-control commands `add_cookie_secret`,
`activate_cookie_secret`, and `drop_cookie_secret` for runtime rotation, and
`print_cookie_secrets` to inspect the values in use.

### COOKIE-aware IP rate limiting

`ip-ratelimit-cookie` is enforced (1.21.0). An upgrade can activate the
intended COOKIE-client rate limit in configurations that already set the
option, so monitor rejected traffic.

## DNSSEC trust anchors and certificate material

The default root keys in `unbound-anchor` include key 38696 (1.21.0). Inspect
compiled-in material with:

```sh
unbound-anchor -l
```

The built-in `icannbundle.pem` includes ICANN public keys covering 2009–2029
and 2025–2045 (1.26.0). Use `-l` to show built-in material or `-c` to select an
external bundle that can be updated independently:

```sh
unbound-anchor -c /etc/unbound/icannbundle.pem
```

## DNSSEC validation tightening

### Alias chains

YXDOMAIN is accepted only with a DNAME, signatures from revoked DNSKEYs are
rejected, and DNAME-to-CNAME and wildcard-CNAME chains have stricter trust
checks (1.25.0).

### Proof and RSA-key handling

Libnettle builds validate noncanonical RSA DNSKEYs whose modulus has leading
zeroes and compute their size correctly (1.26.0). Negative caching works with
unsalted NSEC3 records. Signed wildcard NSEC records are checked before use as
DS proofs. Aggressive NSEC/NSEC3 processing rejects signer-zone mismatches,
overreaching next-owner names, and results outside the trust-anchor bailiwick.

## Iterator and query hardening

### RRSIG scrub bound

`iter-scrub-rrsig` caps RRSIGs retained by the iterator scrubber and defaults
to `8` (1.25.0):

```conf
server:
    iter-scrub-rrsig: 8
```

### Missing glue

`harden-unverified-glue` includes missing AAAA lookups initiated by cache fill
(1.22.0).

### Malformed errors and EOF

Malformed cases receive error replies rather than silence and do not reflect
parts of the query (1.25.0). CHAOS queries do not echo incoming EDNS extended
RCODEs. TCP client EOF cancels pending replies and closes the connection.

## Response and local-zone policy

### SVCB/HTTPS rebinding protection

`private-address` filtering removes matching SVCB and HTTPS records as well as
address records (1.25.0), closing a rebinding route that did not require A or
AAAA data.

### Refused DS queries

An `always_refuse` local zone blocks DS queries along with other types
(1.25.0).

### Tagged RPZ matching

Tags on tagged RPZ zones are honored (1.21.0). This corrects the regression in
which tags were ignored after moving from 1.19.3 to 1.20.0.

### ZONEMD in RPZ data

ZONEMD records are ignored as a policy type while loading RPZ zones (1.25.0),
so their presence does not break root-key priming.

## DNS64 and NAT64 validation policy

When DNSSEC is enabled, the AAAA query behind a DNS64 answer must validate
successfully (1.26.0). DNS64 synthesis preserves `rpz-passthru` decisions and
keeps ECS-scoped answers out of the global cache.

The interaction between `do-nat64` and `do-not-query-address` is applied
consistently during retries (1.25.0).

## External cachedb trust

Expired bogus cachedb data is not returned as non-bogus, and cached
aggressive-negative replies carry RA (1.25.0). `forward-no-cache` and
`stub-no-cache` prevent external cachedb reads and writes, including relevant
ECS paths.
