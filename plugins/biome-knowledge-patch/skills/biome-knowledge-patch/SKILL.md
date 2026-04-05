---
name: biome-knowledge-patch
description: "Biome v2.0-2.4 changes since training cutoff — linter domains, includes replacing ignore/include, assists, GritQL plugins, type-aware linting, Vue/Svelte/Astro full support, embedded snippets. Load before writing Biome config or rules."
license: MIT
metadata:
  author: Nevaberry
  version: "2.4.0"
---

# Biome v2.0–v2.4 Knowledge Patch

You know Biome through v1.6.x: basic lint/format for JS/TS/JSX/TSX/JSON, biome.json config, biome check/format/lint commands, Prettier-compatible formatter, ~200 lint rules, partial Astro/Svelte/Vue support.

This patch covers v2.0–v2.4 (2025-06-17 – 2026-02-10).

## Index

| Topic | Reference | Key changes |
|-------|-----------|-------------|
| Configuration & Migration | [references/config-and-migration.md](references/config-and-migration.md) | `files.includes` replaces ignore/include, config discovery, nested configs for monorepos |
| Linting & Plugins | [references/linting-and-plugins.md](references/linting-and-plugins.md) | Linter domains, type-aware linting, suppression comments, GritQL plugins |
| Formatting & Language Support | [references/formatting-and-languages.md](references/formatting-and-languages.md) | Assists, HTML formatter, embedded snippets, Vue/Svelte/Astro, Tailwind v4 CSS |

---

## Quick Reference — Breaking Changes

### `files.includes` replaces `files.ignore` and `files.include`

**This is the most impactful v2 breaking change.** Both fields merged into one.

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

- Globs no longer auto-prepend `**/` — you must write full patterns
- `*` no longer matches `/`
- Globs are relative to config file location, not working directory
- `!` prefix — skip formatting/linting but still index for types (v2.3)
- `!!` prefix — completely exclude from all Biome operations (v2.3)

See [references/config-and-migration.md](references/config-and-migration.md) for config discovery and monorepo setup.

---

## Quick Reference — Linter Domains

Framework-specific rule groups that auto-activate based on `package.json` dependencies.

| Domain | Activates for |
|--------|---------------|
| `react` | React projects |
| `next` | Next.js projects |
| `solid` | SolidJS projects |
| `vue` | Vue projects |
| `playwright` | Playwright tests |
| `drizzle` | Drizzle ORM |
| `qwik` | Qwik projects |
| `project` | Module graph analysis (import cycles, unresolved imports) |
| `types` | Type inference rules (no TS compiler needed) |
| `test` | Test-specific rules |

```json
{
  "linter": {
    "domains": {
      "react": "recommended",
      "next": "all",
      "project": "recommended",
      "types": "recommended"
    }
  }
}
```

Values: `"recommended"` (stable rules), `"all"` (including nursery), `"none"`.
CLI: `--only=project`, `--skip=test`.

See [references/linting-and-plugins.md](references/linting-and-plugins.md) for type-aware linting, suppression comments, and GritQL plugins.

---

## Quick Reference — Assists

New category between formatter and linter. Actions without diagnostics. Import organizing moved here from linter.

```json
{
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on",
        "useSortedKeys": { "level": "on", "options": { "groupByNesting": true } },
        "useSortedAttributes": "on",
        "noDuplicateClasses": "on"
      }
    }
  }
}
```

Import organizer revamp: cross-chunk sorting, import merging from same module, custom ordering, export organizing, import attribute sorting.

See [references/formatting-and-languages.md](references/formatting-and-languages.md) for HTML formatter, embedded snippets, and framework support.
