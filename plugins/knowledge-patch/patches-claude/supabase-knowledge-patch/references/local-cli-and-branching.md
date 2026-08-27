# Local Development, CLI, Branching, and Deployment

Use this reference for local-stack configuration, migrations and seeds, CLI compatibility, branches, previews, and GitHub deployment.

## Local development and CLI

### npm CLI runtime and clean-volume upgrades
The npm-distributed CLI requires Node.js 20 or later and must be run with `npx`/`bunx` or installed as a development dependency; global npm installation is unsupported. Before upgrading a local stack, preserve uncommitted schema and data, then remove its volumes so managed-service migrations start cleanly.

```sh
supabase db diff -f my_schema
supabase db dump --local --data-only > supabase/seed.sql
supabase stop --no-backup
```

### Remote configuration as code
`supabase config push` applies the local `supabase/config.toml` settings to the linked hosted project.

### Declarative schema files
Desired database state can live in `supabase/schemas/*.sql`; `supabase db diff -f <name>` generates an incremental migration, and `supabase migration up` applies it locally. Files run lexicographically unless `[db.migrations].schema_paths` specifies an order; overlapping globs are deduplicated and sorted.

```toml
[db.migrations]
schema_paths = ["./schemas/employees.sql", "./schemas/*.sql"]
```

The experimental pgdelta workflow can bootstrap those files from a local, linked, or URL-addressed database and then generate a migration by syncing them against migration state.

```sh
supabase --experimental db schema-declarative generate
supabase --experimental db schema-declarative sync
```

Schema diffs do not cover DML, materialized views, view ownership or grants, `alter policy`, column or schema privileges, comments, partitions, publication membership, or domains; keep such changes in explicit versioned migrations.

### Migration command hazards
`supabase migration squash` emits a schema-only result and omits all DML, including cron jobs, Storage buckets, and Vault secrets; it replaces the latest migration unless `--version` selects another target. Remote `db reset` drops user-created database entities but preserves cluster-level custom roles, and an initial `db pull --schema ...` ignores the schema filter when local migration history is empty, requiring an unfiltered pull first.

### Local secrets and Auth email templates
`config.toml` can interpolate values from a project-root `.env` with `env(NAME)`. Local Auth templates use relative `content_path` files and require a stack restart; hosted templates must instead be copied into the hosted project configuration.

```toml
[auth.external.github]
client_id = "env(GITHUB_CLIENT_ID)"
secret = "env(GITHUB_SECRET)"

[auth.email.notification.password_changed]
enabled = true
content_path = "./templates/password_changed.html"
```

### Declarative local Storage buckets
Storage RLS can be pulled with `supabase db pull --schema storage`, but buckets and objects are rows rather than schema. Declare bucket settings and seed local objects from `objects_path` with `supabase seed buckets`.

```toml
[storage.buckets.images]
public = false
file_size_limit = "50MiB"
allowed_mime_types = ["image/png", "image/jpeg"]
objects_path = "./images"
```

### Deterministic multi-file seeds
`[db.seed].sql_paths` accepts ordered paths and globs relative to `supabase`; glob matches are lexically sorted, duplicate matches are removed, and unmatched patterns warn.

```toml
[db.seed]
enabled = true
sql_paths = ["./countries.sql", "./seeds/*.sql"]
```

### Restoring a downloaded backup locally
Set the local Postgres image to the backup's recorded `PG:` version, then start only the database with `--from-backup`; this path supports backup versions from `15.1.0.55` onward.

```sh
echo '15.6.1.115' > supabase/.temp/postgres-version
supabase db start --from-backup db_cluster.backup
```

### Database-test isolation and CI linting
`supabase test db` runs each `.sql` or `.pg` pgTAP file in its own transaction and rolls it back regardless of outcome. `supabase db lint` exits successfully by default even with findings; use `--fail-on warning` or `--fail-on error` to make CI fail at the desired threshold.

## CLI compatibility

### Local Edge Functions receive JWKs
CLI 2.84.0 exposes JWKs to Edge Functions as a non-internal environment value, making the local signing-key set available to function code rather than reserving it for runtime internals.

### ARM page-size support for local Vector
CLI 2.84.2 updates the Docker Vector service from 0.28.1 to 0.53.0 for ARM page-size support. ARM hosts that cannot start the local Vector container need this CLI version or later.

### Edge Runtime restarts refresh Kong
The CLI 2.84.4 pre-release reloads Kong after restarting Edge Runtime, preventing stale Edge Runtime DNS state from surviving a local restart.

### Local notification email templates
The CLI 2.84.5 pre-release fixes mounting notification email templates in the local stack.

## Branches and deployments

### Persistent branches use remote-scoped configuration
A persistent branch must exist before it can be targeted under `[remotes.<name>]`; set its branch project ID, then nest any standard configuration below that remote. When a PR is merged into the persistent branch, the integration applies the matching remote configuration and skips configuration if the remote is absent or its project ID is wrong.

```toml
[remotes.staging]
project_id = "staging-branch-ref"

[remotes.staging.db.seed]
enabled = true
sql_paths = ["./seeds/staging.sql"]
```

### Encrypted preview secrets have a restricted config surface
CLI-managed secrets are isolated per branch. For Git-backed previews, commit a dotenvx-encrypted `supabase/.env.preview`, keep `supabase/.env.keys` untracked and upload it as branch secrets; the executor decrypts it, but literal `encrypted:` values work only in designated secret fields and other fields must use `env(NAME)`.

```sh
npx @dotenvx/dotenvx set OAUTH_SECRET '<secret>' -f supabase/.env.preview
npx supabase secrets set --env-file supabase/.env.keys
```

### Dashboard branches do not round-trip every change
Dashboard-managed branches can merge only into main, and the base project always remains the production branch even if a different GitHub branch is linked to it. Pulling production into a preview replaces its existing Edge Functions while preserving preview-only new functions; custom roles are not captured on branch creation, function deletions must be repeated on main, and migration conflicts need manual resolution.

### Preview migrations and seeds are incremental
Preview branches start without production data, remember applied migrations, and run their seed only once at creation; later commits apply only new migrations. To replace an already-applied migration or rerun seeding, push the corrected files and recreate the preview by closing and reopening its PR, which reruns all migrations and loses branch-local data; seed changes never merge into production.

### GitHub production deployment is selective
The GitHub integration's **Deploy to production** option applies new migrations and deploys Edge Functions and Storage buckets declared in `config.toml`. API settings, Auth settings, and seed files are ignored by that option by default.

### Branch deployments form a dependent workflow
The workflow runs `clone → pull → health → configure → migrate → seed → deploy`; health waits up to two minutes for all branch services, configuration is GitHub-only, migration also applies Vault secrets, and persistent-branch seeding must be enabled in `config.toml`. A failed parent step skips its dependent steps, so a migration failure prevents seeding and deployment.

### Persistent branches emit completion webhooks
A persistent branch can send a Standard Webhooks `run.completed` payload containing its project reference, log URL, failure state, and per-step statuses whenever an action run finishes.

```sh
supabase branches update <branch-ref> \
  --notify-url https://example.com/branch-runs
```

### Custom ORM jobs can retrieve preview credentials
After the `Supabase Preview` check succeeds, a GitHub Actions job can export the matching branch environment and run custom migrations or seeds with credentials such as `POSTGRES_URL_NON_POOLING`.

```sh
supabase --experimental branches get "$GITHUB_HEAD_REF" -o env >> "$GITHUB_ENV"
psql "$POSTGRES_URL_NON_POOLING" -c 'select 1'
```

### Vercel synchronization occurs at PR creation
Supabase supplies the corresponding preview-branch environment variables when a pull request opens, not when its Git branch is created. Because Vercel may begin its preview before that update lands, Supabase automatically redeploys the PR's most recent deployment.

### Legacy GraphQL privileges can block `db pull`
On older hosted projects, `db pull` can fail while locking `graphql._type`; restore object privileges in the `graphql` schema before retrying.

```sql
grant all on all tables in schema graphql to postgres, anon, authenticated, service_role;
grant all on all functions in schema graphql to postgres, anon, authenticated, service_role;
grant all on all sequences in schema graphql to postgres, anon, authenticated, service_role;
```

### Custom role ownership can block `db push`
If `db push` fails with `42501` on objects owned by a custom role, grant `postgres` membership in that owner role.

```sql
grant "custom_role" to "postgres";
```

## Platform capabilities

### Gitless branching is the default
Branches can be created and managed directly from the dashboard without a GitHub integration, and this is now the default branching workflow.

### Local SQL snippets
CLI 2.72.7 adds saved snippets to local Studio. Files live in `supabase/snippets`, appear automatically in Studio, and can be committed to Git or ignored locally.
