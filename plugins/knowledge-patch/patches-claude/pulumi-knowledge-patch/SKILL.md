---
name: pulumi-knowledge-patch
description: Pulumi
version: "3.254.0"
license: MIT
metadata:
  author: Nevaberry
---


# Pulumi Knowledge Patch

Use this skill when implementing, reviewing, upgrading, or operating Pulumi projects. Inspect the project's `Pulumi.yaml`, language manifest, CLI version, backend, and provider constraints before applying version-sensitive guidance. Prefer the project's code, schemas, generated SDKs, and observed CLI behavior when they disagree with generalized advice.

## Reference Index

| Reference | Topics |
| --- | --- |
| [CLI operations and configuration](references/cli-operations-and-configuration.md) | Command changes, environment controls, machine output, project creation, Neo, logging, and tracing |
| [Cloud, policy, and operations](references/cloud-policy-and-operations.md) | Authentication, Pulumi Cloud and ESC, policy, CI/CD, backends, credentials, and remote operations |
| [Components, packages, and runtimes](references/components-packages-and-runtimes.md) | Cross-language components, package lifecycle, templates, runtime baselines, language SDKs, and testing |
| [Providers, schemas, PCL, and protocols](references/providers-schemas-pcl-and-protocols.md) | Provider authoring, plugin resolution, schema and code generation, PCL, invokes, and protocol changes |
| [State, import, and resource lifecycle](references/state-import-and-lifecycle.md) | Protection, deletion, replacement, hooks, imports, stack migration, state repair, and direct resources |

## Load References by Task

- For an application program or generated project, start with components, packages, and runtimes.
- For a CLI script or CI wrapper, load CLI operations and configuration, then cloud operations if it authenticates or selects a backend.
- For provider, converter, analyzer, schema, or code-generator work, load providers, schemas, PCL, and protocols.
- For imports, repairs, replacements, protection, or resource hooks, load state, import, and resource lifecycle.
- For ESC, Pulumi Cloud, Registry policy, remote deployment, or DIY backend work, load cloud, policy, and operations.
- Load more than one reference when a workflow crosses layers; package generation, imports, and component providers commonly do.

## Breaking Changes and Removed Surfaces

- Do not use `pulumi query`; the command has been removed.
- Do not implement provider `StreamInvoke`; that RPC has been removed from the Provider service.
- Do not use the experimental local `Pulumi.<stack>.deploy.yaml` workflow or its CLI commands. Manage deployment settings through Pulumi Cloud.
- Do not use `pulumi new --ai` or its removed interactive AI mode. Use `pulumi neo` for the replacement terminal workflow.
- Treat logout as destructive to local backend configuration: it now removes all backend configuration, shared temporary agent credentials, and the current tokenless backend.
- The legacy DIY-backend deprecation is now an error. If a temporary bypass is unavoidable, the current variable is `PULUMI_DIY_BACKEND_IGNORE_DEPRECATION_ERROR`.
- Provider tooling must use the `pulumi-language-dotnet/v3/codegen` module rather than the deprecated core-repository .NET codegen package.
- PCL `package` block labels are deprecated.
- Node.js Pulumi programs now require Node.js 22 or later. Newly generated TypeScript projects use `nodenext` for both module settings.

For the exact migration details, read the CLI, component/runtime, and provider references before changing scripts or build tooling.

## High-Risk Operation Checklist

Before preview, update, refresh, destroy, import, or direct state work:

1. Confirm the active backend and stack. Current-stack selection is backend-scoped, and `PULUMI_STACK` can select a stack without persisting a selection.
2. Inspect protection, retention, parents, providers, replacement relationships, hooks, and pending creates.
3. Decide whether changed program code must run. Refresh and destroy skip it unless run-program behavior is requested; preview and update accept it only with refresh.
4. Keep secrets redacted. `--show-secrets` emits plaintext to terminals and captured logs.
5. Use `--output json` when another process consumes operation results; diagnostics are emitted on stderr.
6. Treat `--ignore-protect`, `state delete --all`, multi-URN state deletion, and direct state import as explicit repair or override operations.
7. Export or otherwise secure state before manual repair, and verify with a preview afterward.

## Quick Reference: Engine and Configuration

### Run program code for refresh-aware operations

Use `--run-program` with refresh or destroy when the program establishes credentials, loads secrets, defines dynamic providers, or otherwise supplies operation context:

```shell
pulumi refresh --run-program
pulumi destroy --run-program
PULUMI_RUN_PROGRAM=true pulumi up --refresh
```

`pulumi preview --refresh` and `pulumi up --refresh` also accept `--run-program`. Refresh and destroy accept `--config` and `--config-path`, and refreshing stack configuration includes imported environments.

### Target and safety controls

Use `--exclude <URN>` to omit a target and add `--exclude-dependents` to omit its children. An explicit child value of `protect: false` or `retainOnDelete: false` overrides an inherited true value. A protected-delete error does not stop unrelated deployment work.

Use `pulumi state protect`, `state taint`, and `state untaint` for durable state changes. Use `--ignore-protect` only for a single preview, update, or destroy that intentionally permits protected deletions.

### Configuration and environment overrides

- `PULUMI_OPTION_<FLAG>` supplies any CLI flag; for example, `PULUMI_OPTION_REFRESH=true` supplies `--refresh`.
- `PULUMI_PARALLEL` maps to `--parallel`; `PULUMI_PARALLEL_DIFF` enables concurrent diffs.
- `pulumi config set --type` fixes a scalar's stored type; `--raw` preserves newlines from stdin.
- `--override-env` temporarily replaces imported environments for one engine operation.
- `--skip-config-validation` bypasses project config-schema validation for one engine operation.
- The YAML config change that preserved types was reverted; YAML `null` still warns when it would become an empty string.

## Quick Reference: Output, Logs, and Traces

Use `--output json` with `up`, `preview`, `refresh`, `destroy`, and `import`. Operation summaries identify affected resources; historical summaries are available through:

```shell
pulumi stack history events --summary
```

Automatic encrypted CLI logging is enabled by default. Property-value secrets are redacted. Use `pulumi logs ls`, `decrypt`, `rm`, and `share` to manage captures.

Use `--otel-traces` with a relative file or a supported endpoint. gRPC, secure gRPC, and HTTPS endpoints are supported; headers and `OTEL_RESOURCE_ATTRIBUTES` can enrich exports. `TRACEPARENT` attaches CLI spans to an existing trace.

## Quick Reference: Authentication

For CI/CD, prefer native OIDC login over a stored long-lived Pulumi token. `--oidc-token` accepts a raw JWT or `file://` path; organization, team, and user can be inferred from claims or narrowed explicitly. The exchanged access token expires after two hours by default unless `--oidc-expiration` changes it.

If `credentials.json` contains an OAuth refresh token, a 401 triggers one automatic token refresh and retry. Stored credentials may opt into OS-protected encryption with `PULUMI_CREDENTIAL_STORE`.

## Quick Reference: Packages and Components

A cross-language component source contains `PulumiPlugin.yaml`; same-language-only components do not need it. TypeScript exports component classes directly, YAML exposes top-level `components`, and Python, Go, .NET, and Java start runtime-specific component provider hosts.

Install source packages with `pulumi package add`, recording them under `packages` in `Pulumi.yaml`; run `pulumi install` after a fresh checkout when generated SDKs are not committed. Prefix local paths with `./` or `../`. Package sources can be Git URLs, local directories, Registry identifiers, parameterized packages, or extension packages.

Unqualified package names resolve through the Pulumi Cloud Registry. Use `--server <URL>` only when commands should talk directly to a plugin server and preserve that server in `Pulumi.yaml`.

## Quick Reference: Resource Lifecycle

Use `replaceWith` when replacing one custom resource must replace another even without an infrastructure dependency. Relationships are transitive and may be mutual. Use `replacement_trigger` when replacement should follow an arbitrary value change.

Resource hooks are available in Go, Node.js, Python, and PCL. Delete hooks require the program during destroy; error hooks receive provider failures and can drive retries. A successful PCL `onError` hook retries the failed operation, while a failing after-hook fails the deployment.

An `ignoreChanges` path missing from old state uses the new value instead of failing. Failed registrations now produce faulted outputs, and diffs nested in `Output` values are no longer ignored.

## Quick Reference: Imports and Direct Resources

Import options can be supplied by resource transforms. A resource can be imported and updated in one deployment while retaining its import ID. Import files can include providers, rich values, inputs, and outputs; supplying outputs imports state directly and skips the provider read.

`pulumi do` supports stateful create, delete, patch, and upsert. Use `--resources` to reference existing stack resources and `show-resources` to list their identifiers. Stateful patch overlays inputs on the existing snippet. Outside a project, the command creates a fallback project and stack under `PULUMI_HOME`.

## Quick Reference: Providers and Invokes

Output-form invokes in Go, Node.js, Python, and PCL carry resource dependencies so the engine can defer them while dependencies or remote-component children are being created. During preview, a deferred invoke resolves as unknown. Component-parented invokes inherit providers from the component's `providers` option.

Provider handshakes can supply schema-loader, package-resolver, and mapper service addresses. CLI-launched providers receive the active login through `PULUMI_API` and `PULUMI_ACCESS_TOKEN`. Provider `Configure` and `DiffConfig` require type information, and explicit providers receive `DiffConfig` replacement checks.

## Quick Reference: Language Runtimes

- Python supports native async entrypoints through `pulumi.run`; uv projects may override the environment with `UV_PROJECT_ENVIRONMENT`.
- Go output-form invoke SDKs that pass unresolved arguments into the core SDK require Pulumi SDK v3.255.0 or later.
- Bun is a native Pulumi language runtime, distinct from using Bun only as a Node.js package manager.
- Generated Go programs and SDK modules target Go 1.25; Automation API supports Go 1.26.
- Python supports Python 3.14, with `grpcio>=1.75.1` on that runtime.

Read the component/runtime reference before changing language manifests or regenerating SDKs.

## Decision Rules

- Inspect the installed CLI and SDK versions before using a newly introduced flag, protocol field, or generated-code contract.
- Separate CLI behavior, language SDK behavior, provider protocol behavior, and Pulumi Cloud behavior; a feature may arrive in those layers at different times.
- Preserve safety and secrecy defaults unless the user explicitly authorizes an override.
- When a migration changes persisted state, backend selection, credentials, or secrets providers, preview and verify the destination before removing the source.
- For package or schema work, resolve whether the package is ordinary, parameterized, or extension-parameterized before choosing token names and generation paths.
- For provider work, validate against the exact schema and protocol types in the repository rather than assuming older host or handshake signatures.
