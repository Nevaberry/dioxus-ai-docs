---
name: pulumi-knowledge-patch
description: Pulumi
version: "3.254.0"
license: MIT
metadata:
  author: Nevaberry
---


# Pulumi Knowledge Patch

Use this skill when authoring, upgrading, automating, or operating Pulumi
projects, providers, packages, policy packs, and backends. Inspect `Pulumi.yaml`,
the stack configuration, language manifests and lockfiles, provider schemas, and
the selected backend before applying guidance. Prefer the repository's pinned
CLI and SDK versions, tests, and observed behavior where they differ.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Automation and integrations](references/automation-and-integrations.md) | Automation API, Pulumi Cloud API, remote deployments, MCP, CI, Operator, Neo |
| [CLI and operations](references/cli-and-operations.md) | Engine commands, flags, environment controls, direct-resource work, diagnostics, logs |
| [Components and packages](references/components-and-packages.md) | Cross-language components, YAML components, package sources, registries, publishing |
| [Languages and runtimes](references/languages-and-runtimes.md) | Node.js, Python, Go, Java, .NET, Bun, YAML, testing and toolchains |
| [PCL and conversion](references/pcl-and-conversion.md) | PCL types and forms, HCL, code generation, imports, converters, snippets |
| [Policy, security, and authentication](references/policy-security-and-auth.md) | OIDC, ESC, policy analysis, credentials, secrets, traces |
| [Provider and protocols](references/provider-and-protocols.md) | Provider SDKs, schemas, RPCs, handshakes, invokes, plugin hosts |
| [Resources and engine behavior](references/resources-and-engine.md) | Hooks, replacement, inheritance, imports, refresh, diffs, component semantics |
| [State, imports, and backends](references/state-imports-and-backends.md) | State repair, migration, converters, DIY backends, tags, journaling |

## Breaking Changes and Required Migrations

### Raise Runtime Baselines

- Node.js projects now require Node.js 22 or later. The test matrix includes
  Node.js 26, TypeScript 6 is accepted, and generated TypeScript uses `nodenext`.
- Generated Go programs and SDK modules target Go 1.25; Automation API supports
  Go 1.26. Generated output-form invokes require Pulumi SDK v3.255.0 or later.
- Python supports Python 3.14, which requires `grpcio>=1.75.1`.

### Remove Retired Surfaces

- Replace scripts that call removed `pulumi query` or the removed provider
  `StreamInvoke` RPC.
- Remove `Pulumi.<stack>.deploy.yaml`, its CLI subcommands, `--config-file`, and
  SDK file readers. Manage deployment settings in Pulumi Cloud instead.
- Replace the discontinued `pulumi new --ai` workflow with `pulumi neo`.
- Migrate .NET provider code generation away from
  `pulumi/pkg/v3/codegen/dotnet` to the `pulumi-dotnet` repository package.

### Update Provider and Package Contracts

- Rename `PulumiPlugin.yaml`'s `pulumiVersionRange` to
  `requiredPulumiVersion`; the handshake field `pulumi_version_range` is gone.
- Pass explicit schema loaders during PCL/schema binding and `plugin.Context`
  to Go host boot and resolution APIs. `Configure` and `DiffConfig` require a
  resource type.
- Provider schemas reject whitespace or control characters in names, reserved
  package names `pulumi` and `input`, and modules nested under the index module.
- Prefix local package paths with `./` or `../`; an unprefixed source is no
  longer assumed to be a path. Unqualified package names resolve through the
  Pulumi Cloud Registry.

### Account for Backend and Authentication Changes

- Logout deletes all configuration for the backend and clears shared temporary
  and current tokenless credentials.
- Legacy non-project DIY backend mode now fails instead of warning. The bypass
  variable is `PULUMI_DIY_BACKEND_IGNORE_DEPRECATION_ERROR`.
- Current-stack selection is backend-scoped, so switching backends no longer
  carries a stale stack selection.

## Safe Engine Operations

### Preview Before Overriding Protection

Use resource targets and protection overrides narrowly:

```shell
pulumi preview --exclude '<URN>' --exclude-dependents
pulumi preview --ignore-protect
```

`--ignore-protect` permits protected deletion for that operation. A child may
explicitly set `protect: false` or `retainOnDelete: false` to override inherited
`true`. Use `pulumi state protect`, `taint`, and `untaint` for durable state
changes, and use multi-URN `pulumi state delete` for dependency-safe deletion.

### Run the Program When the Operation Needs It

`refresh` and `destroy` do not normally incorporate changed program code. Add
`--run-program` when code establishes credentials, secrets, dynamic providers,
or hooks needed by the operation. With `--refresh`, `preview` and `up` also
accept it; `PULUMI_RUN_PROGRAM` supplies the global setting.

```shell
pulumi refresh --run-program
PULUMI_RUN_PROGRAM=true pulumi up --refresh
```

### Prefer Structured Output for Automation

`up`, `preview`, `refresh`, `destroy`, and `import` accept `--output json`.
Historical operations can be reduced to the same summary shape:

```shell
pulumi preview --output json
pulumi stack history events --summary
```

Non-UTF-8 bytes appear as `b"<base64>"` in machine output. CLI diagnostics are
written to stderr, and full output is hidden unless `--show-full-output` is set.

## Components and Packages

A component directory needs `PulumiPlugin.yaml` only when it is consumed across
languages. TypeScript exports component classes directly; YAML uses top-level
`components`; Python, Go, .NET, and Java start a component provider host. Use
`pulumi package add` for Git, local, registry, extension, or direct-server
sources, then `pulumi install` to restore entries from `Pulumi.yaml`.

```shell
pulumi package add ./components/secure-s3
pulumi package add --extension <source>
pulumi install
```

An invoke parented to a component inherits its provider from the component's
`providers` option. Keep that parent relationship in generated or handwritten
code so invokes and resources choose providers consistently.

## Resource Lifecycle and Recovery

- `replaceWith` replaces a resource when any referenced resource is replaced;
  relationships may be transitive or mutual. `replacement_trigger` instead
  replaces when an arbitrary value changes.
- Resource hooks cover lifecycle and retry behavior. Destroy operations with
  delete hooks must run the program; a successful `OnError` hook retries the
  failed operation, while a failed after-hook fails the deployment.
- `Output.recover` in Node.js and Python can recover failed output resolution.
  Failed registrations now produce faulted, not unknown, outputs.
- Output-form invokes declare dependencies so the engine delays them until
  resources and remote-component children are ready; preview returns unknown
  while those dependencies are unresolved.

## Authentication, Secrets, and Observability

Use `pulumi login --oidc-token` for short-lived Pulumi Cloud credentials. The
token may be raw or read from `file://`; its organization, team, and user can be
inferred from claims, or narrowed explicitly. The default lifetime is two hours.

Automatic encrypted CLI logging is enabled by default. Property secrets are
redacted, and `pulumi logs ls`, `decrypt`, `rm`, and `share` manage captures.
Treat `--show-secrets` as an explicit disclosure into terminals and logs.

For tracing, `--otel-traces` accepts files plus gRPC, secure gRPC, and HTTPS
endpoints, headers, and `OTEL_RESOURCE_ATTRIBUTES`; `TRACEPARENT` connects CLI
spans to a parent trace.

## Configuration and Environment Controls

- Any command flag can be expressed as `PULUMI_OPTION_*`; for example,
  `PULUMI_OPTION_REFRESH=true`. `PULUMI_STACK` selects the stack.
- `PULUMI_PARALLEL` supplies `--parallel`; `PULUMI_PARALLEL_DIFF` enables
  concurrent diffs, and cgroup CPU limits constrain effective parallelism.
- `up`, `preview`, `destroy`, and `refresh` accept `--override-env` and
  `--skip-config-validation` for one operation.
- `pulumi config set --type` selects a scalar type, `set-all --json` sets bulk
  JSON configuration, and `set --raw` preserves newlines from stdin.

Open the matching reference before changing a protocol, state format, provider
schema, package source, policy pack, or language runtime; those areas have
additional compatibility constraints that do not fit safely in a quick guide.
