# CLI & Deployment

## Declarative Database Schemas

Supabase CLI supports declarative schema management: define your desired database state in SQL files under `supabase/schemas/`, then auto-generate versioned migrations via diff. This replaces writing migrations imperatively.

```sql
-- supabase/schemas/employees.sql
create table "employees" (
  "id" integer not null,
  "name" text,
  "age" smallint not null
);

create view "profiles" as
select
  id,
  name
from
  "employees";
```

Generate a migration by diffing current migrations against declared schema:

```bash
supabase db diff -f create_employees_table
# Generates supabase/migrations/<timestamp>_create_employees_table.sql

# Apply the migration
supabase migration up
```

To update, edit the schema file in-place and re-diff — the CLI generates only the incremental ALTER statements. Views and functions can be edited in-place without recreating the entire body manually.

Control schema file ordering in `config.toml` (files are lexicographic by default):

```toml
[db.migrations]
schema_paths = [
  "./schemas/employees.sql", # Always first
  "./schemas/*.sql",         # Rest in lexicographic order (deduplicated)
]
```

Roll back locally to a specific migration version (not for production-deployed migrations):

```bash
supabase db reset --version 20241005112233
```

**Caveats**: The `migra` diff tool doesn't track DML statements, view ownership/grants, security invoker on views, materialized views, ALTER POLICY, column privileges, schema privileges, comments, partitions, domain statements, or publications.

## Storage Bucket Seeding via Config

Define storage buckets declaratively in `config.toml` and seed them from local directories:

```toml
[storage.buckets.images]
public = false
file_size_limit = "50MiB"
allowed_mime_types = ["image/png", "image/jpeg"]
objects_path = "./images"                        # Relative to supabase/ directory
```

```bash
supabase seed buckets  # Uploads files from supabase/images/ to "images" bucket
```

## Multiple Seed Files

Split seed data into multiple files using `[db.seed]` config:

```toml
[db.seed]
enabled = true
sql_paths = ['./seeds/*.sql'] # Glob patterns supported, lexicographic order
```

Files are processed in declared order, deduplicated across patterns. Base folder is `supabase/`.

## Restoring Downloaded Backups Locally

Restore a project backup (e.g., from a paused project) to local Supabase:

```bash
supabase init
echo '15.6.1.115' >supabase/.temp/postgres-version # Match your backup's PG version
supabase db start --from-backup db_cluster.backup
```

Earliest supported version: `15.1.0.55`. After restore, restart full stack with `supabase stop && supabase start` to use Auth, Storage, and Studio.

## Branching: Persistent vs Preview Branches

Supabase Branching creates isolated environments (separate DB, API, Auth, Storage, Realtime) that spin off from production. Two types:

- **Preview branches**: Ephemeral — auto-paused after inactivity, deleted when PR merges/closes. Created per PR via GitHub integration or dashboard.
- **Persistent branches**: Long-lived for staging/QA/dev. Created via CLI:

```bash
supabase --experimental branches create --persistent
supabase --experimental branches list # shows BRANCH PROJECT ID column
```

## Branch Configuration with `[remotes]` Block

Configure per-environment settings in `config.toml` using `[remotes.<name>]`:

```toml
[remotes.staging]
project_id = "staging-project-ref"

[remotes.staging.api]
max_rows = 1000

[remotes.staging.db.seed]
enabled = true
sql_paths = ["./seeds/staging.sql"]

[remotes.staging.db]
pool_size = 25
```

All standard config sections (api, db, auth, edge_runtime, etc.) are available under `[remotes.<name>]`. The `project_id` must reference an existing persistent branch.

## Encrypted Secrets in config.toml

Two ways to reference secrets in `config.toml`:

```toml
# Option A: env() syntax — references secrets set via CLI
secret = "env(GITHUB_SECRET)"

# Option B: encrypted: syntax — inline encrypted values (dotenvx)
secret = "encrypted:<encrypted-value>"
```

`encrypted:` only works on designated secret fields: `auth.jwt_secret`, `auth.secret_key`, `auth.email.smtp.pass`, `auth.captcha.secret`, `auth.hook.*.secrets`, `auth.sms.*.auth_token`, `auth.external.*.secret`, `edge_runtime.secrets.*`, `db.root_key`, `db.vault.*`, `studio.openai_api_key`.

Set decryption keys as project secrets:

```bash
npx @dotenvx/dotenvx set MY_SECRET "value" -f supabase/.env.preview
npx supabase secrets set --env-file supabase/.env.keys
```

## Branch Deployment DAG

Merging a branch into production runs a 7-step deployment workflow. If a step fails, dependent steps are skipped:

1. **Clone** — checkout repo at git branch
2. **Pull** — retrieve migrations from main project
3. **Health** — wait up to 2 min for all services healthy
4. **Configure** — apply config.toml changes (GitHub integration only)
5. **Migrate** — apply pending migrations + vault secrets
6. **Seed** — run seed files (must be enabled in config.toml for persistent branches)
7. **Deploy** — deploy changed Edge Functions + update function secrets

## Branch Webhook Notifications

Subscribe to `run.completed` webhooks on persistent branches:

```bash
supabase branches update \
  https:// <branch-ref >--notify-url <branch-ref >.supabase.co/functions/v1/notify-slack
```

Payload follows Standard Webhooks format with `type: "run.completed"`, containing `project_ref`, `details_url`, and `action_run` with step statuses.

## CI: Fetch Branch Credentials in GitHub Actions

Use `supabase branches get` to export branch credentials as env vars in CI:

```yaml
steps:
  - uses: supabase/setup-cli@v1
    with:
      version: latest
  - run: supabase --experimental branches get "$GITHUB_HEAD_REF" -o env >> $GITHUB_ENV
  - name: Run migrations with ORM
    run: psql "$POSTGRES_URL_NON_POOLING" -c 'select 1'
```

This outputs `POSTGRES_URL_NON_POOLING` and other connection variables for the matching Supabase branch.

## Deploy with Seed Data

```bash
supabase db push --include-seed  # push migrations AND run seed.sql on remote
```

## `config push` — Push Config as Code

Push your local `supabase/config.toml` settings to a linked remote project, enabling config-as-code workflows:

```bash
supabase config push
```

This updates the remote project's configuration (API settings, auth config, etc.) to match your local config file. Pair with `supabase link` and version-controlled `config.toml` for reproducible environments.

## Experimental pgdelta Declarative Schema Commands

New experimental commands using pgdelta (distinct from the older migra-based `db diff` approach) for fully declarative schema management:

```bash
# Bootstrap: export current DB schema into declarative SQL files
supabase db schema-declarative-generate --experimental

# Generate a migration by diffing declarative files against migration state
supabase db schema-declarative-sync --experimental
```

Enable permanently in config instead of passing `--experimental`:

```toml
[experimental.pgdelta]
enabled = true
```

`generate` exports the live database schema into SQL files under the declarative schema directory. `sync` computes the diff between your declarative files and current migrations, then optionally names and applies the resulting migration. If no declarative schema exists yet, `sync` offers to run `generate` first.

## `db lint --fail-on` for CI Pipelines

The `--fail-on` flag controls when `db lint` returns a non-zero exit code:

```bash
supabase db lint --fail-on warning # Fail on warnings or errors
supabase db lint --fail-on error   # Fail only on errors
supabase db lint --fail-on none    # Always succeed (default)
```

Also supports `--linked` or `--db-url` to lint remote databases, and `--schema` to restrict to specific schemas.

## `inspect db traffic-profile` — Table I/O Analysis

Analyzes table read/write patterns using `pg_stat_user_tables` and `pg_statio_user_tables`:

```bash
supabase inspect db traffic-profile
```

Classifies each table as Read-Heavy (reads > 5x writes), Write-Heavy (writes > 20% of reads), Balanced, Read-Only, or Write-Only. Output includes blocks read, write tuples, and activity ratio.

## Edge Functions Debugging via V8 Inspector

`supabase functions serve` supports V8 inspector protocol for debugging with Chrome DevTools, VS Code, or IntelliJ:

```bash
supabase functions serve --inspect                         # Alias for --inspect-mode brk
supabase functions serve --inspect-mode run                # Connect anytime, no auto-pause
supabase functions serve --inspect-mode brk                # Break at first line
supabase functions serve --inspect-mode wait               # Pause until inspector connects
supabase functions serve --inspect-mode brk --inspect-main # Also debug main worker
```

Configure the inspector port and worker policy in `config.toml`:

```toml
[edge_runtime]
inspector_port = 8083          # Default inspector port
policy = "oneshot"             # Force restart after each request (useful for reflecting code changes immediately)
```

`oneshot` policy processes one request then exits — ideal for debugging. `per_worker` (default) reuses workers across requests.
