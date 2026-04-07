---
name: terraform-knowledge-patch
description: "Terraform/OpenTofu changes since training cutoff (latest: TF 1.15 / OT 1.12) — ephemeral values, write-only arguments, cross-object validation, Stacks, resource identity, OpenTofu divergences. Load before working with Terraform or OpenTofu."
license: MIT
version: "1.15.0"
metadata:
  author: Nevaberry
---

# Terraform / OpenTofu Knowledge Patch

Covers Terraform 1.8–1.15 and OpenTofu 1.7–1.12 (April 2024 – March 2026).
Baseline knowledge: Terraform 1.7, OpenTofu 1.6.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Ephemeral values | [references/ephemeral-values.md](references/ephemeral-values.md) | Ephemeral variables, resources, write-only arguments, new functions |
| Variable validation | [references/variable-validation.md](references/variable-validation.md) | Cross-object references in validation blocks |
| Import & identity | [references/import-identity.md](references/import-identity.md) | Resource identity schema, import by identity attributes |
| Terraform Stacks | [references/stacks.md](references/stacks.md) | Component-based multi-environment deployments (HCP Terraform) |
| Terraform Actions | [references/actions.md](references/actions.md) | Day 2 provider-defined operations (TF 1.14 preview) |
| New functions | [references/new-functions.md](references/new-functions.md) | templatestring, ephemeralasnull, terraform.applying |
| OpenTofu divergences | [references/opentofu.md](references/opentofu.md) | enabled meta-argument, destroy=false, const variables, prevent_destroy expressions |

## Quick Reference — What's New

### Ephemeral Values (TF 1.10+, OT 1.11) — Most Important Change

New value category **never persisted** to plan or state. Three constructs:

| Construct | Syntax | Purpose |
|---|---|---|
| Ephemeral variable | `variable "x" { ephemeral = true }` | Accept secrets as input without state storage |
| Ephemeral output | `output "x" { ephemeral = true }` | Pass secrets between modules without state storage |
| Ephemeral resource | `ephemeral "provider_type" "name" { }` | Fetch secrets at plan/apply time, never stored |

Reference via `ephemeral.<type>.<name>.<attribute>`.

Ephemeral resources have an **open/renew/close** lifecycle — they run during every plan and apply, never persisted between runs. If an input references an unknown value, execution defers to apply.

**Critical pattern — secrets in provider config:**
```hcl
ephemeral "aws_secretsmanager_secret_version" "db_master" {
  secret_id = data.aws_db_instance.example.master_user_secret[0].secret_arn
}

locals {
  credentials = jsondecode(ephemeral.aws_secretsmanager_secret_version.db_master.secret_string)
}

provider "postgresql" {
  host     = data.aws_db_instance.example.address
  password = local.credentials["password"]
}
```

### Write-Only Arguments (TF 1.11+, OT 1.11)

Resource attributes that accept ephemeral values and are **never stored in state**. Paired with a `_wo_version` argument to control updates.

```hcl
resource "aws_db_instance" "main" {
  # ...
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = 1  # Increment to trigger password rotation
}
```

Common write-only attributes:

| Resource | Write-only attribute |
|---|---|
| `aws_db_instance` | `password_wo` |
| `aws_rds_cluster` | `master_password_wo` |
| `aws_secretsmanager_secret_version` | `secret_string_wo` |
| `aws_ssm_parameter` | `value_wo` |
| `google_secret_manager_secret_version` | `secret_data_wo` |
| `kubernetes_secret_v1` | `data_wo` |

See [references/ephemeral-values.md](references/ephemeral-values.md) for full examples.

### Cross-Object Variable Validation (TF 1.9)

Validation blocks can now reference **other variables, data sources, and locals** — not just the variable itself:

```hcl
variable "cluster_endpoint" {
  type    = string
  default = ""

  validation {
    condition     = var.create_cluster == false ? length(var.cluster_endpoint) > 0 : true
    error_message = "cluster_endpoint required when create_cluster is false."
  }
}
```

See [references/variable-validation.md](references/variable-validation.md) for details.

### templatestring Function (TF 1.9)

Renders a template from a string value (not a file). Useful for templates from data sources:

```hcl
locals {
  rendered = templatestring(data.http.template.response_body, {
    APP_NAME = var.app_name
    PORT     = var.port
  })
}
```

### Resource Identity for Import (TF 1.12)

Import blocks now support structured identity attributes instead of opaque ID strings:

```hcl
import {
  to = aws_instance.example
  identity = {
    id = "i-1234567890abcdef0"
  }
}
```

See [references/import-identity.md](references/import-identity.md) for details.

### Terraform Stacks (HCP Terraform, GA Sep 2025)

Component-based multi-environment deployments using new file types. Requires HCP Terraform.

```hcl
# main.tfcomponent.hcl
component "networking" {
  source = "./modules/networking"
  inputs = { region = var.region, cidr = var.cidr }
}

component "cluster" {
  source = "./modules/k8s"
  inputs = { vpc_id = component.networking.vpc_id }
}
```

```hcl
# deploy.tfdeploy.hcl
deployment "us-east" {
  inputs = { region = "us-east-1", cidr = "10.0.0.0/16" }
}
deployment "eu-west" {
  inputs = { region = "eu-west-1", cidr = "10.1.0.0/16" }
}
```

Limits: 20 deployments, 100 components, 10k resources per stack. See [references/stacks.md](references/stacks.md).

### Terraform Actions (TF 1.14, Preview)

Day 2 operations defined by providers — triggered before/after resource CRUD or ad hoc via CLI. Codifies operational tasks (Lambda invocations, cache invalidations, Ansible playbooks) alongside infrastructure. See [references/actions.md](references/actions.md).

### New Functions Quick Reference

| Function | Version | Purpose |
|---|---|---|
| `templatestring(str, vars)` | TF 1.9 | Render template from string (not file) |
| `ephemeralasnull(value)` | TF 1.10+ | Convert ephemeral value to non-ephemeral null |
| `terraform.applying` | TF 1.10+ | Returns true during apply, false during plan |

See [references/new-functions.md](references/new-functions.md) for examples.

### OpenTofu Divergences

| Feature | Version | Syntax |
|---|---|---|
| `enabled` meta-argument | OT 1.11 | `lifecycle { enabled = var.create }` |
| `destroy = false` | OT 1.12 | `lifecycle { destroy = false }` |
| `const` variables | OT 1.12 | `variable "x" { const = true }` |
| `prevent_destroy` expressions | OT 1.12 | `lifecycle { prevent_destroy = var.protect }` |

See [references/opentofu.md](references/opentofu.md) for examples.
