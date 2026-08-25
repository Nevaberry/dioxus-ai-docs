# CLI, Automation, and Output

## Planning and graph output

### Graph selection

`terraform graph` emits a simplified resource relationship graph by default.
Use `terraform graph -type=plan` for the earlier detailed plan-style dependency
graph (`terraform-1.7.0`).

### Failed checks remain visible

When `postcondition` or `prevent_destroy` rejects a proposed change, Terraform
shows both the rejected change and its error rather than replacing the change
with only the error (`terraform-1.7.0`).

Entirely unknown blocks remain visible in Terraform plans; 1.9.6 also renders
complete changes within unknown nested blocks (`terraform-1.9.0`). Terraform
1.7.4 renders integers larger than 2^63 without truncating them in
human-readable plans (`terraform-1.7.0`).

### Plan JSON convergence signals

`terraform show -json` plan output includes (`terraform-1.8.0`):

- `applyable`: whether automation should offer an apply.
- `complete`: whether applying is expected to converge fully. When false,
  automation should offer another plan/apply round afterward.

OpenTofu `plan -concise` omits state-refresh log lines
(`opentofu-1.7.0`). OpenTofu `apply -concise` suppresses progress-like output
and emphasizes final results (`opentofu-1.10.0`).

## Console behavior

`terraform console -plan` calculates a proposed state before evaluating
expressions, so it is slower at startup than evaluation against prior state
(`terraform-1.7.0`). Terraform console accepts pasted multiline expressions
when delimiters remain open, although interactive editing is limited
(`terraform-1.9.0`).

OpenTofu console accepts `-lock=false` and `-lock-timeout=DURATION`
(`opentofu-1.12.0`).

```shell
tofu console -lock-timeout=30s
```

## Machine-readable command output

### Terraform JSON

`terraform init -json` provides structured initialization output
(`terraform-1.9.0`). Terraform later emits backend-configuration messages
from that command as JSON, includes early diagnostics in
`terraform validate -json`, and places file-level test diagnostics in JUnit
XML skipped-test elements (`terraform-1.15.0`).

`terraform modules -json` inventories installed modules and says whether each
is referenced by the current configuration (`terraform-1.10.0`).

`terraform state show` exits with status 1 when it cannot render the requested
resource (`terraform-1.15.0`).

### OpenTofu JSON

`tofu init -json` and `tofu get -json` emit structured automation output;
OpenTofu also follows XDG base-directory locations (`opentofu-1.7.0`).

`tofu show -json -config` summarizes the full configuration without a plan,
while `tofu show -json -module=DIR` summarizes one module. Configuration JSON
also reports each input variable's type and whether it is required
(`opentofu-1.11.0`).

```shell
tofu show -json -config
tofu show -json -module=./modules/service
```

`-json-into=FILENAME` writes machine-readable output to a file while normal
human output remains on standard output. Streaming commands may target an IPC
path such as a named pipe (`opentofu-1.12.0`).

```shell
tofu plan -json-into=plan.json
```

## Targeting, exclusion, and explicit inputs

OpenTofu `plan -exclude=ADDRESS` skips the selected objects and everything that
depends on them, complementing `-target`'s selected dependency closure
(`opentofu-1.9.0`). `-target-file` and `-exclude-file` load reusable address
lists from files (`opentofu-1.10.0`).

```shell
tofu plan -exclude=kubernetes_manifest.crds
tofu plan -target-file=targets.txt
tofu plan -exclude-file=excluded.txt
```

OpenTofu `show` accepts explicit `-state` and `-plan=FILE` forms while
retaining the older optional positional argument (`opentofu-1.10.0`).

Terraform accepts the optional `resource.` prefix in target addresses
(`terraform-1.9.0`). The `-state` option on Terraform `plan`, `apply`, and
`refresh` is deprecated; use a local backend path (`terraform-1.10.0`).

## Diagnostics and sensitive output

OpenTofu commands accept `-consolidate-warnings` and
`-consolidate-errors` to control diagnostic summarization
(`opentofu-1.9.0`). `-show-sensitive` reveals values that plan and apply would
normally mask, so treat its output as secret-bearing.

During OpenTofu validation, `plantimestamp()` is unknown starting in 1.9.1;
expressions using it must tolerate unknown results (`opentofu-1.9.0`).

## Queries and generated imports

Terraform list resources are declared in `*.tfquery.hcl`. `terraform query`
executes them and can generate import configuration; `terraform validate
-query` validates query files offline (`terraform-1.14.0`).

```shell
terraform validate -query
terraform query
```

`terraform fmt` also formats query files (`terraform-1.15.0`). Provider-side
configuration generation can use the `GenerateResourceConfiguration` RPC
(`terraform-1.14.0`).

## Provider-defined actions

Top-level Terraform action blocks represent imperative operations outside
normal CRUD. Trigger them from resource lifecycle or explicitly with
`-invoke`. Use 1.14.1 or later so `after_create` and `after_update` execute
after resource apply, and 1.14.4 or later for actions in modules with no
instances (`terraform-1.14.0`).

## Terraform Stacks CLI

`terraform stacks` exposes commands supplied by the installed Stacks plugin;
inspect its actual command set with `terraform stacks -help`
(`terraform-1.13.0`).

Terraform 1.14.2 adds Stacks component-registry resolution. `path.module` and
`path.root` return documented relative paths starting in 1.14.3; use 1.14.5
or later when Stacks validation must resolve relative module paths
(`terraform-1.14.0`). Terraform Stacks also performs input-variable validation
(`terraform-1.15.0`).

HCP-backed `cloud` configuration can address workspaces by HCP resource ID
starting in Terraform 1.9.5 (`terraform-1.9.0`).

## Process and environment behavior

OpenTofu `TF_CLI_ARGS` and command-specific variants parse empty quoted
strings as zero-length arguments (`opentofu-1.11.0`).

`OPENTOFU_USER_AGENT` is removed. On Unix, `tofu login` honors `BROWSER` only
when it names a single command that accepts the URL as its only argument;
unset it to restore platform browser selection (`opentofu-1.12.0`).

`tofu destroy -suppress-forget-errors` suppresses forget-related destroy
errors and exits successfully (`opentofu-1.12.0`).
