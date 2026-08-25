# Database, Sessions, and Persistence

## MySQLi operations and timeout handling

### Deprecated administrative APIs

Source batch: `8.4-migration`.

`mysqli_ping()` / `mysqli::ping()`, the MySQLi kill and refresh APIs, explicit
`mysqli_store_result()` mode, and their associated compatibility constants are
deprecated. Issue SQL `KILL` or `FLUSH` when those operations are needed.

`mysqli_execute()` is deprecated; use `mysqli_stmt_execute()` (source batch
`8.5-migration`).

### Timeout error codes

With MySQL server 8.0.24 or newer, mysqlnd reports server wait timeouts as error
`4031` rather than `2006`. Retry and disconnect detection must recognize the
new code (source batch `8.4-migration`).

### Constructor failure

Re-running the MySQLi constructor on an initialized object now throws (source
batch `8.5-migration`).

## PostgreSQL API and SQL parsing

Source batch: `8.4-migration`.

The two-argument forms of `pg_fetch_result()`, `pg_field_prtlen()`, and
`pg_field_is_null()` should use the three-argument form with `row: null`.

In dollar-quoted PDO_PGSQL SQL, stop escaping question marks as `??`.

PDO_PGSQL credentials embedded in the DSN now override credentials supplied to
the constructor.

## PDO drivers, DSNs, and members

### Driver-specific connections

Source batch: `8.4.0`.

PDO drivers may expose driver-specific subclasses. Obtain them through
`PDO::connect()` or by directly constructing the corresponding subclass. The
connection's concrete type can represent database-specific functionality.

### Driver-aware SQL parsing

Source batch: `8.4.0`.

PDO may use driver-specific SQL parsers instead of only its generic parser. The
MySQL parser recognizes backtick identifiers and hash comments. The SQLite
parser recognizes backtick literals and square-bracket identifiers. Their
contents are therefore not mistaken for SQL syntax such as placeholders.

### Attribute types and connection requirements

Source batch: `8.4-migration`.

The following PDO attributes accept and return booleans rather than integers:

- PDO_DBLIB unique-identifier and date-time attributes.
- PDO_FIREBIRD autocommit.
- PDO_MYSQL autocommit, emulated-prepare, and direct-query attributes.

Building PDO_FIREBIRD requires a C++ compiler and fbclient 3.0 or newer.

### Deprecated DSNs, constants, and prefixed methods

Source batch: `8.5-migration`.

The remote `uri:` PDO DSN scheme is deprecated for security reasons.

Move driver-specific constants on `PDO` to `Pdo\Dblib`, `Pdo\Firebird`,
`Pdo\Mysql`, `Pdo\Odbc`, `Pdo\Pgsql`, or `Pdo\Sqlite`. Move the prefixed
PostgreSQL and SQLite methods on `PDO` to the same-purpose methods on their
driver subclasses. The unusable `PDO::PGSQL_TRANSACTION_*` constants are also
deprecated.

### Fetch semantics

Source batch: `8.5-migration`.

`PDO::FETCH_CLASS` constructor arguments use normal `call_user_func_array()`
semantics. String keys are named arguments, and by-reference parameters require
references in the argument array.

Changing fetch mode during a fetch now throws. Do not hard-code the changed
fetch-flag integer values. Combine `FETCH_PROPS_LATE` only with `FETCH_CLASS`,
and do not use `FETCH_INTO` with `fetchAll()`.

## SQLite and Firebird behavior

Source batch: `8.5-migration`.

Firebird rejects overlong cursor names. SQLite PDO rejects NUL bytes in quoted
strings and throws when a collation callback returns the wrong type.

### Configurable SQLite transactions

Source batch: `8.5.0`.

`Pdo\Sqlite::ATTR_TRANSACTION_MODE` selects deferred, immediate, or exclusive
behavior for subsequent `beginTransaction()` calls.

```php
$pdo->setAttribute(
    Pdo\Sqlite::ATTR_TRANSACTION_MODE,
    Pdo\Sqlite::TRANSACTION_MODE_IMMEDIATE,
);
$pdo->beginTransaction();
```

## DBA and ODBC handles

Source batch: `8.4-migration`.

DBA connections are `Dba\Connection` objects. ODBC connections and results are
`Odbc\Connection` and `Odbc\Result`. Replace `is_resource()` return checks with
explicit failure checks such as `=== false`.

`odbc_fetch_row()` warns and returns `false` when its row number is zero or
negative.

Passing `null` or `false` to `dba_key_split()` is deprecated. Validate the
input instead of relying on the old fallback behavior.

## Session storage and configuration

### Deprecated configuration

Source batch: `8.4-migration`.

Calls to `session_set_save_handler()` with more than two arguments are
deprecated.

Stop changing `session.sid_length` and `session.sid_bits_per_character`, and
make storage accept 32-character hexadecimal IDs. Stop changing these
deprecated cookie and trans-SID settings:

- `session.use_only_cookies`
- `session.use_trans_sid`
- `session.trans_sid_tags`
- `session.trans_sid_hosts`
- `session.referer_check`

`SID` is deprecated as well.

Session configuration emits warnings for a non-positive
`session.gc_divisor` or a negative `session.gc_probability`.

### Session input validation

Source batch: `8.5-migration`.

Serializing `$_SESSION` with a key containing `|` now warns instead of failing
silently. `session_start()` requires its options to be a hashmap and requires
`read_and_close` to have a type compatible with `int`.

## Partitioned cookies

Source batch: `8.5.0`.

`session_set_cookie_params()`, `session_get_cookie_params()`,
`session_start()`, `setcookie()`, and `setrawcookie()` recognize the
`partitioned` cookie option.

```php
setcookie('sid', $value, ['partitioned' => true]);
```

## Security patch releases

Source batch: `8.2.33-8.5.9-security`.

PHP 8.2.33, 8.3.33, 8.4.24, and 8.5.9 are security releases. Deployments on
any of those branches should upgrade to the corresponding patch version.

PHP 8.5.9 specifically fixes the BCMath out-of-bounds write vulnerability
GHSA-x692-q9x7-8c3f / CVE-2026-17544.
