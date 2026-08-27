# Policy, Security, and Authentication

## Native OIDC login

`pulumi login` exchanges an external identity provider OIDC token for a
short-lived Pulumi Cloud token, avoiding a stored long-lived credential in CI
(batch `native-oidc`). The organization must trust the issuer and authorize the
claims and audience. `--oidc-token` accepts a raw token or `file://` path;
`--oidc-org`, `--oidc-team`, and `--oidc-user` scope the result. Tokens expire in
two hours by default; change this with `--oidc-expiration`.

When a token is supplied, login defaults to Pulumi Cloud and infers organization,
team, and user from JWT claims. OAuth refresh tokens in `credentials.json` cause
a 401 to refresh the access token and retry once.

Logout deletes all backend configuration, removes shared temporary credentials,
and clears the current tokenless backend. `pulumi login --insecure` is retained
in service secrets-manager state for self-signed backends.

## Credential storage and provider login

Set `PULUMI_CREDENTIAL_STORE` to opt into credential encryption with an
operating-system-protected key. `pulumi env provider aws-login`, `azure-login`,
and `gcp-login --export-env-vars` export standard provider SDK variables that
reference login outputs.

## ESC environments

ESC can rotate long-lived credentials such as AWS IAM access keys on demand or
on a schedule. Rotation uses two secrets for consumer transitions, separates
administrator and consumer roles, and can call downstream webhooks.

The ESC GitHub Action injects environment secrets and configuration into a
workflow and can run ESC commands. It can pair with `pulumi/auth-actions` for
OIDC-based Pulumi Cloud authentication. Opening an ESC environment projects
files to disk and exposes their paths through environment variables for every
output format.

`pulumi env open-request` submits the request for approval instead of leaving a
draft; `--reason` supplies approver context. Local policy packs can resolve ESC
environments.

## Policy installation and authoring

`pulumi policy install` installs policy-pack dependencies; policy commands
automatically install missing analyzer plugins. The engine supports severity
overrides and the CLI displays each policy violation's severity.

Go has a Policy as Code SDK; Automation API preview and up options can carry
policy packs. The SDK exposes Pulumi `Context`, executable policy binaries, and
full-stack validation through `policyx.NewStackValidationPolicy` and the
`AnalyzeStack` RPC.

## Policy analysis

`pulumi policy analyze` evaluates a pack against existing stack state.
`--file <stack-export>` analyzes an export without stack selection or backend
login. `pulumi policy new --runtime-options` supplies runtime settings.

Pulumi Insights can apply existing Policy as Code rules to discovered resources,
including resources outside Pulumi IaC. Link Insights Accounts and stacks to
Policy Groups to cover discovered AWS, Azure, OCI, and Kubernetes resources.

## Secret behavior

If an invoke has secret input and its provider lacks secret support, the engine
marks the invoke outputs secret. Node.js and Python resource hooks receive
secrets as `Output` values. Undecryptable stack-reference outputs are elided,
and a missing Python stack-reference output does not raise.

The general CLI secret filter does not consider case-insensitive `true` and
`false` to be filter values. Automatic logs redact property secrets, but
`preview` or `up --show-secrets` emits plaintext into terminal and captured logs.

Reading non-secret stack outputs and running `pulumi about` no longer needs the
passphrase for a passphrase-encrypted stack.

## Tracing

`--otel-traces` writes to a relative file or exports to gRPC, `grpcs://`, or
HTTPS endpoints. Exporters accept header authentication and
`OTEL_RESOURCE_ATTRIBUTES`. Provider OpenTracing spans are bridged into
OpenTelemetry, and `TRACEPARENT` parents CLI spans beneath an existing trace
(behavior spanning `3.214.1-3.228.0` and `3.255.0-3.258.0`).
