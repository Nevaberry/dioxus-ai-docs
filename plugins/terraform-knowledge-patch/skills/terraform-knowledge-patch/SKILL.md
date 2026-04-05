---
name: terraform-knowledge-patch
description: "Terraform 1.10-1.15 and OpenTofu divergences including ephemeral resources, write-only attributes, S3 native state locking, import by identity, short-circuit operators, Stacks CLI, terraform query, actions blocks, deprecated attribute, convert() function, and OpenTofu-specific features (state encryption, provider for_each, lifecycle enabled). Use when writing Terraform/OpenTofu configurations targeting recent versions."
license: MIT
metadata:
  author: Nevaberry
  version: "1.15"
---

# Terraform Knowledge Patch

Post-training knowledge for Terraform 1.10-1.15 and OpenTofu divergences.
Assumes familiarity with Terraform through 1.9 including HCL, providers, state management,
modules, workspaces, `removed` block, test framework (`mock_provider`, `override_resource`),
`import` with `for_each`, provider-defined functions (`provider::aws::fn()`), `issensitive()`,
`templatestring()`, cross-object variable validation. OpenTofu fork known through 1.6.

## References

- [Ephemeral Resources & Write-Only Attributes](references/ephemeral-write-only.md) — Ephemeral block type, write-only `_wo` attributes, `ephemeralasnull()`, secrets management patterns
- [State & Backends](references/state-backends.md) — S3 native state locking via `use_lockfile`, DynamoDB deprecation
- [Import, Query & Actions](references/import-query-actions.md) — Import by identity, `terraform query` with `.tfquery.hcl`, actions block, `-invoke` flag
- [Stacks](references/stacks.md) — `terraform stacks` CLI, `.tfcomponent.hcl`, `.tfdeploy.hcl`, HCP Terraform multi-environment deployments
- [Testing](references/testing.md) — Test parallelism (`-parallelism=n`), test variable definitions in `.tftest.hcl`
- [Language Features](references/language-features.md) — Short-circuit `&&`/`||`, `convert()`, `deprecated` attribute, output type constraints, dynamic module `source`/`version`
- [OpenTofu Divergences](references/opentofu-divergences.md) — State/plan encryption, `.tofu` file extension, early evaluation, provider `for_each`, `lifecycle { enabled }`, `-exclude` flag, OCI registry support

## Quick Reference — Key Features by Version

| Version | Feature | Details |
|---|---|---|
| 1.10 | Ephemeral resources | `ephemeral` block — never persisted to state |
| 1.10 | `ephemeralasnull()` | Bridge ephemeral values to non-ephemeral contexts |
| 1.11 | Write-only attributes | `_wo` suffix attrs, never stored in state |
| 1.11 | S3 native locking | `use_lockfile = true` replaces DynamoDB |
| 1.12 | Import by identity | Structured `identity {}` instead of opaque `id` string |
| 1.12 | Short-circuit `&&`/`||` | Right side not evaluated if result determined |
| 1.12 | Test parallelism | `-parallelism=n` for `terraform test` |
| 1.13 | Stacks CLI | Multi-environment deployments via HCP Terraform |
| 1.13 | Test variable definitions | `variable` blocks in `.tftest.hcl` files |
| 1.14 | `terraform query` | Query infrastructure via `.tfquery.hcl` without state |
| 1.14 | Actions block | Imperative operations outside CRUD lifecycle |
| 1.15 | `deprecated` attribute | Deprecation warnings on variables and outputs |
| 1.15 | `convert()` function | Explicit type conversion |
| 1.15 | Dynamic module source | Variables/locals in module `source` and `version` |
| 1.15 | Output type constraints | `type` attribute on output blocks |

## Ephemeral Resources (1.10)

New `ephemeral` block type — resources never persisted to state, re-read every plan/apply:

```hcl
ephemeral "aws_secretsmanager_secret_version" "db_pass" {
  secret_id = "my-db-password"
}

resource "aws_db_instance" "main" {
  password_wo         = ephemeral.aws_secretsmanager_secret_version.db_pass.secret_string
  password_wo_version = 1
}
```

Variables and outputs can be `ephemeral = true`. Ephemeral values can only flow to contexts that accept them (provider configs, write-only attributes, other ephemeral outputs). Use `ephemeralasnull(value)` to bridge to non-ephemeral contexts.

## Write-Only Attributes (1.11)

Provider-defined attributes that accept values but are never stored in state. Named with `_wo` suffix, paired with `_wo_version` integer. Increment version to trigger rotation:

```hcl
resource "aws_db_instance" "main" {
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = 1  # bump to rotate
}
```

## Short-Circuit Operators (1.12)

`&&` and `||` now short-circuit. Safe to write:

```hcl
var.map != null && var.map["key"] == "value"
```

## S3 Native State Locking (1.11)

```hcl
terraform {
  backend "s3" {
    bucket       = "my-state"
    key          = "terraform.tfstate"
    use_lockfile = true  # no DynamoDB needed
  }
}
```

## Import by Identity (1.12)

`import` blocks support structured `identity` instead of opaque `id` string:

```hcl
import {
  to       = aws_instance.example
  identity = { instance_id = "i-1234567890abcdef0" }
}
```

Provider must implement identity schema.

## `terraform query` (1.14)

Query existing infrastructure via `.tfquery.hcl` files without managing state:

```hcl
# find_instances.tfquery.hcl
list "aws_instance" "all" {
  filter {
    tag    = "Environment"
    values = ["production"]
  }
}
```

Run with `terraform query`. Can generate import configuration from results.

## Actions Block (1.14)

Imperative operations outside CRUD lifecycle:

```hcl
action "invalidate_cache" {
  type = "aws_cloudfront_create_invalidation"
  inputs = {
    distribution_id = aws_cloudfront_distribution.main.id
    paths           = ["/*"]
  }
}
```

Triggered via `-invoke` CLI flag or resource lifecycle hooks.

## Stacks (1.13)

`terraform stacks` for multi-environment deployments (requires HCP Terraform). File types:
- `*.tfcomponent.hcl` — `component` blocks referencing modules
- `*.tfdeploy.hcl` — `deployment` blocks (one per environment/region)

Limits: max 20 deployments, 100 components, 10,000 resources per stack.

## Language Features (1.15)

**`deprecated` attribute** — deprecation warnings on variables and outputs:

```hcl
variable "old_name" {
  type       = string
  deprecated = "Use var.new_name instead"
}
```

**`convert()` function** — explicit type conversion: `convert(value, type)`.

**Dynamic module source** — variables and locals in module `source` and `version`:

```hcl
module "app" {
  source  = "hashicorp/consul/aws"
  version = var.consul_version  # was previously static-only
}
```

**Output type constraints**:

```hcl
output "ids" {
  type  = list(string)
  value = aws_instance.main[*].id
}
```

## OpenTofu Key Differences

| Feature | OpenTofu | Terraform |
|---|---|---|
| State/plan encryption | OT 1.7+ (`encryption {}` block) | Not available |
| `.tofu` file extension | OT 1.8+ (overrides `.tf`) | Not supported |
| Early evaluation in backends | OT 1.8+ | TF 1.15 (partial) |
| Provider `for_each` | OT 1.9+ | Not available |
| `lifecycle { enabled }` | OT 1.11+ | Not available |
| `-exclude` flag | OT 1.9+ | Not available |
| OCI registry support | OT 1.10+ | Not available |
