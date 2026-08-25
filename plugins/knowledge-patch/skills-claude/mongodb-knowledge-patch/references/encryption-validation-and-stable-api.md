# Encryption, validation, and Stable API

## Queryable Encryption string-query preview

MongoDB 8.2 can enable prefix, suffix, and substring queries on encrypted string fields. This is
public preview functionality with three hard constraints:

- do not use it in production;
- its data is incompatible with the future GA design; and
- collections that enable it will have to be dropped.

Treat every collection used for the preview as disposable test data.

Using this feature from `mongosh` also requires the Automatic Encryption Shared Library 8.2 or
newer, supplied through `--cryptSharedLibPath`.

## `mongocryptd` maintenance-release hazards

On Windows, `mongocryptd` 8.2.0 does not start with `--logpath NUL`. This affects the .NET/C#
driver's default launch as well. Use a non-NUL log path, use the Automatic Encryption Shared
Library, or upgrade to 8.2.1 or newer.

Versions 8.2.4 and 8.2.5 limit `mongocryptd` messages to 16 KiB. Skip these versions or use the
shared library when larger encrypted commands are possible.

## Lookups across encrypted collections

From 8.1, a single `$lookup` stage can reference multiple encrypted collections under either
Client-Side Field Level Encryption or Queryable Encryption. Encryption-aware pipeline planning
no longer needs to assume one encrypted collection per lookup stage.

## Reject-and-log schema validation

The 8.1 validation action `errorAndLog` both rejects an invalid insert or update and records the
violation in the `mongod` log. For a collection that already has a validator:

```javascript
db.runCommand({
  collMod: "orders",
  validationAction: "errorAndLog"
})
```

This differs from warning-only validation because the write does not succeed.

## Validation inspection

From 8.1, `validate` includes index specifications in `indexDetails`. In 8.2, its `repairMode`
field describes attempted inconsistency repairs. Consumers should tolerate and preserve both
fields.

## Stable API V1

MongoDB 8.1 added both the `renameCollection` command and the
`db.collection.renameCollection()` helper to Stable API V1. Stable-API clients may use the
operation without treating it as outside API V1.

## Connection identity inspection

`connectionStatus.authInfo.UUID` identifies the current client connection. Use it when an
authorization-status report must be correlated with connection-level diagnostics.
