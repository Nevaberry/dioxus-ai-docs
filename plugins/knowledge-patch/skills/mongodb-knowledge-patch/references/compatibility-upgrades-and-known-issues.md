# Compatibility, upgrades, and known issues

## Linux kernel 6.19 incompatibility

MongoDB 8.0 and newer can crash at startup on Linux kernel 6.19 because of the bundled TCMalloc
version. The incompatibility applies to official packages, package-manager installations, and
containers. Avoid the combination until using a MongoDB build whose allocator contains the fix.

Do not assume a container insulates `mongod` from this issue: the container uses the host kernel.

## Upgrade prerequisites

Before upgrading an 8.0 deployment to 8.2, verify that its feature compatibility version is
`8.0`:

```javascript
db.adminCommand({ getParameter: 1, featureCompatibilityVersion: 1 })
```

Do not begin the binary upgrade until the returned FCV is correct.

## Downgrade constraints

- The supported downgrade path from 8.2 is a single-version downgrade to 8.0.
- Community Edition does not support binary downgrades.
- FCV cannot be downgraded to or from a minor release.
- For Enterprise Edition, changing FCV before a binary downgrade makes support assistance
  necessary.

Plan rollback around these constraints; a binary swap alone is not a valid generic rollback
procedure.

## Patch-level known issues

### `mongocryptd` 8.2.0 on Windows

The 8.2.0 process does not start with `--logpath NUL`. The .NET/C# driver's default
`mongocryptd` launch uses that path and is affected as well. Choose one of these workarounds:

- set a non-NUL log path;
- use the Automatic Encryption Shared Library instead of `mongocryptd`; or
- run 8.2.1 or newer.

### `mongocryptd` 8.2.4 and 8.2.5 message size

These releases limit `mongocryptd` messages to 16 KiB. Skip both releases or use the Automatic
Encryption Shared Library for encrypted commands that can exceed the limit.

### 8.2.0 spilling crash

MongoDB 8.2.0 can crash when more than 1000 memory-intensive queries are actively spilling.
Increasing `spillWiredTigerSessionMax` is the documented mitigation.

### Trim character-set limit

Starting in 8.2.8, the `chars` string passed to `$trim`, `$ltrim`, or `$rtrim` is limited to
4096 characters. Applications that construct the value dynamically should validate its length.
