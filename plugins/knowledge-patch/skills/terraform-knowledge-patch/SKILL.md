---
name: terraform-knowledge-patch
description: Terraform / OpenTofu current compatibility guidance. Use for Terraform / OpenTofu work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Terraform Knowledge Patch

Baseline: Terraform through 1.6.x, including tests, import and check blocks, HCL, providers, state, modules, workspaces, and the OpenTofu 1.6 fork; covered range: Terraform 1.7–1.15, OpenTofu 1.7–1.12, current Stacks/HCP behavior, and Plugin Framework v1.5–v1.19.

## Reference index

| Reference | Topics |
|---|---|
| [language-and-modules.md](references/language-and-modules.md) | Expressions, functions, validation, sensitivity, ephemeral values, modules, provider configuration |
| [state-import-and-refactoring.md](references/state-import-and-refactoring.md) | State compatibility, removal, moves, imports, identities, plans, locking |
| [backends-encryption-and-security.md](references/backends-encryption-and-security.md) | Backends, authentication, encryption, artifact installation, security and platform boundaries |
| [cli-automation-and-output.md](references/cli-automation-and-output.md) | CLI changes, JSON, console, plan rendering, query, actions, automation flags |
| [testing.md](references/testing.md) | Terraform Test and OpenTofu Test, mocks, overrides, variables, concurrency, cleanup, JUnit |
| [stacks-and-hcp.md](references/stacks-and-hcp.md) | Stacks components and deployments, HCP execution, migration, governance, registries |
| [provider-plugin-framework.md](references/provider-plugin-framework.md) | Provider functions, moves, schema types, ephemeral/write-only/identity/list/action APIs, Go floors |

## Upgrade blockers and deprecations

### S3 backend migrations

- Terraform 1.7 changed the S3 credential search order. Its temporary `use_legacy_workflow = true` escape hatch is deprecated; OpenTofu 1.8 removes that argument entirely.
- Terraform 1.10 removes deprecated flat assume-role attributes: use the `assume_role` block.
- Native S3 lock files use `use_lockfile`. Terraform 1.11 deprecates DynamoDB locking arguments; when both mechanisms are configured on Terraform 1.10, both locks are acquired.
- Terraform 1.15 validates `AWS_USE_FIPS_ENDPOINT` and `AWS_USE_DUALSTACK_ENDPOINT` strictly as `true` or `false`.

### Configuration and state compatibility

- Terraform 1.7 writes input validations into state. Readers on the 1.3, 1.4, or 1.5 lines need at least 1.3.10, 1.4.7, or 1.5.7 respectively; pre-1.3 and 1.6+ readers are unaffected.
- Terraform 1.9 rejects provider version constraints inside `.tftest.hcl`; put them in the main `required_providers` configuration.
- Terraform 1.10 deprecates `-state` on `plan`, `apply`, and `refresh`; configure `backend "local" { path = ... }`.
- Reserved resource type names in Terraform 1.10 `moved` blocks require `resource.<type>.<name>`.
- OpenTofu 1.10's PostgreSQL locking is incompatible with older OpenTofu processes sharing the same database; mixing them risks data loss.
- OpenTofu 1.11 ignores deprecated AzureRM `endpoint`/`ARM_ENDPOINT` and `msi_endpoint`/`ARM_MSI_ENDPOINT`; reinitialize with `tofu init -reconfigure`.

### Platform boundaries

- Terraform 1.12 and OpenTofu 1.10 require Linux kernel 3.2+.
- OpenTofu 1.10 requires macOS 11+, OpenTofu 1.11 requires macOS 12+, and OpenTofu 1.12 is the last planned macOS 12 line.
- Building Terraform 1.14 requires macOS Monterey or later.
- OpenTofu 1.12 deprecates WinRM provisioner connections for removal in 1.13; migrate Windows targets to SSH.

## Ephemeral and write-only data

Terraform 1.10 introduces phase-scoped `ephemeral` resources and `ephemeral = true` variables/outputs. Their values exist only during one operation phase, are not stored in plan or state, and may differ between plan and apply. Provider support is per resource type.

```hcl
ephemeral "aws_secretsmanager_secret_version" "db" {
  secret_id = var.secret_id
}

variable "session_token" {
  type      = string
  ephemeral = true
}
```

Terraform 1.11 adds provider-declared write-only managed-resource arguments. A `_wo` value is sent every operation but produces no diff and is never persisted. Pair it with a stored provider-specific version/trigger argument to make rotation visible.

```hcl
resource "aws_db_instance" "db" {
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = var.password_version
}
```

Unknown ephemeral inputs can defer opening an ephemeral resource until apply. OpenTofu gains ephemeral resources, variables, outputs, and write-only attributes in 1.11. See the language and provider-framework references for mark propagation, partial ephemeral values, schema rules, and lifecycle APIs.

## State removal, moves, and imports

Use declarative removal when the change belongs in reviewable configuration:

```hcl
removed {
  from = aws_instance.example
  lifecycle { destroy = false }
}
```

Terraform 1.7 supports `removed` blocks and `for_each` imports. Terraform 1.8 supports provider-approved cross-resource-type `moved` conversions. Terraform 1.9 adds destroy-time provisioners to `removed`; use 1.9.5+ for nested-module targets. Terraform 1.12 imports can use provider-defined `identity` instead of `id`, but not both.

OpenTofu 1.10 reaches cross-type moves and richer removals. OpenTofu 1.12 also permits dynamic `prevent_destroy` and `lifecycle { destroy = false }` directly on managed resources.

## Dynamic modules and module contracts

Terraform 1.15 permits variables and locals in module `source` and `version`. OpenTofu has supported early-evaluated module and backend inputs since 1.8; values must be available before provider configuration. OpenTofu 1.12 can declare that contract explicitly:

```hcl
variable "module_source" {
  type  = string
  const = true
}
```

Terraform 1.15 and OpenTofu 1.10 allow `deprecated = "..."` on module variables and outputs. Terraform 1.15 also adds output `type` constraints and `convert(value, type)`.

## Expressions and provider functions

- Provider-defined functions use `provider::<name>::<function>(...)` in Terraform 1.8+.
- `templatestring(template, variables)` renders dynamic template text in Terraform 1.9 and OpenTofu 1.7.
- Terraform 1.9 variable validations can refer to other variables, locals, and data sources.
- `element` accepts negative indices in Terraform 1.10 and OpenTofu 1.10; use Terraform 1.10.5+ for tuples.
- `&&` and `||` short-circuit in Terraform 1.12 and OpenTofu 1.10.
- Terraform 1.15 adds `convert`; output blocks can declare a `type`.

## Queries and actions

Terraform 1.14 adds list resources declared in `*.tfquery.hcl`, `terraform query`, optional generated imports, and offline `terraform validate -query`. Terraform 1.15 extends `terraform fmt` to query files.

Providers can also expose top-level actions for imperative operations. Actions can be lifecycle-triggered or invoked explicitly with `-invoke`; Terraform 1.14.1 fixes post-create/update ordering.

## Testing essentials

- Terraform 1.7 adds provider mocks, resource/data/module-output overrides, test tfvars, functions in inputs, and references to variables or prior runs.
- Terraform 1.11 adds shared `state_key`, plan-time overrides through `override_during = plan`, and GA `-junit-xml`.
- Terraform 1.12 adds parallel run eligibility and `terraform test -parallelism=n`; Terraform 1.13 parallelizes eligible teardown.
- Terraform 1.13 test files can declare typed external variables and derive file variables from run outputs.
- Terraform 1.15 mock values can call functions. Alpha builds also expose retained test backends, `skip_cleanup`, and `terraform test cleanup`; do not rely on these in stable releases.

## OpenTofu state encryption

OpenTofu 1.7 adds `terraform.encryption` and the overriding/merging `TF_ENCRYPTION` input for local/backend state and saved plans. Back up both state and keys first. Migrate by making the new method primary and the old/plaintext method a fallback; reads try fallbacks, but writes always use the primary method. Remove the fallback only after a successful rewrite.

Available 1.7 key sources include PBKDF2, AWS KMS, GCP KMS, and OpenBao Transit. Remote-state consumers configure decryption separately through `remote_state_data_sources`. OpenTofu 1.10 adds external programs and PBKDF2 chaining; OpenTofu 1.11 adds Azure Key Vault.

## Experimental boundaries

Do not assume prerelease features exist in stable binaries. Terraform 1.13's `-allow-deferral` is alpha-only, as are Terraform 1.15's retained test backends, `skip_cleanup`, and `terraform test cleanup`. Plugin Framework deferred operations and state stores are experimental and carry no compatibility promise until their matching Terraform Core features stabilize.

## Batch coverage

The detailed references incorporate content from every included batch, with overlaps deduplicated into shared topics:

| Terraform | OpenTofu | Other |
|---|---|---|
| `terraform-1.7.0-guide`, `terraform-1.7.0` | `opentofu-1.7.0` | `terraform-stacks-and-hcp` |
| `terraform-1.8.0-guide`, `terraform-1.8.0` | `opentofu-1.8.0` | `provider-plugin-framework` |
| `terraform-1.9.0-guide`, `terraform-1.9.0` | `opentofu-1.9.0` | |
| `terraform-1.10.0-guide`, `terraform-1.10.0` | `opentofu-1.10.0` | |
| `terraform-1.11.0-guide`, `terraform-1.11.0` | `opentofu-1.11.0` | |
| `terraform-1.12.0` | `opentofu-1.12.0` | |
| `terraform-1.13.0` | | |
| `terraform-1.14.0` | | |
| `terraform-1.15.0` | | |
