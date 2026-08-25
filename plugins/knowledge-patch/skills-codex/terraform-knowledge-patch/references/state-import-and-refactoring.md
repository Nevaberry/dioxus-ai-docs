# State, Import, and Refactoring

## State compatibility and planning (`terraform-1.7.0`)

Terraform 1.7 writes input validations into state again. If state is shared across minor lines, including through `terraform_remote_state`, readers on 1.3, 1.4, and 1.5 must be at least 1.3.10, 1.4.7, and 1.5.7 respectively. Pre-1.3 and 1.6 or later readers are unaffected.

When a `postcondition` or `prevent_destroy` rule rejects a proposed change, Terraform 1.7 plan output retains both the proposed change and its diagnostic rather than replacing the change with the error.

Terraform 1.9 restores entirely unknown blocks that older plan rendering omitted; 1.9.6 also renders complete changes inside unknown nested blocks (`terraform-1.9.0`). Starting in 1.9.8, `terraform plan` validates provider requirements recorded in state as well as current configuration requirements.

Terraform 1.9.0 through 1.9.3 can run irrelevant variable validations during destroy planning and fail against incomplete state. Terraform 1.9.4 fixes that path.

Terraform 1.10 refresh-only plans containing only output changes are applyable, so applying them records the refreshed outputs (`terraform-1.10.0`). Terraform 1.14.2 prevents a failed resource-instance apply from leaving that instance with empty state (`terraform-1.14.0`).

## Cross-resource-type moves (`terraform-1.8.0`)

A `moved` block can transfer an object between resource types only when the target provider declares a conversion from the source type.

```hcl
moved {
  from = old_service.example
  to   = new_service.example
}
```

Terraform 1.9 can directly move an existing `null_resource` object to `terraform_data` (`terraform-1.9.0-guide`).

```hcl
moved {
  from = null_resource.bootstrap
  to   = terraform_data.bootstrap
}
```

In Terraform 1.10, a resource type that collides with a top-level block or reserved keyword needs the explicit `resource.` prefix in a `moved` address.

```hcl
moved {
  from = resource.data.old_name
  to   = resource.data.new_name
}
```

Terraform 1.9 also accepts the optional `resource.` prefix in target addresses, such as `resource.aws_instance.example`.

## Removed blocks and destroy-time cleanup (`terraform-1.9.0-guide`)

Terraform 1.9 permits destroy-time provisioners in `removed` blocks, preserving cleanup after the original resource declaration is deleted.

```hcl
removed {
  from = null_resource.cleanup

  provisioner "local-exec" {
    when    = destroy
    command = "cleanup-command"
  }
}
```

Terraform 1.9.0 through 1.9.4 skip such provisioners when the removed resource is in a nested module; use 1.9.5 or later.

OpenTofu 1.10 permits `lifecycle` configuration inside a `removed` block, so the replacement declaration can control how remaining instances are treated (`opentofu-1.10.0`).

OpenTofu 1.12 also permits `lifecycle { destroy = false }` on a managed resource, removing its object from state without asking the provider to destroy the remote object (`opentofu-1.12.0`).

```hcl
resource "example_service" "legacy" {
  lifecycle {
    destroy = false
  }
}
```

During a broader destroy, `tofu destroy -suppress-forget-errors` suppresses errors caused by resources being forgotten and exits successfully.

## Import generation and validation

Terraform 1.8 configuration generation for imports recognizes string values containing valid JSON and emits `jsonencode(...)` rather than opaque string literals.

Terraform 1.9 rejects an `import` block that targets a nonexistent module instead of silently ignoring it. Terraform 1.9.7 quotes generated map keys containing whitespace; 1.9.8 quotes every key whose syntax would otherwise be invalid, so use 1.9.8 when arbitrary keys can occur.

Terraform 1.12 import blocks may set provider-defined `identity` instead of `id`; the attributes are mutually exclusive (`terraform-1.12.0`).

```hcl
import {
  to       = example_resource.item
  identity = var.item_identity
}
```

Terraform 1.14 list resources and `terraform query` can discover infrastructure and generate import configuration. Providers can improve generated configuration through the `GenerateResourceConfiguration` RPC; see the CLI reference for query-file syntax and commands.

## Local state paths

Terraform 1.10 deprecates `-state` on `plan`, `apply`, and `refresh`. Configure the path through the local backend instead.

```hcl
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

OpenTofu 1.10 expands `tofu show` with explicit `-state` and `-plan=FILE` forms while retaining the older zero-or-one-positional-argument syntax.

## Write-only arguments (`terraform-1.11.0-guide`)

Provider-declared write-only managed-resource arguments accept ephemeral or ordinary values. Terraform sends them on every operation but never persists or diffs them. Increment the provider-specific stored companion version or trigger argument to make rotation visible.

```hcl
ephemeral "random_password" "db_password" {
  length = 16
}

resource "aws_db_instance" "example" {
  password_wo         = ephemeral.random_password.db_password.result
  password_wo_version = 1
}
```

Provider implementations must follow additional schema and lifecycle contracts described in the Plugin Framework reference.
