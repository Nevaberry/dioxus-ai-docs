# Language, modules, and lifecycle

## Early evaluation for modules and backends (`1.8.0`)

OpenTofu can evaluate variables and locals early enough for module `source` and `version` arguments and backend configuration.

```hcl
variable "module_version" {
  default = "5.1.0"
}

locals {
  state_key = "production.tfstate"
}

terraform {
  backend "s3" {
    key = local.state_key
  }
}

module "network" {
  source  = "example/network/aws"
  version = var.module_version
}
```

Keep early expressions limited to values available during initialization. They cannot depend on state or provider-defined functions, and 1.8 does not add dynamic provider configuration.

OpenTofu 1.9 prompts for variables needed during early evaluation. It prohibits sensitive values in backend configuration and module source locations because initialization or module installation would expose them.

OpenTofu 1.8.3 offers `TOFU_ENABLE_STATIC_SENSITIVE=1` to opt into sensitive marking for variables used in module sources, module versions, and backends. Earlier 1.8 behavior warns for compatibility; sensitive marking becomes the default in 1.9.

## Static initialization contracts (`1.12.0`)

Declare `const = true` when an input must be compatible with static evaluation:

```hcl
variable "module_source" {
  type  = string
  const = true
}
```

The `language` configuration block separates OpenTofu version constraints from constraints on other software. A module containing it requires OpenTofu 1.12+, so do not adopt it when older OpenTofu compatibility is required.

## OpenTofu-specific source files

An OpenTofu-specific `.tofu` file masks the identically named `.tf` file. If both `main.tofu` and `main.tf` exist, OpenTofu ignores `main.tf`. Module authors can keep a Terraform-compatible fallback in `.tf` while placing OpenTofu-only syntax in the matching `.tofu` file.

## Module interface contracts (`1.10.0`)

Module authors can mark input variables and output values as deprecated. Consumers receive warnings at use sites.

A module `version = null` is equivalent to omitting the version argument.

## Iterated provider configurations (`1.9.0`)

An aliased provider configuration can use `for_each`. `each.key` configures each instance, and resources or modules can select different instances.

```hcl
provider "aws" {
  alias    = "by_region"
  for_each = var.aws_regions

  region = each.key
}
```

Dynamic instance keys used in a resource `provider` selection or a module `providers` map are automatically converted to strings from 1.10.

## Provider-defined and built-in functions

Since `1.7.0`, providers can expose functions, including functions selected dynamically from provider configuration. Call them as:

```hcl
provider::<provider_name>::<function>(arguments)
```

OpenTofu 1.10 adds functions to the built-in `terraform` provider for encoding and decoding `.tfvars` data and for encoding arbitrary values as OpenTofu expression syntax.

## Recursive templates

`templatefile` can recursively call `templatefile` from 1.7. The default maximum call depth is 1024, enabling composition of file-backed templates without an external preprocessing step.

## Short-circuit logic and indexing

From 1.10, `&&` and `||` short-circuit. A skipped right operand is not evaluated, so a guarded null dereference does not fail.

```hcl
locals {
  enabled = var.settings != null && var.settings.enabled
  last    = element(var.items, -1)
}
```

`element` also extends its wrapping behavior to negative indices; `-1` selects the final item.

## Sensitivity and unknown values (`1.11.0`, `1.12.0`)

`issensitive(unknown)` now returns unknown. If that result feeds plan-time-only contexts such as `count` or `for_each`, ensure its argument is known.

Comparing a complex value with `null` yields a sensitive boolean only when the whole value is sensitive, not merely when a nested attribute is sensitive. Such comparisons can feed plan-time contexts such as `lifecycle.enabled`.

## Object, regex, fileset, and YAML behavior

From 1.11:

- An object constructor passed to an object-typed input warns about undeclared attribute names.
- `regex` and `regexall` accept long Unicode property names such as `\p{Letter}`.
- `fileset` matches literal metacharacters escaped with backslashes.

From 1.12, `yamldecode` accepts a YAML `<<` merge tag whose value is a sequence of mappings, not just one mapping.

## Ephemeral values and write-only attributes (`1.11.0`)

Input variables, output values, and provider-defined resources can be ephemeral. Their values live only in memory during one operation phase and are never persisted in plans or state.

Providers can expose write-only managed-resource attributes, allowing a secret such as an initial password or private key to be sent without retaining a copy. Both ephemeral resource types and write-only attributes require explicit provider support.

Apply-time input values can configure state and plan encryption. Every non-ephemeral apply-time input must equal the value recorded during planning.

## Conditional resources and modules

Use `lifecycle.enabled` for a resource or module that should have either zero or one instance, instead of encoding the condition with `count`.

```hcl
module "servers" {
  source  = "./app-cluster"
  servers = 5

  lifecycle {
    enabled = var.enable_cluster
  }
}
```

Nesting avoids colliding with a resource argument or module input also named `enabled`. From 1.11.4, a module containing local provider configurations rejects `enabled`, matching restrictions on `count`, `for_each`, and `depends_on`.

## Dynamic destruction lifecycle (`1.12.0`)

`lifecycle.prevent_destroy` can refer to symbols in the same module, including input variables. A shared module can vary protection by caller.

A managed resource can set `lifecycle.destroy = false` to remove the object from state without asking the provider to destroy it.

```hcl
resource "example_database" "main" {
  lifecycle {
    prevent_destroy = var.protect_database
  }
}

resource "example_object" "detached" {
  lifecycle {
    destroy = false
  }
}
```

Use 1.12.4 or later when saving a plan that might replace a resource with `destroy = false`; earlier 1.12 builds fail in that case.

## Moves and removals (`1.10.0`)

`moved` blocks can move remote objects between different resource types while the provider migrates their state.

`removed` blocks can include `lifecycle` and `provisioner` configuration to control how remaining instances are treated.

## Provider-defined import identities

In 1.12, an `import` block can use an `identity` object matching the provider-defined identity schema for the resource type, rather than only a plain `id` string.

## Replacement propagation

`replace_triggered_by` in 1.12 replaces its resource when the referenced resource is itself being replaced. Previously the trigger fired only when the reference was updated.

## Provider deprecations

References to provider schema attributes or blocks marked deprecated produce warnings in 1.12. The `-deprecation=` CLI option can disable these diagnostics when necessary, but migration is preferable.
