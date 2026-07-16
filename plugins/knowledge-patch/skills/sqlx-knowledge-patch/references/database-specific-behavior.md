# Database-Specific Behavior

## PostgreSQL network types

Since `0.8.0`, the `ipnet` feature maps PostgreSQL `INET` and `CIDR` values using types from the `ipnet` crate. This is an alternative to the existing `ipnetwork` integration.

```toml
[dependencies]
sqlx = { version = "0.8", features = [
  "runtime-tokio",
  "postgres",
  "ipnet",
] }
```

Choose the integration that matches the network-address types used by the application.

## PostgreSQL option escaping

`PgConnectOptions::options()` now escapes option values. Pass unescaped values and remove application-side escaping left over from earlier SQLx versions. Keeping both layers can double escape the option.

## PostgreSQL passfile passwords

SQLx now decodes password backslash escapes in `.pgpass`. An existing passfile containing backslashes can therefore result in a different password being sent after an upgrade. Inspect the passfile's escaped form when authentication changes unexpectedly.

## MySQL RSA authentication

For a plaintext MySQL connection that requires RSA password encryption, enable `mysql-rsa`:

```toml
[dependencies]
sqlx = { version = "0.9", features = [
  "runtime-smol",
  "mysql",
  "mysql-rsa",
] }
```

Without that feature, the authentication path fails. A TLS connection does not use this RSA plaintext-connection path.

## MySQL text inference

Non-binary text-like columns that were previously inferred as `Vec<u8>` may now be inferred as `String`. Recompile checked queries and update intentional byte-oriented handling where the database column is actually textual.

## MySQL character sets and collations

SQLx sends `SET NAMES utf8mb4` without forcing a collation.

Calling either of these connection-option methods automatically enables `set_names`:

- `MySqlConnectOptions::charset()`
- `MySqlConnectOptions::collation()`

Account for the automatically enabled statement when connection initialization or server policy is sensitive to `SET NAMES`.

## SQLite extension loading

SQLite extension loading is unsafe in SQLx 0.9, whether invoked through the API or configured through `sqlx.toml`. The capability is gated by `sqlite-load-extension`.

Treat extension identity and path as trusted inputs and keep the unsafe boundary explicit.

## SQLite value thread safety

The SQLite value types intentionally impose these restrictions:

| Type | Restriction | Consequence |
| --- | --- | --- |
| `SqliteValue` | `!Sync` | A shared reference cannot safely cross threads. |
| `SqliteValueRef` | `!Send` | The borrowed value reference cannot move to another thread. |

Clone, own, or mutex-wrap suitable owned state before crossing the relevant boundary. Do not work around the marker traits with an unsafe assertion.

## SQLite repeated borrowed decoding

After decoding a SQLite value as borrowed `&[u8]` or `&str`, trying to decode the same value as another type now produces an error. Decode once into the required representation, or create an owned copy before applying a separate conversion.

## SQLite library compatibility

The maximum compatible version of `libsqlite3-sys` may be raised in a non-breaking SQLx release. Dependency resolution that selects a newer compatible binding version is therefore not, by itself, evidence of a breaking SQLx release.
