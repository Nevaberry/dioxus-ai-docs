# Automation and Integrations

## Automation API operation control

Inline Go, Node.js, and Python programs can request run-program behavior for
refresh and destroy. Node.js adds `previewDestroy`; Python preview exposes JSON
output and command options can use `on_error` to consume stderr incrementally.
These operation controls arrived in batch `3.182.0-3.198.0`.

The generated low-level Node.js interface exposes `cancel`. Generated Node.js,
Python, and Go Automation APIs expose import; Go preview-refresh and refresh can
pass `--import-pending-creates`. Python's `preview_refresh` and
`preview_destroy` accept a `program` argument, and the Python SDK has native
async entrypoints through `pulumi.run`.

Automation API project settings may omit a runtime. Go Automation API supports
Go 1.26.

## Pulumi Cloud API

Use `pulumi api <op-or-path>` to call any Pulumi Cloud API operation or raw path.
It handles fields, headers, input/body data, path templates, content negotiation,
and dry runs. `list` and `describe` expose the OpenAPI surface. `--paginate`
combines cursor pages into one JSON envelope, `--emit-events` reports pagination
on stderr, and the final result selector is `--output`, not `--format` (batch
`3.229.0-3.248.0`).

## Remote deployments

Failed `pulumi up --remote` and `pulumi deployment run` operations return a
nonzero exit code. Remote execution no longer needs a local `Pulumi.yaml`, and
new projects install packages required by generated programs (batch
`3.255.0-3.258.0`).

## Neo workflows

`pulumi neo` is available without an experimental switch. Its assistant runs
approved shell and filesystem tools locally in the working directory while the
conversation is backed by Pulumi Console. It supports non-interactive `--print`,
approval and permission modes, and `--disable-integrations`. Plan mode must be
selected before the first message and blocks writes, updates, and pull-request
creation until approval.

`pulumi neo acp` serves Neo over stdio using Agent Client Protocol. Read-only and
plan modes are session options. `pulumi neo resume` restores history, while
`--debug-update` and `--debug-preview` investigate failed operations. The old
Pulumi AI choice and the `pulumi new --ai` and `--language` flags were removed;
Neo is the supported replacement.

## MCP integration

The Pulumi MCP Server exposes CLI and Registry capabilities to compatible
clients, including registry resource information and infrastructure operations
(batch `release-notes-117`).

## CI and controllers

The GitLab integration supports multiple Pulumi jobs in parallel in one pipeline
on SaaS and self-managed installations. CI/CD-variable authentication provides a
tokenless path without personal access tokens.

Pulumi Kubernetes Operator 2.0 provides automatic retries for temporary
failures, fine-grained refresh control, idempotent updates, and revised
reconciliation and CRD management.

## Project bootstrapping

Projects can omit a runtime in CLI operations. `pulumi project new -y` creates a
minimal project without a template, `pulumi new` aliases `pulumi project new`,
and the `pulumi` package makes commands available through `npx`.

```shell
npx pulumi preview
```
