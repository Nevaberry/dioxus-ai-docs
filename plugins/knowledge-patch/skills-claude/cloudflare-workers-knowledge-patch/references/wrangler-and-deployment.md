# Wrangler and deployment

This reference consolidates Wrangler behavior from batches `2025` and `2026`
with authentication, startup, and Builds changes from batch
`2026-07-30-2026-08-14`.

## Upgrade to Wrangler v4

Wrangler v4 follows the Node.js release lifecycle and no longer supports
Node.js 16. It updates bundled esbuild from 0.17.19 to 0.24. Wrangler minor
releases may update pre-1.0 esbuild versions in ways that change bundling.

Wildcard dynamic imports bundle every matching file. Inspect the resulting
bundle for unintended files and rerun build tests after Wrangler minor updates.

### Replace removed and deprecated behavior

| Earlier behavior | Replacement |
| --- | --- |
| `legacy_assets` | Static Assets |
| `node_compat` | `nodejs_compat` |
| `getBindingsProxy()` | `getPlatformProxy()` |
| `wrangler publish` | `wrangler deploy` |
| `wrangler pages publish` | `wrangler pages deploy` |
| `wrangler generate` | `npm create cloudflare@latest` |
| `wrangler version` | `wrangler --version` |

Remove `usage_model`; it has no effect. Workers Sites and service environments
configured with `legacy_env` are deprecated in favor of Static Assets and
Wrangler environments.

## Distinguish local and remote resources

Every Wrangler command that supports both local and remote operation defaults
to local mode. KV and R2 commands need `--remote` when they should touch
account data:

```sh
wrangler kv key get --binding MY_KV "my-key" --remote
```

Make the target explicit in scripts so a local default does not silently
replace an intended remote operation.

## Use authentication profiles

Wrangler supports named OAuth logins that are activated for a directory and
its descendants:

```sh
wrangler auth create client-a
wrangler auth activate client-a ~/clients/client-a
wrangler deploy --profile client-a
```

`account_id` can still constrain a project to the intended account.
`CLOUDFLARE_API_TOKEN` takes precedence over profiles in CI and other automated
environments.

### Device-code login

Wrangler 4.119.0 adds an OAuth device flow that does not open a callback server
on `localhost:8976`. It works from containers, SSH sessions, Codespaces, or a
second device. Suppress browser launch when needed:

```sh
npx wrangler login --device --browser=false
```

## Generate runtime declarations

`wrangler types` builds `worker-configuration.d.ts` from compatibility date,
flags, bindings, and module rules. Include the file with
`compilerOptions.types`, add `@types/node` when using Node.js compatibility,
and detect stale committed output in CI:

```sh
wrangler types --check
```

`@cloudflare/workers-types` v5 exposes only the current stable types at its
root and experimental APIs at `/experimental`. Dated package entrypoints are
removed.

## Inspect startup behavior

Wrangler 4.116.0 extends `wrangler check startup` with raw and gzip bundle
sizes and a local CPU summary divided into sampled, active,
garbage-collection, and idle time.

The command still writes `worker-startup.cpuprofile` for Chrome DevTools or VS
Code. Use local durations to locate expensive startup work, but do not treat
them as authoritative production startup timings.

## Pin the Workers Builds Node.js version

Workers Builds defaults to Node.js 24.18.0. The build image preinstalls Node.js
22.23.2 and 24.18.0. Override the selected version with `NODE_VERSION`,
`.nvmrc`, or `.node-version` when the project requires a different runtime.
