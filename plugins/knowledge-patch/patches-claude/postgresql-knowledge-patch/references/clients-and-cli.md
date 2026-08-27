# Clients, Authentication, and Command-Line Tools

## Cancel safely and stream chunked results (17.0)

The current libpq cancellation API supports blocking or nonblocking operation
and can reuse an existing encrypted connection, replacing the old
blocking, unencrypted-only behavior. `PQsetChunkedRowsMode()` returns results
in chunks. `PQsendPipelineSync()` queues a synchronization point without
necessarily flushing it immediately, and `PQchangePassword()` hashes a new
role password before sending it.

## Negotiate TLS directly (17.0)

`sslnegotiation=direct` begins TLS immediately and saves a negotiation round
trip. Use it only with ALPN and a PostgreSQL 17-or-newer server.

```text
host=db.example dbname=app sslmode=require sslnegotiation=direct
```

## Account for psql behavior changes (17.0)

`\watch` has a `min_rows` stopping condition, and Control-C can cancel a
connection attempt. `FETCH_COUNT` applies to row-returning statements beyond
`SELECT`. Backslash-command output honors `\pset null`; `\dp` prints `(none)`
for explicitly empty privileges but leaves default privileges blank.

## Update pgbench invocations (17.0)

The former `pgbench -d` debug option is now `--debug`. `-d` selects the
database, with `--dbname` as its long spelling. `--exit-on-abort` ends a run
after any client aborts, and `\syncpipeline` sends pipeline synchronization
messages explicitly.

## Harden patched clients (17.0)

Later 17.x clients discard unauthenticated server error text received before
SSL or GSS negotiation. Libpq escaping functions validate input encoding, so
applications and intermediaries must agree on that encoding. Trusted PL/Perl
rejects `%ENV` changes; `plperlu` retains that ability.

## Reconnect after notification-consumption failure (17.0)

In updated 17.x releases, an error while consuming asynchronous `NOTIFY` is
always promoted to `FATAL` and closes the connection. Reconnect because the
failure means a notification may have been lost.

## Migrate authentication and time-zone assumptions (18.0)

MD5 password authentication is deprecated. `CREATE ROLE` or `ALTER ROLE`
warns when setting an MD5 password unless `md5_password_warnings` is disabled.
Session time-zone abbreviations take precedence over entries from
`timezone_abbreviations`.

## Configure OAuth and TLS groups (18.0)

`oauth` is a `pg_hba.conf` authentication method. Server token validation uses
libraries listed in `oauth_validator_libraries`; libpq has OAuth connection
options, and source builds need `--with-libcurl`. TLS configuration adds
`ssl_tls13_ciphers`. The multi-valued `ssl_groups` replaces `ssl_ecdh_curve`
(the old name still works), and its default includes X25519.

## Bound wire-protocol negotiation (18.0)

Wire protocol 3.2 provides 256-bit cancel keys. `PQfullProtocolVersion()` and
new connection parameters and environment variables report and bound accepted
protocol versions. Clients receive notifications when `search_path` changes,
and `PQtrace()` covers authentication and every other message.
`sslkeylogfile` exports TLS key material for debugging. Affected public APIs
use `int64_t` instead of deprecated `pg_int64`.

## Drive prepared statements and pipelines in psql (18.0)

Use `\parse`, `\bind_named`, and `\close_prepared` for named prepared
statements. Pipeline mode adds `\startpipeline`, `\syncpipeline`,
`\sendpipeline`, `\endpipeline`, `\flushrequest`, `\flush`, and
`\getresults`; `%P` and the `PIPELINE_*_COUNT` variables expose its state.

## Use richer psql display controls (18.0)

Append `x` to list commands for expanded output. `\conninfo` uses a richer
tabular display, and `WATCH_INTERVAL` sets the default `\watch` delay.
Function and operator descriptions show leakproof status, partition
descriptions show access methods, and `\dx` includes an extension's default
version.
