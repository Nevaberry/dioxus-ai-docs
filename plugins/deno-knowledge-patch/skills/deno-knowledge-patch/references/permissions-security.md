# Permissions & Security

## Permission Sets in deno.json (2.5+)

Define named permission sets and reference them with `-P` (or `--permission-set`). A `"default"` set is used when `-P` has no argument.

```jsonc
{
  "permissions": {
    "default": { "read": ["./data"], "env": true },
    "dev": { "read": true, "write": true, "net": true }
  },
  "tasks": { "start": "deno run -P main.ts" }
}
```
```bash
deno run -P=dev main.ts # uses "dev" set
deno run -P main.ts     # uses "default" set
```

Permissions can also be set under `"test"`, `"bench"`, or `"compile"` keys — requires `-P` flag when running.

## `--ignore-read` and `--ignore-env` (2.6+)

Instead of throwing `NotCapable`, return `NotFound`/`undefined` for denied paths/env vars. Useful for deps that handle missing values gracefully but not permission errors.

```bash
deno run --ignore-read=/etc --ignore-env=AWS_SECRET_KEY main.ts
```

`Deno.env.toObject()` now works with partial permissions — returns only allowed vars.

## Permission Broker (2.6+, experimental)

External process mediates all permission requests. When active, all `--allow-*`/`--deny-*`/`--ignore-*` flags are ignored.

```bash
DENO_PERMISSION_BROKER_PATH=/perm_broker.sock deno run untrusted_code.ts
```

## Permission Enhancements (2.4+)

`--allow-net` supports subdomain wildcards and CIDR ranges:

```bash
--allow-net=*.foo.localhost
--allow-net=192.168.0.128/25
```

New `--deny-import` flag blocks specific import hosts.

## DENO_AUDIT_PERMISSIONS (2.5+)

Set `DENO_AUDIT_PERMISSIONS=./audit.log` to write a JSONL log of all permission checks. Combine with `DENO_TRACE_PERMISSIONS=1` to include stack traces.

## Permissions No Longer Required

- `Deno.cwd()` no longer needs `--allow-read` (2.2+)
- `Deno.execPath()` no longer needs `--allow-read` (2.4+)
