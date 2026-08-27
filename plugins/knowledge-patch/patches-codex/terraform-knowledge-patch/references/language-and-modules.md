# Language, Values, Modules, and Providers

## Provider-defined functions (`terraform-1.8.0`, `opentofu-1.7.0`)

Terraform providers can contribute functions invoked as `provider::provider_name::function_name(...)`. The built-in `terraform` provider includes `decode_tfvars`, `encode_tfvars`, and `encode_expr` for explicitly reading or generating Terraform expression and tfvars syntax.

OpenTofu providers can derive their function set from provider configuration. Use OpenTofu 1.7.5 or later for complete behavior: tests were fixed in 1.7.1, variables and outputs in 1.7.2, child modules in 1.7.4, and partially unknown arguments in 1.7.5. `tofu providers schema` includes provider functions starting in OpenTofu 1.8.

## Template strings

OpenTofu 1.7 adds `templatestring(template, variables)` and permits recursive `templatefile` calls with a default maximum depth of 1024.

```hcl
message = templatestring("Hello, $${name}!", { name = "Ada" })
```

Terraform 1.9 adds the same function, but its template argument must be a direct reference to a named string object in the current module, such as a data-source result; the second argument supplies interpolation variables (`terraform-1.9.0-guide`).

```hcl
locals {
  rendered = templatestring(data.http.template.response_body, {
    APP_NAME = var.app_name
  })
}
```

## Variable validation and value marks

Terraform 1.9 validation conditions can refer to other variables, locals, and data sources instead of only the variable being validated (`terraform-1.9.0-guide`). Terraform 1.9 also propagates sensitivity from a sensitive `templatefile` path to the rendered result instead of failing.

```hcl
variable "cluster_endpoint" {
  type    = string
  default = ""

  validation {
    condition     = var.create_cluster == false ? length(var.cluster_endpoint) > 0 : true
    error_message = "Specify cluster_endpoint when create_cluster is false."
  }
}
```

Terraform 1.10 conditional and `for` expressions combine marks from all participating values. An expression may therefore become sensitive after an upgrade where an older runtime exposed it. Terraform 1.13 preserves sensitivity on nested-module outputs; use 1.13.2 or later to keep changed sensitive inputs hidden between plan and apply, and 1.13.3 or later for validation conditions to preserve sensitive and ephemeral metadata (`terraform-1.13.0`).

OpenTofu 1.8.7 prevents validation errors from disclosing sensitive values. OpenTofu 1.11 warns when an object assigned to a typed variable has attributes outside the target type. Its `issensitive` returns unknown for an unknown argument, so that result cannot control plan-time `count` or `for_each` unless the input is known (`opentofu-1.11.0`).

OpenTofu 1.12 marks `complex_value == null` as sensitive only when the whole value is sensitive, not merely because a nested element is sensitive. Such null checks can be used in non-sensitive contexts such as `enabled` (`opentofu-1.12.0`).

`nonsensitive` accepts already non-sensitive input and returns it unchanged in Terraform 1.7 (`terraform-1.7.0`).

## Ephemeral values

Terraform 1.10 adds `ephemeral = true` input and output variables, provider-defined `ephemeral` resources, `ephemeralasnull`, and `terraform.applying` (`terraform-1.10.0-guide`). Ephemeral values are omitted from plan and state, may differ between plan and apply, and live only for one operation phase. Each ephemeral resource is opened and closed independently during each phase.

```hcl
ephemeral "aws_secretsmanager_secret_version" "db_master" {
  secret_id = data.aws_db_instance.example.master_user_secret[0].secret_arn
}

variable "session_token" {
  type      = string
  ephemeral = true
}
```

Terraform 1.11 can defer opening an ephemeral resource until apply when an input is unknown during planning. Dependencies still order prerequisites before the resource and consumers after it (`terraform-1.11.0-guide`). Use 1.11.1 or later for values that are both sensitive and ephemeral, and 1.11.3 or later for zero-instance modules containing ephemeral resources (`terraform-1.11.0`).

Terraform 1.12.2 permits partial ephemeral values in outputs declared ephemeral (`terraform-1.12.0`). OpenTofu 1.11 adds ephemeral inputs, outputs, resources, and provider-declared write-only managed-resource attributes (`opentofu-1.11.0`). OpenTofu 1.12 rejects ephemeral `count` values (`opentofu-1.12.0`).

## Dynamic and early-evaluated modules

OpenTofu 1.8 allows variables and locals in module sources and versions and in backend configuration (`opentofu-1.8.0`). These expressions run before provider configuration. Use 1.8.5 or later when combining variable- or local-based backend settings with reinitialization or `-backend-config`.

OpenTofu 1.8.3 adds sensitivity handling for early-evaluated module and backend inputs. On that line, enable the compatibility behavior below; it becomes the default in 1.9.

```shell
export TOFU_ENABLE_STATIC_SENSITIVE=1
```

OpenTofu 1.9 prompts for missing early-evaluation inputs and rejects sensitive values for backend configuration or module source locations, where initialization or installation would expose them (`opentofu-1.9.0`). OpenTofu 1.9.1 is required for GitHub module sources whose branch names contain slashes.

Terraform 1.15 permits variables and locals in module `source` and `version`, and most commands accept variable values to resolve them (`terraform-1.15.0`). Version 1.15.5 permits a dynamic module version to be `null`; 1.15.6 fixes installation edge cases involving `null` and sensitive or ephemeral source values.

```hcl
variable "module_source" {
  type = string
}

locals {
  module_version = "1.2.0"
}

module "service" {
  source  = var.module_source
  version = local.module_version
}
```

## Static-evaluation contracts and product-specific files

OpenTofu 1.12 variables can declare `const = true` to require assignments compatible with static evaluation. Its new `language` configuration separates the OpenTofu constraint from constraints on other software; the normal form makes 1.12 the module minimum unless the backward-compatible interim form is used.

```hcl
variable "module_source" {
  type  = string
  const = true
}
```

Since OpenTofu 1.8, a `.tofu` file causes OpenTofu to ignore the identically named `.tf` file. Keep portable configuration in `main.tf` and OpenTofu-only constructs in `main.tofu`.

## Module contracts and deprecations

OpenTofu 1.10 variables and outputs accept deprecation messages (`opentofu-1.10.0`). Use at least 1.10.7 for tests or complex deprecated values: 1.10.6 fixes crashes involving multiple deprecated marks, and 1.10.7 fixes tests consuming deprecated outputs.

Terraform 1.15 variables and outputs also accept `deprecated`; assigning a deprecated variable or reading a deprecated output warns. Provider-authored deprecations on resource attributes and blocks also appear as warnings.

```hcl
variable "legacy_region" {
  type       = string
  deprecated = "Use region instead."
}

output "legacy_id" {
  value      = example_resource.main.id
  deprecated = "Use resource_id instead."
}
```

Terraform 1.15 output blocks can declare `type`, and `convert(value, type)` performs an explicit inline conversion.

```hcl
output "ports" {
  value = convert(var.ports, set(number))
  type  = set(number)
}
```

## Provider configuration iteration

OpenTofu 1.9 alternate provider configurations can use `for_each`, letting resources choose instances by region or another deployment dimension.

```hcl
provider "aws" {
  alias    = "by_region"
  for_each = var.aws_regions
  region   = each.key
}
```

OpenTofu 1.11 accepts provider functions in `for_each` expressions inside `dynamic` blocks and indexed provider references such as `null.some_alias[each.key]` in `.tf.json`.

## Expressions and lifecycle

- Terraform 1.10 `element` accepts negative indices. Versions 1.10.0 through 1.10.4 can crash for tuples; use 1.10.5 or later (`terraform-1.10.0`).
- Terraform 1.12 `&&` and `||` short-circuit, so a decisive left side can protect an invalid right-side access (`terraform-1.12.0`).
- OpenTofu 1.9.1 makes `plantimestamp()` unknown during validation; validation expressions must tolerate that (`opentofu-1.9.0`).
- Terraform 1.13 checks filesystem-function results for plan/apply consistency. Use 1.13.5 or later when `templatefile` calls impure functions or filesystem functions appear in provider configuration.
- OpenTofu 1.11 `regex` and `regexall` accept long Unicode properties such as `\p{Letter}`, and `fileset` can match filenames containing escaped glob metacharacters.
- OpenTofu 1.12 `yamldecode` accepts YAML merge keys whose value is a sequence of mappings.

```hcl
condition = var.settings == null || var.settings.enabled

locals {
  config = yamldecode(<<-YAML
    base: &base {retries: 3}
    timing: &timing {timeout: 30}
    service:
      <<: [*base, *timing]
  YAML
  )
}
```

OpenTofu 1.11 resources and modules can use `lifecycle { enabled = CONDITION }` as a zero-or-one alternative to `count` or `for_each`. From 1.11.4, modules with local provider configurations reject it like `count`, `for_each`, and `depends_on`.

OpenTofu 1.12 lets `prevent_destroy` refer to other symbols in the same module. It also replaces a resource when its `replace_triggered_by` target is itself being replaced, rather than only when that target is updated.

## Validation boundaries

OpenTofu 1.11 can validate non-root modules that declare provider `configuration_aliases`. Terraform 1.15.9 reports errors or warnings for invalid `list`, `import`, `backend`, and `cloud` blocks in child modules (`terraform-1.15.9`). Configurations that previously passed validation may therefore produce new diagnostics.

Terraform 1.13 `-allow-deferral` for unknown `count` and `for_each` values was alpha-only and is unavailable in stable 1.13 binaries.
