# Clients and drivers

Use this reference for JDBC, CLI, protocol spooling, authentication reuse, and
client-visible metadata.

## Runtime and connection validation

The JDBC driver and CLI require Java 11 or newer (470).

`Connection.isValid(int)` validates both the connection and its credentials
(469). The JDBC connection property `validateConnection` is also available;
use it where connection-pool validation must explicitly exercise credentials.

The JDBC driver provides a `javax.sql.DataSource` implementation (472).

## Query statistics

`io.trino.jdbc.QueryStats` exposes these additional measurements (469):

- `planningTimeMillis`
- `analysisTimeMillis`
- `finishingTimeMillis`
- `physicalInputBytes`
- `physicalWrittenBytes`
- `internalNetworkInputBytes`
- `physicalInputTimeMillis`

Event listeners separately receive time spent in the `FINISHING` state (479);
do not infer that value by subtracting unrelated client durations.

## Protocol spooling

Spooling behavior can be selected with session properties (469). The JDBC
driver and CLI support spooling when the cluster uses a private certificate
chain (469), provided the client trust configuration recognizes that chain.

The spooling protocol can serialize connector-provided custom types (482).
This removes the earlier custom-type limitation, but client code must still be
able to interpret the returned type.

## Authentication token reuse and refresh

JDBC external-authentication tokens can be persisted under `~/.trino/` and
reused by separate client processes (481):

```properties
externalAuthenticationTokenCache=SYSTEM
```

JDBC connections using `accessToken` transparently refresh OAuth2 tokens when
the server enables refresh tokens (481):

```properties
http-server.authentication.oauth2.refresh-tokens=true
```

The first setting controls cross-process token caching. The second depends on
server-side refresh-token support; they solve different lifecycle problems.

## Request headers

Send arbitrary client HTTP headers with the JDBC `extraHeaders` connection
option or the CLI `--extra-header` flag (479). Treat header values as
credentials when they carry authentication or authorization material, and
avoid placing them in logs or shell history.

## Prepared values and statement parameters

`PreparedStatement.setBigDecimal()` accepts scientific-notation string forms,
including `0E-10` (481).

Parameters are supported in table `VERSION AS OF` and `TIMESTAMP AS OF`
clauses (480), and in `WITH SESSION`, `SET SESSION`, and `CALL` statements
(481):

```sql
SELECT * FROM iceberg.sales.orders FOR VERSION AS OF ?;
SET SESSION query_max_execution_time = ?;
```

## Result metadata and types

`ResultSetMetaData.getColumnClassName()` returns the correct Java class name
for `map`, `row`, `time with time zone`, `timestamp with time zone`,
`varbinary`, and null values (480).

The JDBC driver and CLI support `variant` values (481). Older CLI releases
render variant values as JSON, so scripts should not assume identical display
format across client versions.

`number` interoperates with `json`, boolean casts, and Python UDFs as described
in the SQL reference. JDBC metadata users should avoid assuming every numeric
value fits `DECIMAL(38, s)`.

