# Clients, Authentication, and Command-Line Tools

Use this reference for connection security, libpq and protocol compatibility,
interactive psql workflows, pgbench, and failure handling. Version-dependent
items below retain the full `17.0` and `18.0` batch attribution.

## Authentication and TLS

### Move away from MD5 authentication

MD5 password authentication is deprecated in PostgreSQL 18. Setting an MD5
password with `CREATE ROLE` or `ALTER ROLE` warns unless
`md5_password_warnings` is disabled. Migrate both stored passwords and
`pg_hba.conf` rules instead of suppressing the warning indefinitely.

PostgreSQL 18 accepts `oauth` as a `pg_hba.conf` method. Server token
validation is provided by libraries listed in `oauth_validator_libraries`, and
libpq has matching OAuth connection options. A source build with OAuth support
requires `--with-libcurl`.

TLS configuration adds `ssl_tls13_ciphers`. The former `ssl_ecdh_curve` name
still works, but `ssl_groups` is the multi-valued replacement and defaults to
a set that includes X25519.

### Negotiate TLS directly

Since PostgreSQL 17, `sslnegotiation=direct` starts TLS immediately and avoids
the usual negotiation round trip:

```text
host=db.example dbname=app sslmode=require sslnegotiation=direct
```

Direct negotiation requires ALPN and a PostgreSQL 17-or-newer server. Later
17.x libpq releases also discard unauthenticated server error text received
before SSL or GSS negotiation.

### Treat encoding and TLS debug output as sensitive

Updated 17.x libpq escaping functions validate the input encoding, so the
application and intermediary must agree on that encoding. PostgreSQL 18 adds
`sslkeylogfile` for exporting TLS key material during debugging; protect that
file because it can make captured traffic decryptable.

## libpq and wire protocol

### Use the current cancellation and result APIs

PostgreSQL 17's replacement cancel API supports blocking and nonblocking
cancellation while reusing the encrypted connection. This avoids the old
blocking, unencrypted-only cancellation behavior.

Other PostgreSQL 17 additions are:

- `PQsetChunkedRowsMode()` to return results in chunks.
- `PQsendPipelineSync()` to queue a pipeline synchronization point without
  necessarily flushing immediately.
- `PQchangePassword()` to hash a new role password before sending it.

### Bound protocol compatibility deliberately

Wire protocol 3.2 in PostgreSQL 18 supports 256-bit cancel keys. Use
`PQfullProtocolVersion()` and the new connection parameters or environment
variables to bound acceptable protocol versions when compatibility matters.

Clients are notified when `search_path` changes, and `PQtrace()` can trace
authentication and every other protocol message. Public APIs affected by the
type cleanup use `int64_t` rather than deprecated `pg_int64`.

## psql prepared statements and pipelines

PostgreSQL 18 psql adds `\parse`, `\bind_named`, and `\close_prepared` for
named prepared statements. Its explicit pipeline commands are
`\startpipeline`, `\syncpipeline`, `\sendpipeline`, `\endpipeline`,
`\flushrequest`, `\flush`, and `\getresults`. `%P` and the
`PIPELINE_*_COUNT` variables expose pipeline state.

PostgreSQL 17 also added `\syncpipeline`, which explicitly sends a pipeline
synchronization message from a pgbench script.

## psql display, watch, and connection behavior

PostgreSQL 17 psql behavior includes:

- `\watch` has a `min_rows` stopping condition.
- Control-C can cancel a connection attempt.
- `FETCH_COUNT` applies to row-returning statements beyond `SELECT`.
- Backslash-command output honors `\pset null`.
- `\dp` shows `(none)` for explicitly empty privileges while leaving default
  privileges blank.

PostgreSQL 18 adds `WATCH_INTERVAL` as the default `\watch` delay. Appending
`x` to list commands requests expanded output, `\conninfo` uses a richer
tabular display, function/operator descriptions show leakproof status,
partition descriptions show access methods, and `\dx` shows each extension's
default version.

## pgbench compatibility

The old PostgreSQL 17 `pgbench -d` debug spelling became `--debug`; `-d` now
selects the database and `--dbname` is its long spelling. `--exit-on-abort`
stops the run after any client aborts.

## Client-side failure semantics

### Reconnect after notification-consumption errors

In updated 17.x releases, any error while consuming asynchronous `NOTIFY` is
promoted to `FATAL` and closes the connection. Reconnect because a notification
may have been lost; continuing on the same connection is not possible.

### Respect trusted PL/Perl restrictions

Updated trusted PL/Perl rejects changes to `%ENV`; only `plperlu` retains that
capability.

## Session time-zone parsing

PostgreSQL 18 gives session time-zone abbreviations precedence over entries in
`timezone_abbreviations`. Audit applications that depend on a conflicting
abbreviation definition.
