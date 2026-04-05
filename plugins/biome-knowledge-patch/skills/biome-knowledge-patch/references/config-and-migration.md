# Configuration & Migration (v2.0–v2.4)

## `files.includes` Replaces `files.ignore` and `files.include`

Breaking change in v2.0. Both fields merged into a single `files.includes` array.

```json
{
  "files": {
    "includes": [
      "**",
      "!**/generated",
      "!!**/dist"
    ]
  }
}
```

Key behavior changes from v1:
- Globs no longer auto-prepend `**/` — you must write full patterns
- `*` no longer matches `/`
- Globs are relative to config file location, not working directory

### Ignore Prefixes (v2.3)

- `!` — skip formatting/linting but still index for types
- `!!` — completely exclude from all Biome operations

## Monorepo Nested Configs

Nested `biome.json` files in subdirectories are supported. They must be marked as non-root:

```json
{ "root": false }
```

Or extend from root with shorthand:

```json
{ "extends": "//" }
```

**Important:** Nested configs do NOT inherit from root by default — use `extends` explicitly.

## Config File Discovery (v2.4)

Hidden config files are now supported:
- `.biome.json` / `.biome.jsonc` (loaded after `biome.json`/`biome.jsonc`)

Config home directory:
- Linux: `$XDG_CONFIG_HOME/biome` or `~/.config/biome`
- macOS: `~/Library/Application Support/biome`

Priority order: project folder → parent folders → config home.
