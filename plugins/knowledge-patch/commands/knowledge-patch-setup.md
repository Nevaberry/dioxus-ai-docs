---
name: knowledge-patch-setup
description: Scan this project for technologies, install matching Nevaberry knowledge patch plugins
---

# Knowledge Patch Setup

Scan this project to detect technologies in use and install matching knowledge patch plugins.

## Step 1: Detect Technologies

Scan the project root for config files and dependencies to determine what technologies are used. Read the relevant files and check against the detection rules below.

### Config files to check

Read whichever of these files exist in the project root:

- `package.json` — JavaScript/TypeScript ecosystem (check `dependencies` and `devDependencies`)
- `Cargo.toml` — Rust ecosystem (check `[dependencies]` and `[dev-dependencies]`)
- `pyproject.toml` — Python ecosystem (check `[project.dependencies]` or `[tool.poetry.dependencies]`)
- `requirements.txt` — Python dependencies (one per line)
- `Pipfile` — Python dependencies
- `go.mod` — Go ecosystem (check `require` block)
- `deno.json` / `deno.jsonc` — Deno ecosystem
- `docker-compose.yml` / `docker-compose.yaml` — look for service images
- `wrangler.toml` / `wrangler.jsonc` — Cloudflare Workers

Also check for the existence of these indicator files (no need to read contents):

- `bun.lock` or `bun.lockb` or `bunfig.toml` → Bun
- `tsconfig.json` → TypeScript
- `next.config.*` → Next.js
- `Dioxus.toml` → Dioxus
- `.python-version` or `poetry.lock` or `uv.lock` → Python
- `build.zig` → Zig
- `svelte.config.*` → Svelte
- `astro.config.*` → Astro
- `tailwind.config.*` → Tailwind CSS
- `vite.config.*` → Vite
- `Dockerfile` → Docker
- `go.mod` → Go
- `biome.json` or `biome.jsonc` → Biome
- `vitest.config.*` → Vitest
- `playwright.config.*` → Playwright
- `k8s/` or `kubernetes/` or `*.k8s.yaml` → Kubernetes
- `terraform/` or `*.tf` → Terraform
- `helmfile.yaml` or `Chart.yaml` → Kubernetes

### Detection rules → Published patches (available now)

| Technology | Patch name | Detected when |
|------------|-----------|---------------|
| Bun | `bun-knowledge-patch` | `bun.lock`, `bun.lockb`, or `bunfig.toml` exists |
| TypeScript | `typescript-knowledge-patch` | `tsconfig.json` exists, or `typescript` in package.json |
| Next.js | `nextjs-knowledge-patch` | `next` in package.json dependencies, or `next.config.*` exists |
| Python | `python-knowledge-patch` | `pyproject.toml`, `requirements.txt`, `Pipfile`, `.python-version`, `poetry.lock`, or `uv.lock` exists |
| Rust | `rust-knowledge-patch` | `Cargo.toml` exists |
| Dioxus | `dioxus-knowledge-patch` | `dioxus` in Cargo.toml dependencies, or `Dioxus.toml` exists |
| PostgreSQL | `postgresql-knowledge-patch` | `pg`, `postgres`, `knex`, `typeorm` in package.json; `psycopg2`, `psycopg`, `asyncpg`, `sqlalchemy` in Python deps; `sqlx`, `diesel`, `tokio-postgres` in Cargo.toml; `postgres` image in docker-compose |
| PostGIS | `postgis-knowledge-patch` | `postgis`, `knex-postgis` in package.json; `geoalchemy2`, `django.contrib.gis`, `geopandas`, `postgis` in Python deps; `postgis` in Cargo.toml |
| Node.js | `nodejs-knowledge-patch` | `package-lock.json`, `.nvmrc`, `.node-version`, or `pnpm-lock.yaml` exists |
| React | `react-knowledge-patch` | `react` in package.json |
| Go | `go-knowledge-patch` | `go.mod` exists |
| Docker | `docker-knowledge-patch` | `Dockerfile` or `docker-compose.*` exists |
| Svelte | `svelte-knowledge-patch` | `svelte` in package.json or `svelte.config.*` exists |
| Tailwind CSS | `tailwind-knowledge-patch` | `tailwindcss` in package.json or `tailwind.config.*` exists |
| Prisma | `prisma-knowledge-patch` | `prisma` or `@prisma/client` in package.json |
| Drizzle | `drizzle-knowledge-patch` | `drizzle-orm` in package.json |
| Vite | `vite-knowledge-patch` | `vite` in package.json or `vite.config.*` exists |
| Deno | `deno-knowledge-patch` | `deno.json` or `deno.jsonc` exists |
| Astro | `astro-knowledge-patch` | `astro` in package.json or `astro.config.*` exists |
| Zig | `zig-knowledge-patch` | `build.zig` exists |
| Axum | `axum-knowledge-patch` | `axum` in Cargo.toml |
| Leptos | `leptos-knowledge-patch` | `leptos` in Cargo.toml |
| SQLx | `sqlx-knowledge-patch` | `sqlx` in Cargo.toml |
| Vercel AI SDK | `vercel-ai-sdk-knowledge-patch` | `ai` or `@ai-sdk/*` in package.json |
| SQLite | `sqlite-knowledge-patch` | `better-sqlite3` in package.json; `rusqlite` in Cargo.toml |
| Kubernetes | `kubernetes-knowledge-patch` | `k8s/`, `kubernetes/`, `*.k8s.yaml`, `helmfile.yaml`, or `Chart.yaml` exists |
| Supabase | `supabase-knowledge-patch` | `@supabase/supabase-js` in package.json or `supabase/` directory exists |
| Biome | `biome-knowledge-patch` | `biome.json` or `@biomejs/biome` in package.json |
| Hono | `hono-knowledge-patch` | `hono` in package.json |
| tRPC | `trpc-knowledge-patch` | `@trpc/server` or `@trpc/client` in package.json |
| Terraform | `terraform-knowledge-patch` | `*.tf` files or `terraform/` directory exists |

### Detection rules → Coming soon (not yet published)

| Technology | Patch name | Detected when |
|------------|-----------|---------------|
| Stripe | `stripe-knowledge-patch` | `stripe` in package.json or Python deps |
| Cloudflare | `cloudflare-knowledge-patch` | `wrangler.toml` exists, or `wrangler` in package.json |
| DuckDB | `duckdb-knowledge-patch` | `duckdb` in package.json, Python deps, or Cargo.toml |
| Zod | `zod-knowledge-patch` | `zod` in package.json |
| Valkey | `valkey-knowledge-patch` | `valkey` image in docker-compose; `ioredis`, `@valkey/valkey-glide` in package.json |
| shadcn/ui | `shadcn-knowledge-patch` | `components.json` with `$schema` containing `shadcn` |

## Step 2: Present Results

Show the user what was detected:

**If recommendations found:**

```
Detected technologies with available knowledge patches:

  bun-knowledge-patch
  typescript-knowledge-patch
  postgresql-knowledge-patch

Also detected (patches coming soon):
  react-knowledge-patch
  stripe-knowledge-patch
```

**If nothing detected:**

Tell the user no technologies were auto-detected and ask if they want to manually select from the published patches list in the table above.

## Step 3: Confirm with User

Use AskUserQuestion to let the user confirm which patches to install. Pre-select all recommended (published) patches.

Then ask which settings scope to use. **Default to Project scope** (`.claude/settings.json`) — this shares patches with collaborators via git so the whole team benefits. Mention that the user can choose Local scope (`.claude/settings.local.json`) instead if they prefer a personal setup.

Present it as: "I'll install these to `.claude/settings.json` (project scope, shared via git). Want me to use local scope instead?"

## Step 4: Install Patches

For each selected patch, update the chosen settings file. Read the file first (or start with `{}` if it doesn't exist).

**CRITICAL: Only add entries — never remove or overwrite existing ones.** The `enabledPlugins` object may already contain other plugins (e.g., `frontend-skill`, `nevaberry-memory`) that are NOT knowledge patches. You must preserve every existing key in the file and in `enabledPlugins`. Only add new `*-knowledge-patch@nevaberry-plugins` entries alongside whatever is already there.

For example, if the file already contains:

```json
{
  "permissions": { "allow": ["Read"] },
  "enabledPlugins": {
    "frontend-skill@some-publisher": true,
    "nevaberry-memory@nevaberry-plugins": true
  }
}
```

After installing bun and typescript patches, the result must be additive:

```json
{
  "permissions": { "allow": ["Read"] },
  "enabledPlugins": {
    "frontend-skill@some-publisher": true,
    "nevaberry-memory@nevaberry-plugins": true,
    "bun-knowledge-patch@nevaberry-plugins": true,
    "typescript-knowledge-patch@nevaberry-plugins": true
  }
}
```

Make sure the `.claude/` directory exists (create if needed).

## Step 5: Show Summary

Show the user a completion summary:

```
Knowledge patch setup complete:

  Installed patches:
    - bun-knowledge-patch
    - typescript-knowledge-patch

  Settings file: .claude/settings.json

  Restart your AI coding tool for patches to take effect.
  The SessionStart hook will enforce patch usage automatically in every session.
```

## Important Notes

- This command is idempotent — running it again updates existing configuration
- Existing patches in settings are preserved; new ones are added alongside them
- No CLAUDE.md or AGENTS.md modification needed — the SessionStart hook handles enforcement automatically
- Works across Claude Code, Cursor, and any tool supporting the plugin hook system
