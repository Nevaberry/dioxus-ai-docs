# CLI, Automation, and Output

## Graphs, console, and human-readable plans (`terraform-1.7.0`)

`terraform graph` emits a simplified resource-relationship graph by default. Use `terraform graph -type=plan` for the detailed plan-style dependency graph used by older releases.

`terraform console -plan` first calculates a proposed state and evaluates expressions against it rather than only the prior state. Startup is consequently slower. Terraform 1.9 console input waits for additional lines while parentheses or similar delimiters remain open; editing is limited and the feature is primarily intended for pasted multiline expressions (`terraform-1.9.0`).

Terraform 1.7.4 renders integers larger than 2^63 without truncation in human-readable plans. When `postcondition` or `prevent_destroy` rejects a change, plans retain the proposed change alongside its diagnostic. Terraform 1.9 restores entirely unknown blocks in plan output and 1.9.6 adds complete nested-block changes.

## Formatting

Terraform 1.7.2 `fmt` formats test mock-data files named `*.tfmock.hcl`. Terraform 1.15 `fmt` also formats `*.tfquery.hcl` query files.

## Structured output

Terraform 1.8 plan JSON from `terraform show -json` includes:

- `applyable`: whether automation should offer an apply.
- `complete`: whether applying should fully converge. When false, plan another round.

Terraform 1.9 adds `terraform init -json` for structured initialization (`terraform-1.9.0`). Terraform 1.15 adds backend-configuration messages to `init -json`, includes early diagnostics in `validate -json`, adds file-level diagnostics to JUnit XML skipped-test elements, and makes `terraform state show` exit 1 when it cannot render the requested resource (`terraform-1.15.0`).

OpenTofu 1.7 provides structured `tofu init -json` and `tofu get -json` and adopts XDG base-directory locations (`opentofu-1.7.0`). OpenTofu 1.11 adds plan-free configuration inspection:

```shell
tofu show -json -config
tofu show -json -module=./modules/service
```

The configuration JSON includes each variable's type constraint and whether it is required.

OpenTofu 1.12 `-json-into=FILENAME` writes machine-readable JSON to a file while preserving normal human output on standard output. Streaming commands can target an IPC path such as a named pipe.

```shell
tofu plan -json-into=plan.json
```

## Inventory and installation automation

Terraform 1.10 `terraform modules -json` lists installed modules and whether the current configuration references them (`terraform-1.10.0`). Terraform 1.8 `providers lock -enable-plugin-cache` can reuse packages in the global plugin cache; installation and lockfile details are in the backend and security reference.

Terraform 1.13 adds `terraform stacks`; its subcommands are supplied by the installed Stacks plugin, so inspect them dynamically (`terraform-1.13.0`):

```shell
terraform stacks -help
```

Terraform 1.15 initialization skips provider development overrides while installing other dependencies normally.

## Targeting and exclusion

Terraform 1.9 accepts the optional `resource.` prefix in target addresses.

OpenTofu 1.9 `-exclude=ADDRESS` skips selected objects and everything depending on them, complementing `-target`, which selects a dependency closure (`opentofu-1.9.0`).

```shell
tofu plan -exclude=kubernetes_manifest.crds
```

OpenTofu 1.10 adds reusable `-target-file` and `-exclude-file` address lists (`opentofu-1.10.0`).

```shell
tofu plan -target-file=targets.txt
tofu plan -exclude-file=excluded.txt
```

## Concise and sensitive output

OpenTofu 1.7 `tofu plan -concise` omits state-refresh messages. OpenTofu 1.10 `tofu apply -concise` suppresses progress-like messages and emphasizes final results.

OpenTofu 1.9 commands accept `-consolidate-warnings` and `-consolidate-errors` to control diagnostic summarization. `-show-sensitive` reveals normally masked values in commands such as plan and apply; protect all resulting output as secret-bearing.

`TF_STATE_PERSIST_INTERVAL` controls OpenTofu state persistence frequency for long operations, starting in OpenTofu 1.8.

## State and plan selection

Terraform 1.10 deprecates `-state` for `plan`, `apply`, and `refresh`; configure a local backend path instead.

OpenTofu 1.10 accepts explicit state and plan modes while preserving the older positional form:

```shell
tofu show -state
tofu show -plan=plan.tfplan
```

OpenTofu 1.12 console accepts `-lock=false` and `-lock-timeout=DURATION`. Its `destroy -suppress-forget-errors` returns success despite errors caused by objects being forgotten.

## Infrastructure queries (`terraform-1.14.0`)

Declare provider list resources in `*.tfquery.hcl`, then validate query files without accessing remote systems or execute them to find existing infrastructure:

```shell
terraform validate -query
terraform query
```

Query results can generate import configuration. Providers can implement `GenerateResourceConfiguration` for more precise generated resource blocks. Terraform 1.15 extends `fmt` to query files.

## Provider-defined actions

Terraform 1.14 top-level action blocks represent imperative provider operations outside ordinary CRUD. Trigger an action from resource lifecycle or explicitly with `-invoke`. Use 1.14.1 or later so `after_create` and `after_update` actions run after the resource apply, and 1.14.4 or later for actions in modules with no instances.

## Validation and exit behavior

Terraform 1.15.1 deliberately does not validate backend attributes that may arrive through `-backend-config`, reversing the over-broad 1.15.0 behavior. Terraform 1.15.9 does diagnose invalid `list`, `import`, `backend`, and `cloud` blocks in child modules.

OpenTofu 1.12 removes `OPENTOFU_USER_AGENT`. On Unix, `tofu login` uses `BROWSER` only if it names a single command accepting the URL as its only argument.
