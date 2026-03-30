# Deployment & Branching

## Remote-Specific Branch Configuration

Use the `[remotes]` block in `config.toml` to configure persistent branches with different settings per environment:

```toml
# Default configuration for all branches
[api]
enabled = true
schemas = ["public", "storage", "graphql_public"]

[db]
pool_size = 10

# Staging overrides
[remotes.staging]
project_id = "staging-project-ref"

[remotes.staging.api]
max_rows = 1000

[remotes.staging.db.seed]
enabled = true
sql_paths = ["./seeds/staging.sql"]

# Production overrides
[remotes.production]
project_id = "prod-project-ref"

[remotes.production.db]
pool_size = 25
```

Create persistent branches first (they outlive PRs, unlike ephemeral preview branches):

```bash
supabase --experimental branches create --persistent
supabase --experimental branches list # get project IDs for [remotes] config
```

## Secret Management in config.toml

Two syntaxes for secrets in `config.toml`:

**`env()` — environment variable reference** (works in any config field):

```toml
[auth.smtp]
host = "env(SMTP_HOST)"
user = "env(SMTP_USER)"
password = "env(SMTP_PASSWORD)"

[auth.external.github]
client_id = "env(GITHUB_CLIENT_ID)"
secret = "env(GITHUB_SECRET)"
```

Set secrets per branch via CLI:

```bash
supabase secrets set --env-file ./supabase/.env
supabase secrets set SMTP_HOST=smtp.example.com
```

**`encrypted:` — inline encrypted values** (only works in designated secret fields):

```toml
[auth.external.github]
secret = "encrypted:<encrypted-value>"
```

Fields supporting `encrypted:` syntax include: `auth.jwt_secret`, `auth.secret_key`, `auth.publishable_key`, `auth.anon_key`, `auth.service_role_key`, `auth.email.smtp.pass`, `auth.captcha.secret`, `auth.hook.*.secrets`, `auth.sms.*.auth_token` (and similar), `auth.external.*.secret`, `db.root_key`, `db.vault.*`, `edge_runtime.secrets.*`, `studio.openai_api_key`.

## Deployment Workflow (DAG)

When merging a branch, Supabase runs a 7-step deployment pipeline in order. If a step fails, dependent steps are skipped:

1. **Clone** — checkout repo at git branch
2. **Pull** — retrieve migrations from main project
3. **Health** — wait up to 2 min for all services (Auth, API, DB, Storage, Realtime)
4. **Configure** — apply `config.toml` changes (GitHub integration only)
5. **Migrate** — run pending migrations + vault secrets
6. **Seed** — run seed files (must be enabled in config.toml for persistent branches)
7. **Deploy** — deploy changed Edge Functions + update function secrets

What gets deployed to production on merge: new migrations, Edge Functions declared in `config.toml`, and storage buckets declared in `config.toml`. API, Auth, and seed file configs are ignored by default.

## CLI Commands

### Config Push

Push local `config.toml` settings to a linked remote project:

```bash
supabase config push
```

Updates the remote project's configuration to match your local `supabase/config.toml`. Allows managing project configuration as code.

### Database Lint CI Integration

The `db lint` command supports `--fail-on` for CI/CD pipelines:

```bash
# Fail CI on any warnings or errors
supabase db lint --fail-on warning

# Fail CI only on errors (ignore warnings)
supabase db lint --fail-on error

# Never fail (default)
supabase db lint --fail-on none
```

### Edge Functions Debugging Modes

`functions serve` supports three inspector modes for debugging via Chrome DevTools, VS Code, or IntelliJ:

```bash
# Pause at first line (default when using --inspect)
supabase functions serve --inspect-mode brk

# Allow inspector connection without pausing
supabase functions serve --inspect-mode run

# Pause until inspector connects
supabase functions serve --inspect-mode wait

# Also allow debugging the main worker (disabled by default)
supabase functions serve --inspect-mode brk --inspect-main
```

Configure inspector port and request policy in `config.toml`:

```toml
[edge_runtime]
inspector_port = 8083
# "per_worker" = reuse worker across requests; "oneshot" = new worker per request
policy = "per_worker"
```

### Inspect DB Traffic Profile

Analyze table I/O patterns to classify read/write workloads:

```bash
supabase inspect db traffic-profile
```

Classifies each table as Read-Heavy (reads > 5x writes), Write-Heavy, Balanced, Read-Only, or Write-Only based on block-level I/O from `pg_stat_user_tables` and `pg_statio_user_tables`.
