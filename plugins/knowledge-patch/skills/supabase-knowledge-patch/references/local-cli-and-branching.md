# Local development, CLI, branching, and deployment

## CLI installation and local stack

### CLI installation and upgrade boundary

The npm CLI needs Node 20+. Global npm installation is unsupported; use `npx`/`bunx`, local dev dependency, Homebrew, Scoop, or standalone. Before upgrading a local stack, preserve schema/data and delete old volumes so managed-service migrations start clean:

```sh
supabase db diff -f my_schema
supabase db dump --local --data-only > supabase/seed.sql
supabase stop --no-backup
```

### Local stack resource and lifecycle controls

All services need at least 7 GB RAM. `supabase start -x gotrue,imgproxy` omits services; `--ignore-health-check` bypasses startup failures. `supabase stop` preserves Docker resources; `--no-backup` deletes local data, and with `--all` deletes data for every local Supabase project on the machine.

### CLI credential-storage fallback

`supabase login` uses native credential storage when available, otherwise plaintext `~/.supabase/access-token`. In CI or where plaintext is unacceptable, do not log in; supply `SUPABASE_ACCESS_TOKEN`.

### Local Analytics Docker access

Local Analytics needs Docker logging access: mount `/var/run/docker.sock` on Linux/macOS or expose `tcp://localhost:2375` on Windows. Local logs use `_analytics`; advanced Logs Explorer can use BigQuery rather than default Postgres.

### ARM page-size support for local Vector

Bundled Vector moved from 0.28.1 to 0.53.0 for ARM page-size support so logging works on affected ARM Docker hosts.

## Configuration and declarative schemas

### Remote configuration as code

Link, then push supported `config.toml` settings to hosted:

```sh
supabase link --project-ref <project-id>
supabase config push
```

### Environment-backed local configuration

`config.toml` reads project-root `.env` through quoted `env(NAME)`, not shell interpolation. Keep `.env` untracked.

```toml
[auth.external.github]
enabled = true
client_id = "env(GITHUB_CLIENT_ID)"
secret = "env(GITHUB_SECRET)"
```

### Declarative schemas

Version-controlled `.sql` definitions can be the source of truth for DB structure across environments.

### Postgres Delta declarative schema sync

CLI provides a pg-delta-backed declarative sync command to reconcile a database with schema definitions, beyond storing them in source control.

### Git-backed local SQL snippets

With CLI 2.72.7+, local Studio reads snippets from `supabase/snippets`; commit them for sharing or ignore for personal use.

## Local Functions, Auth, and Storage

### Local Edge Function inspector modes

`functions serve` modes: `run`, `brk`, `wait`; `--inspect` aliases `--inspect-mode brk`; inspecting main worker also needs `--inspect-main`. `[edge_runtime]` can change port 8083 and choose `per_worker` or `oneshot`.

```sh
supabase functions serve --inspect-mode wait --inspect-main
```

### Local Auth email-template files

Local templates use `subject` plus project-relative `content_path`; notifications need `enabled = true`. Supported security notices include password/email/phone changes, MFA enrollment changes, identity link changes. Restart local containers. These settings do not deploy to hosted; copy to Dashboard.

```toml
[auth.email.notification.password_changed]
enabled = true
subject = "Your password has been changed"
content_path = "./templates/password_changed_notification.html"
```

### Local Storage bucket seeding

Declare bucket metadata and `objects_path` in config. `supabase seed buckets` uploads objects. `db pull --schema storage` captures policies, not bucket/object rows.

```toml
[storage.buckets.images]
public = false
file_size_limit = "50MiB"
allowed_mime_types = ["image/png", "image/jpeg"]
objects_path = "./images"
```

## Migrations, lint, and tests

### CI-controlled database lint failures

`db lint` defaults to `--fail-on none` and succeeds despite findings. Use `--fail-on warning` for warnings/errors, or `--fail-on error` for errors only.

```sh
supabase db lint --linked --fail-on warning
```

### Schema-specific pull bootstrap caveat

`db pull --schema <name>` ignores schema when migrations are empty. Bootstrap unrestricted, then pull the schema:

```sh
supabase db pull
supabase db pull --schema auth
```

### Remote reset role boundary

`db reset --linked`/`--db-url` removes user database entities but preserves cluster-level custom roles, so it is not a clean cluster reproduction.

### Migration squash omissions

`migration squash` is schema-only and omits DML such as cron jobs, buckets, and encrypted Vault secrets. Add those back in a new migration.

### Per-file pgTAP rollback

`supabase test db` runs `.sql`/`.pg` from `supabase/tests` through `pg_prove`; every file gets its own always-rolled-back transaction, isolating fixtures.

### Supabase-specific pgTAP helpers

`basejump-supabase_test_helpers` creates Auth users, switches user/anonymous/service contexts, checks schema-wide RLS, freezes DB time. Install through `database.dev`; alphabetical execution lets `000-...` install shared helpers.

```sql
select dbdev.install('basejump-supabase_test_helpers');
create extension if not exists "basejump-supabase_test_helpers" version '0.0.6';
select tests.create_supabase_user('user1@test.com');
select tests.authenticate_as('user1@test.com');
select tests.rls_enabled('public');
```

## Branch lifecycle and configuration

### Branch environment lifecycle and isolation

Every branch is a separate instance with unique credentials and isolated DB/data, Storage objects, Functions, Auth config. New branches contain no production data. Preview branches are ephemeral, auto-pause, and delete when PR merges/closes; persistent branches neither auto-pause nor auto-delete.

### Remote-specific branch configuration

Preview config follows one-to-one Git mapping. Existing persistent branches need `[remotes.<name>]` with project ID from `supabase --experimental branches list`; missing/wrong remote skips configuration when a PR merges to it.

```toml
[remotes.staging]
project_id = "staging-project-ref"

[remotes.staging.db.seed]
enabled = true
sql_paths = ["./seeds/staging.sql"]
```

Create target before committing remote, e.g. `branches create --persistent`. Nest standard DB/API/Auth/Function config under remote.

### Branch-scoped and encrypted secrets

Secrets are per branch. Service config consumes `env(NAME)`. Dotenvx can commit encrypted `supabase/.env.preview`, while ignored `supabase/.env.keys` values become branch secrets.

```sh
npx @dotenvx/dotenvx set OAUTH_SECRET '<secret>' -f supabase/.env.preview
npx supabase secrets set --env-file supabase/.env.keys
```

Inline `encrypted:<value>` decrypts only designated secret fields (Auth/provider/hooks/SMTP/SMS, root/Vault, Studio key, runtime). Ordinary fields use `env()`.

### GitHub-created preview branches

Automatic branching maps new Git branches; **Supabase changes only** restricts to configured directory changes. Integration applies migrations, comments PR status, may load `supabase/seed.sql`, but never copies production data or promotes seed data.

### Persistent-branch action webhooks

Persistent branches can send Standard Webhooks `run.completed` with branch ref, details URL, run IDs/timestamps, and step statuses:

```sh
supabase branches update <branch-ref> --notify-url https://example.com/branch-events
```

## Deployment workflows

### Production deployment scope

With **Deploy to production**, push/merge to production Git branch applies new migrations, deploys Functions, and Storage buckets declared in config. API/Auth settings, seed files, other config are ignored. Require Supabase status so failed preview migrations cannot merge.

### Vercel preview synchronization

Vercel/Supabase pair the hosting preview with Supabase branch and inject environment when PR opens, not Git-branch creation. First build can race; Supabase redeploys the latest PR deployment after variable sync.

### Dashboard branch merging

SQL/Table Editor, config, keys, connection strings apply to selected branch. Merge requests target main only. Updating drifted preview from main replaces existing Functions but preserves preview-only Functions. Dashboard branches omit custom roles; repeat Function deletions on main; resolve migration conflicts on preview. Once main has history, new branches build from migrations, not a fresh schema dump.

### Branch deployment DAG

`Clone -> Pull -> Health -> Configure -> Migrate -> Seed -> Deploy`. Clone is optional for Dashboard. Pull gets main history; Health waits two minutes for services; Configure is GitHub-only; Migrate applies pending migrations/Vault; Seed must be enabled for persistent; Deploy updates changed Functions/secrets. Failure skips dependents. GitHub runs on every pushed commit.

### Incremental migrations and branch recreation

Preview records applied files and only runs new ones. Editing/removing applied migration does not roll back. Push corrected history then delete/recreate preview (or close/reopen PR) to replay all and seed; this discards added preview data. Otherwise seed runs only at creation.

### Custom ORM migrations on previews

Wait for `Supabase Preview`, then fetch credentials. `POSTGRES_URL_NON_POOLING` is direct and appropriate for migration tools.

```sh
supabase --experimental branches get "$GITHUB_HEAD_REF" -o env >> "$GITHUB_ENV"
psql "$POSTGRES_URL_NON_POOLING" -c 'select 1'
```

### Production mapping and migration drift

Base project is always production even if mapped Git branch changes. Merge/rebase production into previews and ensure dependent migration timestamps are later. First connection after auto-pause can time out; retry or use persistent.

### CLI permission repairs for older projects

For old `db pull` failure on `graphql._type`, grant documented `graphql` object privileges. For `db push` 42501 on custom-role objects, grant that role to `postgres`.

```sql
grant all on all tables in schema graphql to postgres, anon, authenticated, service_role;
grant all on all functions in schema graphql to postgres, anon, authenticated, service_role;
grant all on all sequences in schema graphql to postgres, anon, authenticated, service_role;
grant "custom_role" to postgres;
```
