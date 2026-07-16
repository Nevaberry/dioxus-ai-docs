# Clients, Authentication, and Command-Line Tools

Batch attribution: `17.0`, `18.0`.

## Migrate password authentication and configure OAuth

MD5 password authentication is deprecated. `CREATE ROLE` and `ALTER ROLE` warn
when setting an MD5 password unless `md5_password_warnings` is disabled.

`oauth` is a `pg_hba.conf` authentication method. The server loads token
validation libraries named by `oauth_validator_libraries`, while libpq provides
the corresponding OAuth connection options. Building OAuth support from source
requires `--with-libcurl`.

## Configure TLS negotiation

`sslnegotiation=direct` makes libpq begin TLS immediately, avoiding the usual
negotiation round trip. It requires ALPN and a PostgreSQL 17-or-newer server.

```text
host=db.example dbname=app sslmode=require sslnegotiation=direct
```

Server TLS settings include `ssl_tls13_ciphers`. The multi-valued `ssl_groups`
replaces `ssl_ecdh_curve`, although the old name remains accepted; the default
group list includes X25519.

Later security updates make libpq discard unauthenticated server error text
received before SSL or GSS negotiation. Its escaping functions also validate
input encoding, so applications and intermediaries must agree on that encoding.

## Cancel, stream, and pipeline libpq operations

The current cancel API can operate in blocking or nonblocking mode and reuses
the existing encrypted connection. It replaces the old cancellation behavior,
which was blocking and could not preserve encrypted transport.

`PQsetChunkedRowsMode()` returns query results in chunks.
`PQsendPipelineSync()` queues a pipeline synchronization point without
necessarily flushing immediately. `PQchangePassword()` hashes a new role
password before sending it.

## Negotiate protocol versions

Wire protocol 3.2 supports 256-bit cancel keys. `PQfullProtocolVersion()`
reports the negotiated protocol, and libpq connection parameters and
environment variables can bound acceptable protocol versions.

Clients are notified when `search_path` changes. `PQtrace()` traces
authentication and every other protocol message. `sslkeylogfile` exports TLS
key material for debugging. Updated public signatures use `int64_t` instead of
the deprecated `pg_int64` type.

## Use prepared statements and pipeline mode in psql

psql supplies `\parse`, `\bind_named`, and `\close_prepared` for named prepared
statements.

Pipeline control uses `\startpipeline`, `\syncpipeline`, `\sendpipeline`,
`\endpipeline`, `\flushrequest`, `\flush`, and `\getresults`. The `%P` prompt
escape and `PIPELINE_*_COUNT` variables expose pipeline state.

## Control psql display, fetching, and watch behavior

`\watch` supports a `min_rows` stopping condition, and `WATCH_INTERVAL` sets
its default delay. Connection attempts can be canceled with Control-C.
`FETCH_COUNT` applies to row-returning statements even when they are not
`SELECT`.

Backslash-command output honors `\pset null`. `\dp` displays `(none)` for
explicitly empty privileges while leaving default privileges blank.

Appending `x` to a list command requests expanded output. `\conninfo` uses a
richer tabular display. Function and operator descriptions show leakproof
status, partition descriptions show access methods, and `\dx` includes an
extension's default version.

## Run pgbench with compatible option names

`pgbench -d` now selects the database and `--dbname` is its long form. Use
`--debug` instead of the old `-d` debug meaning. `--exit-on-abort` stops a run
after any client aborts, and `\syncpipeline` explicitly sends pipeline
synchronization messages.

## Recover from asynchronous notification failures

If an updated server reports an error while a client consumes an asynchronous
`NOTIFY`, that error is promoted to `FATAL` and the connection closes. Reconnect:
the failure indicates that a notification may have been lost.
