# Databases and PDO

## General database migrations

### Database API deprecations (8.4-migration)

`mysqli_ping()`/`mysqli::ping()`, MySQLi kill and refresh APIs, explicit
`mysqli_store_result()` mode, and associated compatibility constants are
deprecated. Issue SQL `KILL` or `FLUSH` when those operations are needed.
`mysqli_execute()` is also deprecated; use `mysqli_stmt_execute()`.

Use the three-argument forms of `pg_fetch_result()`, `pg_field_prtlen()`, and
`pg_field_is_null()` with `row: null` instead of their two-argument forms. In
dollar-quoted PDO_PGSQL SQL, stop escaping question marks as `??`.

### Connections migrated from resources (8.4-migration)

DBA connections are `Dba\Connection` objects. ODBC connections and results are
`Odbc\Connection` and `Odbc\Result`. Replace `is_resource()` return checks with
explicit failure checks such as `=== false`.

### MySQL timeout error codes (8.4-migration)

With MySQL server 8.0.24 or newer, mysqlnd reports server wait timeouts as error
`4031` rather than `2006`. Retry and disconnect detection must recognize the
new code.

## PDO compatibility

### Attribute types, credentials, and build requirements (8.4-migration)

PDO_DBLIB unique-identifier/date-time attributes, PDO_FIREBIRD autocommit, and
PDO_MYSQL autocommit/emulated-prepare/direct-query attributes accept and return
booleans rather than integers. PDO_PGSQL credentials embedded in a DSN override
constructor credentials. Building PDO_FIREBIRD requires a C++ compiler and
fbclient 3.0 or newer.

### Driver-specific connection classes (8.4.0)

PDO drivers may expose driver-specific subclasses. Obtain one through
`PDO::connect()` or construct the appropriate subclass directly when code needs
driver-specific functionality represented by the connection's concrete type.

### Driver-aware SQL parsing (8.4.0)

PDO may use driver-specific parsers. The MySQL parser recognizes backtick
identifiers and hash comments; SQLite recognizes backtick literals and
square-bracket identifiers. Their contents are therefore not mistaken for
placeholders or other SQL syntax.

### DSNs, constants, and driver methods (8.5-migration)

The remote `uri:` PDO DSN scheme is deprecated for security reasons. Move
driver-specific constants from `PDO` to `Pdo\Dblib`, `Pdo\Firebird`,
`Pdo\Mysql`, `Pdo\Odbc`, `Pdo\Pgsql`, or `Pdo\Sqlite`. Move prefixed
PostgreSQL and SQLite methods on `PDO` to same-purpose driver-subclass methods.
The unusable `PDO::PGSQL_TRANSACTION_*` constants are deprecated.

### Fetch semantics (8.5-migration)

`PDO::FETCH_CLASS` constructor arguments follow normal
`call_user_func_array()` rules: string keys become named arguments and
by-reference parameters need references in the argument array. Changing fetch
mode during a fetch throws. Do not hard-code changed fetch-flag integer values;
combine `FETCH_PROPS_LATE` only with `FETCH_CLASS`, and do not use `FETCH_INTO`
with `fetchAll()`.

### SQLite transaction mode (8.5.0)

`Pdo\Sqlite::ATTR_TRANSACTION_MODE` selects deferred, immediate, or exclusive
behavior for subsequent `beginTransaction()` calls.

```php
$pdo->setAttribute(
    Pdo\Sqlite::ATTR_TRANSACTION_MODE,
    Pdo\Sqlite::TRANSACTION_MODE_IMMEDIATE,
);
$pdo->beginTransaction();
```

## Driver-specific failures

### Stricter database edge cases (8.5-migration)

Re-running the MySQLi constructor on an initialized object throws. Firebird
rejects overlong cursor names. SQLite PDO rejects NUL bytes in quoted strings
and throws when a collation callback returns the wrong type.
