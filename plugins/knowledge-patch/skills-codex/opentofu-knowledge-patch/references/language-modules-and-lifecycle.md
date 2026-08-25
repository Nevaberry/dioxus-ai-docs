# Language, Modules, Providers, and Lifecycle

## Provider-defined functions (`1.7.0`)

Providers can expose functions, including functions selected dynamically from
provider configuration. Invoke them as
`provider::<provider_name>::<funcname>(args)`.

## Recursive file templates (`1.7.0`)

`templatefile` can recursively call `templatefile`, with a default maximum call
depth of 1024. This allows composition of file-backed templates without an
external preprocessing step.

## Early evaluation for modules and backends (`1.8.0`)

Variables and locals can be evaluated early enough for module `source` and
`version` and for backend configuration. Restrict the expressions to values
available during initialization; dynamic provider configuration was not added
with this feature.

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

From 1.8.3, `TOFU_ENABLE_STATIC_SENSITIVE=1` opts into sensitive marking for
variables used in module sources, module versions, and backend configuration.
Without the opt-in, the 1.8 line warns for compatibility; this marking is the
default from 1.9.

OpenTofu 1.9 prompts for input variables required during early evaluation.
Sensitive values are prohibited in backend configuration and module source
locations because initialization or module installation would expose them.

## OpenTofu-specific source files (`1.8.0`)

An OpenTofu-specific `.tofu` file masks the identically named `.tf` file. If
both `main.tofu` and `main.tf` exist, OpenTofu ignores `main.tf`. A module can
therefore keep a Terraform-compatible `.tf` fallback while adding OpenTofu-only
syntax in the matching `.tofu` file.

## Iterated aliased providers (`1.9.0`)

An aliased provider configuration can use `for_each`. `each.key` can configure
each provider instance, and resources can select different members.

```hcl
provider "aws" {
  alias    = "by_region"
  for_each = var.aws_regions

  region = each.key
}
```

## Module interface deprecations (`1.10.0`)

Module authors can mark input variables and outputs deprecated. Callers that
use the deprecated interface receive warnings, allowing an interface to be
phased out before removal.

## Cross-type moves and controlled removals (`1.10.0`)

`moved` blocks can transfer a remote object between resource instances of
different types while migrating its state. `removed` blocks can contain
`lifecycle` and `provisioner` configuration to control how remaining instances
are handled.

## Short-circuiting and negative indexing (`1.10.0`)

`&&` and `||` short-circuit, so a skipped right operand cannot fail while
dereferencing an absent value. `element` wraps negative indices; `-1` selects
the final element.

```hcl
locals {
  enabled = var.settings != null && var.settings.enabled
  last    = element(var.items, -1)
}
```

## Configuration expression additions (`1.10.0`)

A module `version` may be `null`, which is equivalent to omitting it. Dynamic
instance keys in a resource `provider` selection or module `providers`
selection are automatically converted to strings.

The built-in `terraform` provider adds functions to encode and decode `.tfvars`
data and to encode arbitrary values as OpenTofu expression syntax.

## Ephemeral values and write-only attributes (`1.11.0`)

Ephemeral input variables, outputs, and provider-defined resources live only in
memory for one operation phase and are never stored in plans or state.
Providers can expose write-only managed-resource attributes for secrets such as
initial passwords or private keys, accepting a value without retaining a copy.
Both ephemeral resource types and write-only attributes require provider
support.

## Conditional existence with `lifecycle.enabled` (`1.11.0`)

Resources and modules can use `lifecycle.enabled` when they should have either
zero or one instances. Its lifecycle placement avoids colliding with a real
argument or module input named `enabled`.

```hcl
module "servers" {
  source  = "./app-cluster"
  servers = 5

  lifecycle {
    enabled = var.enable_cluster
  }
}
```

From 1.11.4, a module containing local provider configurations rejects
`enabled`, matching its restrictions on `count`, `for_each`, and `depends_on`.

## Expression and validation changes (`1.11.0`)

- `issensitive(unknown)` now returns unknown. Ensure its input is known before
  using the result in plan-time-only contexts such as `count` or `for_each`.
- Object constructors assigned to object-typed inputs warn about undeclared
  attribute names.
- `regex` and `regexall` accept long Unicode property names such as
  `\p{Letter}`.
- `fileset` can match literal metacharacters escaped with backslashes.

## Dynamic destruction lifecycle (`1.12.0`)

`lifecycle.prevent_destroy` can refer to other symbols in the same module,
including inputs. `lifecycle.destroy = false` on a managed resource removes the
object from state without asking the provider to destroy it. Use 1.12.4+ when
saving a plan that may replace a resource with `destroy = false`; earlier 1.12
releases fail in that situation.

```hcl
variable "protect_database" {
  type    = bool
  default = true
}

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

## Provider-defined import identities (`1.12.0`)

An `import` block can identify an object with an `identity` object conforming
to the resource type's provider-defined identity schema, instead of only a
plain `id` string.

## Static input contracts (`1.12.0`)

Set `const = true` on an input variable to require its assigned value to be
compatible with static evaluation. This makes an initialization-time contract
explicit.

```hcl
variable "module_source" {
  type  = string
  const = true
}
```

## OpenTofu language constraints (`1.12.0`)

The `language` configuration block separates OpenTofu version constraints from
constraints for other software. A module that uses it requires OpenTofu 1.12
or later, so do not adopt it in a module that must retain older compatibility.

## Replacement propagation (`1.12.0`)

`replace_triggered_by` now replaces a resource when the referenced resource is
itself being replaced. Previously it triggered only when the reference was
updated.

## Null comparisons and sensitivity (`1.12.0`)

Comparing a complex value with `null` produces a sensitive boolean only when
the whole value is sensitive, not merely when a nested attribute is sensitive.
The comparison can therefore feed plan-time contexts such as a resource or
module `enabled` argument when only nested data is sensitive.

## Provider deprecation diagnostics (`1.12.0`)

References to resource attributes or blocks that a provider marks deprecated
produce warnings. `-deprecation=` can disable those diagnostics when needed.

## YAML merge sequences (`1.12.0`)

`yamldecode` supports YAML's `<<` merge tag with a sequence of mappings, in
addition to a single mapping.
