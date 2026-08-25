# Permissions and Dependency Security

Keep runtime permissions narrow and enforce dependency, lifecycle-script, registry, and publication trust controls.

## Additional `.npmrc` controls (2.8-guide)

`.npmrc` can set `min-release-age`, `certfile` and `keyfile` for registry mTLS, and an `email` on legacy `_auth` entries. `NPM_CONFIG_REGISTRY` now overrides a registry selected in `.npmrc`.

```ini
min-release-age=72h
```

## Age-filtered npm dist-tags (2.9.1)

When minimum-dependency-age policy filters the version named by an npm dist-tag, resolution now falls back to an eligible version.

## Automated vulnerability remediation (2.8-guide)

`deno audit fix` (also available as `deno audit --fix`) upgrades vulnerable npm packages to the nearest patched versions that still satisfy their declared constraints. Required major-version upgrades are reported separately instead of being applied.

```sh
deno audit fix
```

## Case-insensitive trust-policy exclusions (2.9.1)

Package names in `trust-policy-exclude[]` are now matched case-insensitively.

## Dependency security auditing (2.6-guide)

`deno audit` scans the complete npm and JSR dependency graph against GitHub's CVE database. Experimental `deno audit --socket` also queries socket.dev, using `SOCKET_API_KEY` when present so organization policies can participate in the report.

## Environment-permission behavior (2.3.0)

Programs may read `NO_COLOR` without `--allow-env`, so respecting the standard color opt-out does not require broader environment access. An explicit `--allow-env` also takes precedence over an overlapping `--deny-env` restriction.

## Experimental permission broker (2.6-guide)

Setting `DENO_PERMISSION_BROKER_PATH` delegates permission requests to a separate broker process; while it is active, every `--allow-*`, `--deny-*`, and `--ignore-*` flag is ignored and requests go to the broker instead.

```sh
DENO_PERMISSION_BROKER_PATH=/perm_broker.sock deno run untrusted_code.ts
```

## Ignored audit advisories (2.7-guide)

`deno audit --ignore` accepts comma-separated CVE IDs, allowing CI to suppress accepted risks or false positives.

```sh
deno audit --ignore=CVE-2024-12345,CVE-2024-67890
```

## Lifecycle-script approval (2.6-guide)

`deno approve-scripts` replaces `deno install --allow-scripts` with an interactive package-by-package approval flow. Decisions are persisted in the `allowScripts` field of `deno.json` so later installs have an explicit trust policy.

## Masking denied reads and environment variables (2.6-guide)

`--ignore-read` makes selected file access fail with `NotFound`, while `--ignore-env` makes selected environment reads return `undefined`, allowing dependencies to handle the resources as absent instead of receiving `NotCapable`. With partial `--allow-env`, `Deno.env.toObject()` now returns only the permitted variables.

```sh
deno run --ignore-read=/etc --ignore-env=AWS_SECRET_KEY main.ts
```

## Minimum dependency age (2.6-guide)

`minimumDependencyAge` prevents installation or update to package releases younger than the configured threshold; values may be minutes, an ISO-8601 duration, or an RFC3339 date or timestamp, and `--minimum-dependency-age` provides the CLI equivalent.

```json
{ "minimumDependencyAge": "P2D" }
```

## Named permission sets (2.5-guide)

`deno.json` can define reusable named sets under `permissions`; select one with `--permission-set=<name>` or `-P=<name>`, and select a set named `default` with bare `-P`. The `test`, `bench`, and `compile` keys may instead contain inline permissions, but Deno refuses to apply configured permissions implicitly: opt in with `-P`, or supply explicit permission flags or `-A`.

```json
{
  "permissions": {
    "process-data": {
      "read": ["./data"],
      "write": ["./data"]
    }
  },
  "tasks": { "dev": "deno run -P=process-data main.ts" }
}
```

## Narrow allow rules over broad denies (2.6.0)

A more-specific `--allow-*` rule now overrides a broader `--deny-*` rule, allowing a narrowly scoped exception without relaxing the surrounding denial.

```sh
deno run --deny-read --allow-read=./data main.ts
```

## Network and import permission controls (2.4-guide)

`--allow-net` accepts subdomain wildcards and CIDR ranges, while `--deny-import` can block remote import hosts that Deno otherwise permits by default. Runtime permission queries now accept `{ name: "import" }`, and `Deno.execPath()` no longer requires read permission.

```sh
deno run --allow-net='*.foo.localhost' subdomains.ts
deno run --allow-net=192.168.0.128/25 cidr.ts
deno run --deny-import=cdn.jsdelivr.net main.ts
```

## No-downgrade npm trust policy (2.9-guide)

Setting `trust-policy=no-downgrade` makes resolution fail when a newly published version has weaker publishing evidence than the strongest earlier version of that package, ranking staged 2FA publishing above trusted publishing with provenance and provenance alone. The policy is off by default; `trust-policy-ignore-after` exempts older releases by age and `trust-policy-exclude[]` exempts named packages.

```ini
trust-policy=no-downgrade
```

## npm prereleases through dist-tags (2.9.1)

When an npm dist-tag resolves to a prerelease, adding that dependency now pins the resolved prerelease version.

## OpenTelemetry output and permission logs (2.8-guide)

The built-in integration can print human-readable telemetry to stderr with the `console` protocol or export OTLP over gRPC. Setting `DENO_AUDIT_PERMISSIONS=otel` sends permission checks as span-correlated OTel log records.

```sh
OTEL_DENO=true OTEL_EXPORTER_OTLP_PROTOCOL=console DENO_AUDIT_PERMISSIONS=otel deno run -A main.ts
OTEL_DENO=true OTEL_EXPORTER_OTLP_PROTOCOL=grpc OTEL_EXPORTER_OTLP_ENDPOINT=https://otel.example.com:4317 deno run -A main.ts
```

## Permission audit logging (2.5-guide)

`DENO_AUDIT_PERMISSIONS=<path>` writes permission checks as JSONL records containing a timestamp, permission, and value. Combining it with `DENO_TRACE_PERMISSIONS=1` adds the requesting stack trace.

```sh
DENO_AUDIT_PERMISSIONS=permissions.jsonl DENO_TRACE_PERMISSIONS=1 deno run -A main.ts
```

## Permission tracing and scoped environment access (2.1-guide)

Setting `DENO_TRACE_PERMISSIONS` adds call stacks to interactive permission prompts, but its stack collection is expensive and intended for diagnosis. Environment permission values may end in `*`, allowing a whole variable-name prefix, and `--env-file` may be supplied more than once.

```sh
DENO_TRACE_PERMISSIONS=1 deno run main.ts
deno run --allow-env="AWS_*" --env-file=.env --env-file=.env.local main.ts
```

## Permission-free current directory (2.2-guide)

`Deno.cwd()` no longer prompts for or requires `--allow-read`; revealing the current working-directory path is now unconditionally allowed.

## Private registries through `.npmrc` (2.0-guide)

Deno automatically reads scoped registry and authentication settings from `.npmrc`, with no Deno-specific registry configuration required.

```ini
@mycompany:registry=http://mycompany.com:8111/
//mycompany.com:8111/:_auth=secretToken
```

## Terminal-symlink truncation (2.9.0)

Filesystem truncation no longer follows a symlink in the terminal path component, preventing the symlink's target from being shortened unexpectedly.

## Unix-socket network permissions (2.9.0)

Unix-domain socket operations, including Unix proxies used by `Deno.createHttpClient()`, now require network permission.

```sh
deno run --allow-net app.ts
```
