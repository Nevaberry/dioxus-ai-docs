# State, Import, and Refactoring

## State compatibility and persistence

Terraform writes input validations into state (`terraform-1.7.0`). When state
is shared across minor lines, including through `terraform_remote_state`, use
at least these reader releases:

| Reader line | Minimum reader |
| --- | --- |
| 1.3 | 1.3.10 |
| 1.4 | 1.4.7 |
| 1.5 | 1.5.7 |

Readers before 1.3 and readers on 1.6 or later are unaffected.

OpenTofu's `TF_STATE_PERSIST_INTERVAL` controls persistence cadence during
long operations (`opentofu-1.8.0`).

A refresh-only Terraform plan containing only output changes is applyable, so
applying it can record refreshed output values (`terraform-1.10.0`). Terraform
1.14.2 also prevents an apply failure for a resource instance from leaving
that instance's state empty (`terraform-1.14.0`).

## Address moves

### Provider-approved type conversions

A Terraform `moved` block can transfer an object between different resource
types only when the target provider supplies the conversion
(`terraform-1.8.0`). Terraform can directly move `null_resource` state to
`terraform_data` (`terraform-1.9.0-guide`).

```hcl
moved {
  from = null_resource.bootstrap
  to   = terraform_data.bootstrap
}
```

Resource types whose names collide with top-level blocks or reserved words
need the `resource.` prefix in `moved` addresses (`terraform-1.10.0`). The
optional prefix is also accepted in Terraform target addresses
(`terraform-1.9.0`).

```hcl
moved {
  from = resource.data.old_name
  to   = resource.data.new_name
}
```

OpenTofu `replace_triggered_by` now replaces a resource when the referenced
resource is itself being replaced, not only when it is updated
(`opentofu-1.12.0`).

## Declarative removal and forgetting

Terraform `removed` blocks can retain destroy-time provisioners after the
original resource declaration is deleted (`terraform-1.9.0-guide`). Use
Terraform 1.9.5 or later when the target is in a nested module; 1.9.0 through
1.9.4 skip that provisioner path (`terraform-1.9.0`).

```hcl
removed {
  from = null_resource.cleanup

  provisioner "local-exec" {
    when    = destroy
    command = "cleanup-command"
  }
}
```

OpenTofu permits lifecycle configuration in `removed` blocks
(`opentofu-1.10.0`). It also permits `lifecycle { destroy = false }` directly
on a managed resource to remove the object from state without asking its
provider to destroy the remote object (`opentofu-1.12.0`).

```hcl
resource "example_service" "legacy" {
  lifecycle {
    destroy = false
  }
}
```

`tofu destroy -suppress-forget-errors` suppresses errors caused by resources
being forgotten during destruction and exits successfully
(`opentofu-1.12.0`).

## Imports and generated configuration

### Import target validation

Terraform rejects an import block targeting a nonexistent module rather than
silently ignoring it (`terraform-1.9.0`). Correct or remove such a block
before upgrading.

### Import by provider identity

Terraform import blocks can use provider-defined `identity` in place of `id`;
the two attributes are mutually exclusive (`terraform-1.12.0`).

```hcl
import {
  to       = example_resource.item
  identity = var.item_identity
}
```

Provider implementations must handle identity lifecycle and both identity and
legacy ID import forms; see the Plugin Framework reference.

### Generated configuration fidelity

Terraform import configuration generation recognizes strings containing
valid JSON and emits `jsonencode(...)` rather than opaque string literals
(`terraform-1.8.0`). Terraform 1.9.7 quotes generated map keys containing
whitespace, while 1.9.8 quotes every key that would otherwise be invalid; use
1.9.8 when generated configuration can contain arbitrary keys
(`terraform-1.9.0`).

Terraform list resources in `*.tfquery.hcl` can query infrastructure and
generate import configuration. Providers can refine generation through the
`GenerateResourceConfiguration` RPC (`terraform-1.14.0`).

## Plan and state diagnostics

- Terraform plans retain entirely unknown blocks in rendered output; 1.9.6
  also shows complete changes inside unknown nested blocks
  (`terraform-1.9.0`).
- Starting in 1.9.8, `terraform plan` validates provider requirements recorded
  in state as well as the current configuration (`terraform-1.9.0`).
- Terraform 1.15.9 validates invalid `import` blocks in child modules and can
  therefore diagnose configuration that previously passed
  (`terraform-1.15.9`).

## PostgreSQL backend lock compatibility

OpenTofu's newer PostgreSQL backend uses finer-grained locks and accepts
`table_name` and `index_name` to isolate multiple states. Do not share the
same database between processes on the newer locking implementation and older
OpenTofu processes: incompatible locks can permit conflicting writes and data
loss (`opentofu-1.10.0`).
