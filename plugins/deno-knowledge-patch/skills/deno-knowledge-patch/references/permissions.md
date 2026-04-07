# Permissions

## Permission Sets in Config (2.5+)

Define named permission sets in `deno.json` and use with `-P` / `--permission-set`:
```json
{
  "permissions": {
    "default": {
      "read": [
        "./data"
      ],
      "env": true
    },
    "dev": {
      "read": true,
      "write": true,
      "net": true
    }
  },
  "tasks": {
    "dev": "deno run -P=dev main.ts"
  }
}
```
```bash
deno run -P main.ts     # uses "default" set
deno run -P=dev main.ts # uses "dev" set
```
Can also set permissions under `"test"`, `"bench"`, or `"compile"` keys (requires `-P` flag to activate).

## `--ignore-read` and `--ignore-env` (2.6+)

Return `NotFound`/`undefined` instead of `NotCapable` for denied resources — lets deps that gracefully handle missing files/env vars work without granting full access:
```bash
deno run --ignore-read=/etc --ignore-env=AWS_SECRET_KEY main.ts
```
`Deno.env.toObject()` now returns only allowed vars with partial `--allow-env`.

## Permission Enhancements (2.4+)

- `--allow-net` supports subdomain wildcards (`*.foo.localhost`) and CIDR ranges (`192.168.0.128/25`)
- New `--deny-import` flag to block specific import hosts
- `Deno.execPath()` no longer requires read permissions
