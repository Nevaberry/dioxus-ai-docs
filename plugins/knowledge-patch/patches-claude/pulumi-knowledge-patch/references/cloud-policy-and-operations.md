# Cloud, Policy, and Operations

Use this reference for Pulumi Cloud, ESC, authentication, CI/CD integrations, policy enforcement, backends, credentials, and remote operations.

## MCP integration (batch `release-notes-117`)

Pulumi's MCP Server exposes CLI and Registry capabilities to compatible coding assistants, including resource lookup and infrastructure-management operations from editor workflows.

## GitLab integration (batch `release-notes-117`)

The GitLab integration supports multiple Pulumi jobs running in parallel within one pipeline on GitLab SaaS and self-managed installations. Its CI/CD-variable authentication avoids personal access tokens.

## Kubernetes Operator 2.0 (batch `release-notes-117`)

Pulumi Kubernetes Operator 2.0 is generally available. It adds automatic retry for transient failures, fine-grained refresh control, idempotent updates, and revised reconciliation and CRD management.

## ESC credential rotation (batch `release-notes-117`)

ESC can rotate long-lived credentials such as AWS IAM user access keys on a schedule or on demand. Rotation is declared in ESC environments, uses two secrets for smooth consumer transitions, supports separate administrator and consumer roles, and can invoke downstream webhooks.

## ESC GitHub Action (batch `release-notes-117`)

The ESC GitHub Action injects secrets and configuration from ESC environments and can run ESC commands in a workflow. Pair it with `pulumi/auth-actions` for OIDC-based tokenless Pulumi Cloud authentication.

## Policies for discovered resources (batch `release-notes-117`)

Pulumi Insights can apply existing Policy as Code rules to discovered resources, including infrastructure not managed by Pulumi IaC. Link Insights Accounts to Policy Groups alongside stacks to cover discovered AWS, Azure, OCI, and Kubernetes resources.

## Native OIDC login (batch `native-oidc`)

`pulumi login` exchanges an external identity provider's OIDC token for a short-lived Pulumi Cloud access token. The default lifetime is two hours; use `--oidc-expiration` to change it. The organization must trust the issuer and define authorization policies for claims and audience.

`--oidc-token` accepts a raw token or a `file://` path. Use `--oidc-org` for the organization and optionally narrow the identity with `--oidc-team` or `--oidc-user`.

## DIY backend stack tags (batch `3.199.0-3.214.0`)

S3, Azure Blob, Google Cloud Storage, PostgreSQL, and local DIY backends support stack-tag CRUD, automatic system tags, and tag-filtered stack lists. Tags live as versioned JSON in separate `.pulumi-tags` files beside checkpoints. Existing untagged stacks remain valid, and deleting a stack removes its tag file.

```shell
pulumi stack tag set environment production
pulumi stack ls --tag-filter environment=production
```

## Policy severity overrides (batch `3.199.0-3.214.0`)

The engine supports overriding policy-violation severity, and the CLI displays the effective severity for each violation.

## OIDC defaults and claim inference (batch `3.214.1-3.228.0`)

When given an OIDC token, login defaults to Pulumi Cloud and infers organization, team, and user from JWT claims. Explicit scoping flags remain available when inference should be constrained.

## Policy installation (batch `3.214.1-3.228.0`)

`pulumi policy install` installs policy-pack dependencies. Policy operations also install missing policy analyzer plugins automatically.

## DIY backend storage and deprecation (batch `3.214.1-3.228.0`)

DIY backends support zstd-compressed state. This batch began deprecating the legacy non-project operating mode; later behavior enforces that deprecation as an error.

## Service backend recovery and secrets managers (batch `3.214.1-3.228.0`)

The service backend repairs snapshot-integrity problems automatically while emitting an error event for diagnosis. When imported state refers to the service-backed secrets manager, `pulumi stack import` reconfigures it for the target stack when necessary.

Refreshing a stack's configuration includes the environments imported by the stack.

## Direct Cloud API access (batch `3.229.0-3.248.0`)

Use `pulumi api` to invoke Pulumi Cloud OpenAPI operations or paths directly. Inspect the surface with `list` and `describe`; use `--paginate` for combined cursor results and `--emit-events` for progress on stderr. Authentication follows the active Pulumi Cloud login.

## OAuth refresh and destructive logout (batch `3.229.0-3.248.0`)

If `credentials.json` contains an OAuth refresh token, a 401 triggers an automatic access-token refresh and one retry.

Logout now removes all backend configuration, shared temporary agent credentials, and the current tokenless backend. Treat it as a breaking, local-state-changing operation rather than only token deletion.

## Existing-state policy analysis (batch `3.229.0-3.248.0`)

`pulumi policy analyze` evaluates a policy pack against existing stack state. Local policy packs can resolve ESC environments.

## Automatic encrypted logs (batch `3.249.0-3.254.0`)

Encrypted command logging is enabled by default. Property-value secrets are redacted, and `pulumi logs share` shares a selected capture with Pulumi. Review a log before sharing because command output can contain data that is not represented as a Pulumi property secret.

## Stack migration between backends (batch `3.249.0-3.254.0`)

`pulumi stack migrate` moves a stack from another backend into the currently logged-in backend. It re-encrypts configuration secrets and stack state under the destination backend's secrets provider.

Confirm the destination login, organization, stack identity, and secrets provider before migration. Validate the migrated stack before removing or abandoning the source.

## File-based policy analysis (batch `3.249.0-3.254.0`)

`pulumi policy analyze --file <stack-export>` evaluates exported state without selecting a stack or logging into a backend. `pulumi policy new --runtime-options` supplies policy runtime settings. Policy and policy-group lists support `--output <format>`.

## ESC change requests (batch `3.249.0-3.254.0`)

`pulumi env open-request` submits a change request for approval instead of leaving it as a draft. Use `--reason` to give approvers context.

## ESC file projection (batch `3.255.0-3.258.0`)

Opening an ESC environment projects files to disk and exposes their paths through environment variables for every output format. Treat the projected paths and file lifetimes as secret-bearing runtime material.

## Provider-login environment exports (batch `3.255.0-3.258.0`)

`pulumi env provider aws-login`, `azure-login`, and `gcp-login` accept `--export-env-vars`. This additionally populates the standard provider SDK environment variables with references to the login outputs.

## Remote operation failures (batch `3.255.0-3.258.0`)

Failed `pulumi up --remote` and `pulumi deployment run` operations return a nonzero process exit. Remote updates no longer require a local `Pulumi.yaml`, so automation should rely on the exit status and remote operation result rather than local-project presence.

## Backend selection and compatibility (batch `3.255.0-3.258.0`)

Current-stack selection is scoped to the active backend; switching backends does not reuse a stale selection from another backend. `pulumi login --insecure` is preserved in service secrets-manager state for self-signed backends. S3-compatible DIY backends using a custom endpoint default checksum calculation to `when_required`.

## DIY backend deprecation enforcement (batch `3.255.0-3.258.0`)

The legacy DIY-backend deprecation warning is now an error. The temporary bypass variable is `PULUMI_DIY_BACKEND_IGNORE_DEPRECATION_ERROR`; the older `_WARNING` name no longer applies.

## OS-protected credentials (batch `3.255.0-3.258.0`)

Set `PULUMI_CREDENTIAL_STORE` to opt into stored Pulumi credentials encrypted with a key protected by the operating system.

## Executable and full-stack policy checks (batch `3.255.0-3.258.0`)

Policy packs can point directly to executable binaries rather than only script directories. The Go policy SDK adds `policyx.NewStackValidationPolicy` and supports the analyzer `AnalyzeStack` RPC for validating an entire stack.
