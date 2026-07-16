# Language, Values, Modules, and Providers

Expression semantics, value marks, module contracts, early evaluation, and provider-facing configuration changes.

## Ephemeral, sensitive, and write-only values

### `nonsensitive` accepts already non-sensitive values

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

`nonsensitive(value)` no longer errors when `value` is already non-sensitive, so callers can apply it without first branching on the value's sensitivity.

### Apply-time deferral for ephemeral resources

*Terraform 1.11.0 — batch `terraform-1.11.0-guide`.*

If an ephemeral resource input is unknown during planning but will resolve during apply, Terraform defers opening that resource until apply. Ephemeral resources participate in the dependency graph, so a generated value can be written to an external secret store through a write-only argument, read back through a deferred ephemeral resource, and then passed to a downstream write-only consumer; this preserves a generated secret outside Terraform without putting it in plan or state.

### Ephemeral resources are phase-scoped

*Terraform 1.10.0 — batch `terraform-1.10.0-guide`.*

An `ephemeral` block declares a third resource mode whose object is created or fetched separately for each Terraform phase and explicitly closed before that phase ends. Terraform stores neither the object nor its values in plan or state, and the values need not remain consistent between plan and apply or between runs.

```hcl
ephemeral "aws_secretsmanager_secret_version" "db_master" {
  secret_id = var.secret_id
}

locals {
  credentials = jsondecode(
    ephemeral.aws_secretsmanager_secret_version.db_master.secret_string
  )
}

provider "postgresql" {
  username = local.credentials["username"]
  password = local.credentials["password"]
}
```

Provider support is resource-type-specific. The 1.10 launch set included `aws_secretsmanager_secret_version`, `aws_lambda_invocation`, `azurerm_key_vault_secret`, `azurerm_key_vault_certificate`, `kubernetes_token_request`, and `kubernetes_certificate_signing_request`, along with ephemeral resources in the `random` provider.

### Ephemeral values reach OpenTofu

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

OpenTofu now supports ephemeral input variables and outputs, provider-defined ephemeral resources, and managed-resource write-only attributes. Ephemeral data exists only in memory for one OpenTofu phase and is not persisted in plan or state; providers must explicitly expose the corresponding resource types or attributes.

### Exact 1.10 ephemeral surface

*Terraform 1.10.0 — batch `terraform-1.10.0-guide`.*

Input and output variables can be marked `ephemeral = true` for short-lived values such as session tokens, and Terraform 1.10 also adds the `ephemeralasnull` and `terraform.applying` language helpers.

```hcl
variable "session_token" {
  type      = string
  ephemeral = true
}
```

Managed-resource write-only arguments are not part of Terraform 1.10; they arrive in Terraform 1.11. Configurations using arguments such as `password_wo` or `secret_string_wo` therefore require a later Terraform release even when their values come from an `ephemeral` block.

### Language and ephemeral patch compatibility

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

Terraform 1.11.1 fixes planned-change serialization when values combine ephemeral and sensitive marks. Terraform 1.11.2 makes a `templatestring` consisting only of one null-valued interpolation return an error, while 1.11.3 fixes apply errors when a zero-instance module contains ephemeral resources.

### Managed-resource write-only arguments

*Terraform 1.11.0 — batch `terraform-1.11.0-guide`.*

Terraform 1.11 lets provider-declared write-only arguments accept either ephemeral or ordinary values. Terraform sends a write-only value to the provider during every operation but records it in neither plan nor state, so it cannot display a diff or detect that the value itself changed.

```hcl
locals {
  password_version = 1
}

ephemeral "random_password" "database" {
  length = 16
}

resource "aws_db_instance" "database" {
  instance_class      = "db.t3.micro"
  allocated_storage   = 5
  engine              = "postgres"
  username            = "example"
  skip_final_snapshot = true

  password_wo         = ephemeral.random_password.database.result
  password_wo_version = local.password_version
}
```

Provider-specific companion arguments such as `password_wo_version` are stored in state: increment one to make a rotation visible in the plan and tell the provider to use the new write-only value. Keep the companion versions synchronized when several write-only values must rotate together.

Support is opt-in per resource. Initial examples include `aws_db_instance.password_wo`, `aws_secretsmanager_secret_version.secret_string_wo`, `azurerm_key_vault_secret.value_wo`, `google_secret_manager_secret_version.secret_data_wo`, `kubernetes_secret_v1.data_wo` and `binary_data_wo`, and `helm_release.set_wo`; other database, secret-store, and credential resources also expose provider-specific `_wo` arguments.

### Partial ephemeral output compatibility

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

Terraform 1.12.2 accepts partially ephemeral values in ephemeral outputs; Terraform 1.12.0 and 1.12.1 reject them.

### Sensitive early-evaluation inputs

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

Starting in 1.8.3, handling for variables marked `sensitive` in module sources, module versions, and backend configuration is opt-in. Set `TOFU_ENABLE_STATIC_SENSITIVE=1` in environments using these values; 1.8 otherwise warns for compatibility, and the behavior becomes the default in 1.9.

### Sensitivity and ephemeral metadata fixes

*Terraform 1.13.0 — batch `terraform-1.13.0`.*

Nested-module outputs now retain sensitivity declared in configuration. Terraform 1.13.2 keeps changed sensitive inputs hidden between plan and apply, while 1.13.3 preserves sensitive and ephemeral metadata when evaluating variable validation conditions.

### Validation and marked-value behavior

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

Terraform Stacks now supports input-variable validation. When a container is compared with `null`, only marks on the container itself affect the result; marks nested inside the container no longer mark the comparison result by themselves.

## Functions and expressions

### Built-in tfvars conversion functions

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

The built-in `terraform` provider now exposes `decode_tfvars`, `encode_tfvars`, and `encode_expr` for tooling that needs to read or generate Terraform variable-file content.

### Built-in tfvars tooling functions

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

The built-in `terraform` provider now exposes `decode_tfvars`, `encode_tfvars`, and `encode_expr`, allowing OpenTofu-native tooling to parse variable files and generate variable-file or expression syntax.

### Configuration-dependent provider functions

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

Beyond ordinary provider-defined functions, OpenTofu providers can dynamically define functions based on their provider configuration. The experimental Lua and Go providers demonstrate this OpenTofu-specific capability.

### Dynamic string templates in Terraform

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Terraform 1.9 adds `templatestring(template, variables)` for rendering template text obtained dynamically, such as from an input variable or data resource, rather than loading it from a file with `templatefile`.

```hcl
variable "template" { type = string }
variable "name" { type = string }

output "rendered" {
  value = templatestring(var.template, { name = var.name })
}
```

### Expression and dependency behavior

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

Comparing a complex value with `null` now produces a sensitive boolean only when the container itself is sensitive, not merely when it contains a nested sensitive value; the result can therefore drive `enabled`. `replace_triggered_by` now replaces a resource when the referenced resource is itself being replaced, `yamldecode` supports YAML `<<` merges from sequences of mappings, and a dynamic block's `for_each` can call provider-defined functions. OpenTofu now rejects ephemeral values in `count`.

Calls to modules containing `check` blocks can use `depends_on` without a dependency-cycle error. `length(module.example)` also reports the correct number of instances for `count` or `for_each` modules that declare no outputs.

### Module-source and provider-function patch compatibility

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

OpenTofu 1.9.1 fixes GitHub module sources whose branch names contain slashes. The 1.9.5 notes, still marked unreleased, restore provider functions when parentheses are involved and allow provider-defined functions in a `dynamic` block's `for_each`.

### Negative indices in `element`

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

The `element` function now accepts negative indices. Terraform 1.10.0 through 1.10.4 can crash when a negative index is used with a tuple, so use 1.10.5 or later for that case.

### Provider functions in schema inspection

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

`tofu providers schema` now includes provider-defined functions, allowing schema-driven tooling to discover them instead of maintaining a separate function list.

### Provider-defined functions

*Terraform 1.8.0 — batch `terraform-1.8.0-guide`.*

Terraform 1.8 lets providers expose specialized functions for use in any Terraform expression, including validations, checks, and tests. Invoke them through the provider namespace as `provider::<provider_name>::<function_name>(arguments)`; the function requires a provider version that implements it.

```hcl
locals {
  module_directory_exists = provider::local::direxists(path.module)
}
```

For example, `direxists` is available in the `local` provider from v2.5, while the `time` provider offers `rfc_3339_parse` from v0.11.

### Provider-function patch compatibility

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

Provider functions had important follow-up fixes across the 1.7 line: tests require at least 1.7.1, variables and outputs require 1.7.2, child-module support improved in 1.7.4, and partially unknown arguments follow the plugin protocol starting in 1.7.5.

### Short-circuiting and negative collection indices

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

Logical `&&` and `||` operators now skip the right operand when the left operand determines the result, so they can safely guard expressions that would otherwise fail. `element` extends its wrapping behavior to negative indices, with `-1` selecting the last element; `format` and `formatlist` also accept `null` without producing an apply-time unknown-value failure.

```hcl
locals {
  last    = element(var.items, -1)
  enabled = var.settings != null && var.settings.enabled
}
```

### Short-circuiting logical operators

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

Logical binary operators can now short-circuit, so `false && expression` and `true || expression` need not evaluate the right-hand expression; conditions can therefore guard evaluations that are valid only for some input values.

### Template and validation behavior

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

The new `templatestring(template, variables)` function renders a string value as a template, while `templatefile` can now recurse with a default maximum call depth of 1024. Starting in 1.7.8, `plantimestamp()` correctly remains unknown during validation.

### Validation and expression behavior

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

An object constructor used for a typed input variable now warns about attribute names absent from the target object type, and `tofu validate` can validate non-root modules whose providers declare `configuration_aliases`. `issensitive` now returns an unknown result when its argument is unknown, so it cannot drive plan-time `count` or `for_each` unless the argument is known; `regex` and `regexall` accept long Unicode property names such as `\p{Letter}`, and `fileset` can match escaped glob metacharacters.

### Validation, YAML, and module-selection compatibility

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

Variable validations can now refer to other variables, data, and related values. `yamldecode("+")` follows YAML 1.2 by returning the string `"+"` instead of a numeric parse error, and module `version` constraints now accept `v`-prefixed prerelease selections.

## Modules and provider configuration

### `enabled` for zero-or-one instances

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

Resources and modules can use a boolean `enabled` meta-argument as a clearer alternative to zero-or-one `count` or `for_each`. It is deliberately nested in `lifecycle` so it cannot collide with an existing argument or module input named `enabled`.

```hcl
resource "aws_instance" "example" {
  # ...
  lifecycle {
    enabled = var.enable_instance
  }
}
```

OpenTofu 1.11.1 fixes serialization of `enabled` in saved plans. Starting in 1.11.4, a module containing local provider configurations rejects `enabled`, matching the existing restrictions on `count`, `for_each`, and `depends_on`.

### Apply-time environment-variable overrides

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

Terraform 1.11 reports an attempted variable override through `TF_VAR_*` during `apply` as a warning instead of a misleading error.

### Deprecated module inputs and outputs

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

Module authors can mark input variables and output values as deprecated; callers that use them receive warnings, allowing a module API to evolve without immediately breaking consumers.

```hcl
variable "legacy_region" {
  type       = string
  deprecated = "Use var.region instead."
}
```

Use 1.10.7 or later when testing deprecated outputs, because `tofu test` can crash on them in earlier 1.10 releases.

### Deprecated module inputs and outputs

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

Terraform modules can now set `deprecated = "..."` on `variable` and `output` blocks. Supplying a deprecated input or referencing a deprecated output emits a warning, and deprecation warnings for provider-defined resources, blocks, and attributes now more reliably include the provider's message.

### Early evaluation for modules and backends

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

OpenTofu 1.8 permits input variables and locals in module source and version arguments and in backend configuration. These values must be available during early evaluation; provider configuration is not included in this feature.

```hcl
variable "module_source" {
  default = "./modules/app"
}

module "app" {
  source = var.module_source
}
```

For early-evaluated backends, use 1.8.5 or later: 1.8.4 corrected a false "Backend configuration changed" error involving references and `-backend-config`, while 1.8.5 repaired a related reinitialization regression for backends with required arguments.

### Explicit output types and inline conversion

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

`output` blocks now accept an explicit `type` constraint, while `convert(value, type)` performs a precise conversion at the expression site. Together they let a module state and satisfy its output contract directly.

```hcl
output "port" {
  type  = number
  value = convert(var.port, number)
}
```

### GitHub module refs containing slashes

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Unencoded slashes in GitHub module source refs are no longer truncated or mistaken for subdirectories, so refs such as `?ref=feature/example` work as written.

### Iterated aliased provider configurations

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

An aliased provider configuration can use `for_each` to create dynamically selected instances, letting resource instances use different provider configurations without one manually duplicated block per region.

```hcl
provider "aws" {
  alias    = "by_region"
  for_each = var.aws_regions

  region = each.key
}
```

### Nullable module version constraints and provider keys

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

A module's `version` argument may be `null`, which is equivalent to omitting it. Dynamic instance keys used in a resource's `provider` argument or a module's `providers` map are now automatically converted to strings.

### OCI module sources and provider mirrors

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

OpenTofu can install module packages from OCI registries through the new `oci:` source-address scheme and can use OCI registries as provider mirrors. This enables private or air-gapped distribution of both modules and providers without a conventional module or provider registry.

### OpenTofu-specific `.tofu` overrides

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

When `name.tofu` is present, OpenTofu ignores the identically named `name.tf` file rather than merging the two. A module can therefore keep a compatible `.tf` implementation beside an OpenTofu-specific override.

### Variable-driven module sources and versions

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

Terraform now accepts variables and locals in module `source` and `version` arguments, and most commands can accept the variable values needed to evaluate them. For example, a module can use `source = var.module_source` and `version = local.module_version` instead of requiring both arguments to be literal.

## Validation and evaluation behavior

### Apply-time variable fixes

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Terraform 1.10.1 fixes complex values supplied through environment variables being parsed incorrectly during apply, while 1.10.2 fixes overridden values from auto-loaded tfvars files being reported as changed between plan and apply.

### Cross-object input variable validation

*Terraform 1.9.0 — batch `terraform-1.9.0-guide`.*

An input variable's `validation` condition can now refer to other input variables, locals, and data sources, instead of only the variable being validated. This allows related or dynamically discovered constraints to fail during planning without moving the check to a later resource precondition.

```hcl
variable "create_cluster" {
  type    = bool
  default = false
}

variable "cluster_endpoint" {
  type    = string
  default = ""

  validation {
    condition     = var.create_cluster == false ? length(var.cluster_endpoint) > 0 : true
    error_message = "You must specify cluster_endpoint when not creating a cluster."
  }
}
```

### Destroy plans avoid unnecessary variable validation

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Terraform 1.9.4 stops running unneeded variable validations during destroy plans, preventing failures when such a plan starts with incomplete state.

### Filesystem result consistency

*Terraform 1.13.0 — batch `terraform-1.13.0`.*

Terraform now checks filesystem-function results for consistency to catch invalid data during apply. Terraform 1.13.5 fixes false consistency failures caused by impure functions inside `templatefile` and allows filesystem results to vary when evaluated in provider configuration.

### More complete sensitivity propagation

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Conditional expressions now combine marks from all participating values, so results that incorrectly lost sensitivity in earlier releases may become sensitive after upgrading. Related fixes preserve marks through conditional and `for` expressions with unknown values and prevent `issensitive` from prematurely treating an unknown value as non-sensitive.

### Static-evaluation declarations and language constraints

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

An input variable can set `const = true` to require its assigned value to be available to OpenTofu's static evaluation phase.

```hcl
variable "module_source" {
  type  = string
  const = true
}
```

The new `language` configuration block provides version constraints that distinguish OpenTofu requirements from constraints for other software. Modules adopting it require OpenTofu 1.12 unless they use the release's backward-compatible interim approach.

### Validation with deferred values

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

An unknown variable-validation `error_message` can now pass core validation and be evaluated during planning, and `plantimestamp()` no longer produces an invalid date during validation.

