# CLI, Automation, and Output

Planning and display behavior, console and inspection commands, structured output, query operations, actions, and automation controls.

## Plan and apply behavior

### Configuration inspection without a plan

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

`tofu show -json -config` emits a machine-readable summary of configuration without first creating a plan, while `-module=DIR` limits it to one module. Configuration JSON now also reports each input variable's type constraint and whether it is required.

```shell
tofu show -json -config
tofu show -json -config -module=./modules/app
```

### Diagnostic and sensitive-output controls

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

Various commands accept `-consolidate-warnings` and `-consolidate-errors` to toggle diagnostic summarization. `-show-sensitive` deliberately unmasks sensitive configuration or state values in `plan`, `apply`, and other commands that display them.

### Exclusion-oriented planning

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

`tofu plan -exclude=ADDRESS` skips the selected configuration or state objects and everything that depends on them, complementing `-target`, which selects what to include.

```shell
tofu plan -exclude=kubernetes_manifest.crds
```

### Large-number plan rendering

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

Starting in 1.7.4, the human-readable plan no longer truncates numbers larger than 2^63.

### Machine-readable plan readiness flags

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

The JSON produced for a saved plan by `terraform show` now includes `applyable`, indicating whether automation should offer to apply it, and `complete`, indicating whether applying it is expected to converge desired and actual state. A false `complete` value means automation should encourage another plan/apply round.

### Planned-state console evaluation

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

`terraform console -plan` calculates a plan and evaluates expressions against the planned new state rather than the prior state; it exposes more values at the cost of slower startup.

### Rejected changes remain visible in plans

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

When a `postcondition` or `prevent_destroy` rejects a proposed resource change, the plan now displays that change alongside the error instead of replacing the change with the error.

### Reusable plan selections and explicit CLI output modes

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

`tofu plan` accepts `-target-file` and `-exclude-file` to load reusable lists of resource-instance addresses, while `-concise` is also available for `tofu apply` to suppress progress-like output. `tofu show` adds explicit `-state` and `-plan=PLANFILE` forms while retaining the old positional form.

```shell
tofu plan -exclude-file=deferred-resources.txt
tofu show -plan=tfplan
```

### Unknown blocks remain visible in plans

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Terraform 1.9 restores entirely unknown blocks to plan output. Terraform 1.9.6 additionally renders complete changes inside unknown nested blocks and fixes related rendering crashes.

## Console and inspection

### Expression and console patch compatibility

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Terraform 1.10.1 prevents `templatefile` crashes with an entirely unknown variables map or marked values. Terraform 1.10.4 fixes empty-map conversion type information and prevents `terraform console` from crashing while printing ephemeral values.

### Installed-module inventory

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

`terraform modules -json` lists every installed module in the working directory and reports whether the current configuration still references it.

### Interactive early evaluation and console input

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

OpenTofu now prompts for input variables needed during early evaluation. `tofu console` also accepts expressions split across lines inside matching brackets or with a backslash-escaped newline.

### Multi-line interactive console input

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

The interactive `terraform console` waits for additional lines when an expression has unclosed parentheses or similar delimiters. This initial support is aimed mainly at pasting multi-line expressions and has limited interactive editing.

### Resource-only graphs by default

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

`terraform graph` now shows only relationships between resources by default. Use `terraform graph -type=plan` to request the more detailed approximation of Terraform Core's planning dependency graph that earlier releases produced by default.

## Machine-readable output and automation

### Automation-visible command behavior

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

Applying a saved plan in a different workspace now fails explicitly, `terraform state show` returns exit code 1 when rendering fails, and an unchanged refresh-only plan no longer spuriously returns a nonzero status. Backend messages from `terraform init -json` and early diagnostics from `terraform validate -json` now remain JSON, while file-level test diagnostics appear in skipped JUnit XML elements.

### Experimental initialization tracing

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

Environment-controlled OpenTelemetry export can send partial `tofu init` traces to an operator-controlled collector. The 1.10 implementation is experimental and covers initialization only, with later commands and richer spans left for future releases.

### Machine-readable initialization

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

`terraform init -json` enables machine-readable JSON output for automation.

### New CLI output modes

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

`tofu plan -concise` suppresses state-refresh log lines. `tofu init -json` and `tofu get -json` provide machine-readable output for automation.

### Simultaneous human and JSON output

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

Commands that support JSON output can use `-json-into=FILENAME` to write the machine-readable stream to a file while retaining normal human-readable output on stdout. The destination can be an IPC path such as a named pipe or `/dev/fd/N` when a companion UI must consume streaming events concurrently.

```shell
tofu plan -json-into=plan-events.json
```

## Query and action operations

### CLI environment and locking changes

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

`OPENTOFU_USER_AGENT`, which fully replaced the default HTTP User-Agent, has been removed. On Unix, `tofu login` now honors `BROWSER` when it names a single command that accepts the URL as its sole argument; `tofu console` adds `-lock=false` and `-lock-timeout=DURATION` for state-lock control.

### Deferred actions remain alpha-only

*Terraform 1.13.0 — batch `terraform-1.13.0`.*

Alpha builds can use `terraform plan -allow-deferral` to permit unknown `count` and `for_each` values in `module`, `resource`, and `data` blocks and to let providers react more flexibly to unknown values. This experiment is not available in stable Terraform 1.13 releases.

### Indexed diffs for same-length lists

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

`terraform plan` now compares old and new lists of the same length by corresponding index and renders a separate diff for each element. Lists whose lengths differ retain the previous whole-list presentation.

### List resources and `terraform query`

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

Terraform 1.14 adds list resources in `*.tfquery.hcl` files for querying and filtering existing infrastructure. `terraform query` executes those operations and can optionally generate import configuration; `terraform validate -query` validates query files offline, and 1.14.4 restores warning rendering in cloud-backed query sessions.

```shell
terraform validate -query
terraform query
```

### Provider-defined actions

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

Providers can expose top-level action blocks for imperative operations outside Terraform's CRUD model, such as invoking a Lambda function or creating a CloudFront invalidation; actions can be lifecycle-triggered or explicitly requested with `-invoke`. Apply output now summarizes invoked actions, while 1.14.1 ensures `after_create` and `after_update` actions run after the resource is applied and 1.14.4 fixes plan graphs for actions in modules without instances.

### Query-file formatting

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

`terraform fmt` now formats `*.tfquery.hcl` files used by Terraform query operations.

