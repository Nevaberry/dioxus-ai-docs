# State, Import, and Refactoring

Declarative removal, cross-type moves, import identities, generated configuration, plan/state compatibility, and persistence.

## Removal and resource moves

### Configuration-driven state removal

*Terraform 1.7.0 — batch `terraform-1.7.0-guide`.*

The `removed` block makes state removal declarative, bulk-capable, and visible in a plan. Setting `destroy = false` removes the addressed resource or module from state without destroying the underlying object, providing a workflow-safe alternative to an immediate `terraform state rm`.

```hcl
removed {
  from = aws_instance.example

  lifecycle {
    destroy = false
  }
}
```

### Cross-type moves and richer removals

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

OpenTofu `moved` blocks can now migrate remote objects and state automatically between supported resource types. `removed` blocks now accept `lifecycle` and `provisioner` configuration, bringing destroy behavior and destroy-time cleanup under the declarative removal workflow.

### Destroy-time provisioners in `removed` blocks

*Terraform 1.9.0 — batch `terraform-1.9.0-guide`.*

A `removed` block can now retain provisioners that run while Terraform destroys the removed resource instances. This allows the resource declaration to be deleted without losing required destroy-time cleanup behavior.

```hcl
removed {
  from = aws_instance.example

  lifecycle {
    destroy = true
  }

  provisioner "local-exec" {
    when    = destroy
    command = "./decommission.sh"
  }
}
```

### Direct moves from `null_resource` to `terraform_data`

*Terraform 1.9.0 — batch `terraform-1.9.0-guide`.*

The cross-resource-type refactoring mechanism can now migrate the deprecated `null_resource` type directly to `terraform_data`, preserving the tracked object across its new address instead of requiring manual state removal and import.

```hcl
resource "terraform_data" "bootstrap" {}

moved {
  from = null_resource.bootstrap
  to   = terraform_data.bootstrap
}
```

### Dynamic lifecycle decisions

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

Managed resources can now derive `prevent_destroy` from other values in the same module, allowing a shared module to protect production objects while permitting replacement elsewhere. The new `destroy = false` lifecycle argument instead forgets a managed object without asking its provider to destroy it.

```hcl
resource "example_database" "main" {
  lifecycle {
    prevent_destroy = var.protect_database
  }
}

resource "example_service" "retained" {
  lifecycle {
    destroy = false
  }
}
```

`tofu destroy -suppress-forget-errors` exits successfully when such resources are intentionally forgotten during a destroy operation.

### Nested-module `removed` provisioners require 1.9.5

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

In Terraform 1.9.0 through 1.9.4, provisioners in `removed` blocks were skipped when the resource was in a nested module. Use 1.9.5 or later when relying on destroy-time cleanup in that situation.

### Replacement and failed-apply state fixes

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

Terraform 1.14.1 fixes combinations of `replace_triggered_by` and `-replace` that previously failed to replace some instances. Starting in 1.14.2, an instance apply failure no longer leaves that instance's state empty; 1.14.8 also prevents a relevant-attribute display crash after provider upgrades.

### Reserved resource types in `moved` blocks

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Resource types whose names collide with top-level blocks or reserved keywords must now use the `resource.` address prefix inside `moved` blocks, in the form `resource.<type>.<name>`.

## Import and generated configuration

### `for_each` in import blocks

*Terraform 1.7.0 — batch `terraform-1.7.0-guide`.*

An `import` block can expand over a collection, including across module instances, instead of requiring one block per resource instance.

```hcl
import {
  for_each = local.buckets
  to       = aws_s3_bucket.example[each.key]
  id       = each.value
}
```

### Generated import configuration uses `jsonencode`

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

When import-driven configuration generation encounters a string containing valid JSON, Terraform now emits a `jsonencode(...)` call instead of one quoted string. The generated structure is easier to read and to generalize by replacing individual values with expressions.

### Generated map-key escaping

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Configuration generation in 1.9.7 quotes map keys containing whitespace, and 1.9.8 extends quoting to all keys that would otherwise be invalid syntax.

### Import iteration cannot depend on its target

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

A `for_each` expression in an `import` block may not reference the resource being imported, so its collection must come from independent inputs.

### Import-block validation and destroy behavior

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Import blocks that point into nonexistent modules now raise an error instead of being silently ignored, so they must be fixed or removed during upgrade. An import block also no longer blocks a destroy when its target object has already been deleted.

### Provider-defined import identities

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

An `import` block can use the new `identity` attribute to identify a resource by provider-defined attributes instead of a single `id`; `identity` and `id` are mutually exclusive.

### Provider-generated import configuration

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

The new `GenerateResourceConfiguration` RPC lets providers produce more precise configuration during import. Starting in 1.14.1, its protocol request includes state information for generators that need it.

### Simpler generated primitive strings

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Configuration generation with `plan -generate-config-out` now simplifies string attributes that contain primitive values such as numbers or booleans.

### Workspace import and OSS proxy behavior

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

`terraform import` now retrieves all workspace variables, including inherited variable-set values that the workspace does not override. OSS backend operations now use the backend's proxy support instead of bypassing it.

## State and plan behavior

### Applyable refresh-only output changes

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

A refresh-only plan whose only changes are to outputs is now applyable, allowing those refreshed output values to be recorded without an unrelated resource change.

### Configurable state persistence interval

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

`TF_STATE_PERSIST_INTERVAL` configures the interval at which OpenTofu persists state, allowing operators to tune state-write cadence for long-running operations.

### Destroy-path behavior across the 1.9 line

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

OpenTofu skips import-block processing during `tofu destroy` and correctly handles `create_before_destroy` replacements when refresh is disabled. Starting in 1.9.4, variable validations no longer interfere with destroy operations.

### Local state CLI migration

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

The `-state` flag is deprecated for `terraform plan`, `apply`, and `refresh`. Configure the `path` attribute in a `local` backend instead.

### Local-state crash behavior

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

Local state writes now follow the state-manager persistence contract instead of persisting every intermediate write. This improves large-state performance, but a hard crash during apply may no longer leave an in-progress local state file.

### Optional `resource.` address prefix

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Address targets now correctly accept the optional `resource.` prefix, such as `resource.aws_instance.web`.

### Refactoring across resource types

*Terraform 1.8.0 — batch `terraform-1.8.0-guide`.*

Terraform 1.8 extends `moved` blocks to changes between resource types, including cross-provider moves, but only when the provider declares support for the particular conversion. This replaces the previous remove-from-state, configuration update, and re-import sequence for supported resources.

```hcl
resource "myprovider_new_resource_type" "example" {
  # resource attributes
}

moved {
  from = myprovider_old_resource_type.example
  to   = myprovider_new_resource_type.example
}
```

### State compatibility after restoring input validations

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

Terraform 1.7 writes input validations into state again. For cross-minor state readers such as `terraform_remote_state`, use at least 1.3.10, 1.4.7, or 1.5.7 on those respective series; releases before 1.3 and releases from 1.6 onward are unaffected.

### State migration interoperability

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

`tofu show` and `tofu state show` can read affected state files whose provider addresses refer to the Terraform Registry, avoiding an inspection failure during migration.

