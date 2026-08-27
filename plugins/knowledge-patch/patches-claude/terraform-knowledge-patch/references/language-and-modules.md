# Language, Values, Modules, and Providers

## Values, marks, and expressions

### Sensitivity behavior

- `nonsensitive` accepts an already non-sensitive value and returns it
  unchanged (`terraform-1.7.0`).
- A sensitive path passed to `templatefile` makes the rendered result
  sensitive (`terraform-1.9.0`).
- Conditional and `for` expressions combine marks from every participating
  value, so an upgrade can make a formerly exposed result sensitive
  (`terraform-1.10.0`).
- Terraform preserves sensitivity supplied dynamically to test inputs, not
  only sensitivity declared on the destination variable
  (`terraform-1.9.0`).
- OpenTofu 1.8.7 prevents validation errors from disclosing sensitive values
  (`opentofu-1.8.0`).
- Nested module outputs preserve declared sensitivity. Terraform 1.13.2 also
  hides changed sensitive inputs between plan and apply, and 1.13.3 preserves
  sensitive and ephemeral metadata in variable-validation conditions
  (`terraform-1.13.0`).
- In OpenTofu, comparing a complex value with `null` is sensitive only when
  the whole value is sensitive, not merely because a nested value is. Such
  checks can drive non-sensitive contexts such as `enabled`
  (`opentofu-1.12.0`).

### Expression compatibility

- `element(collection, index)` accepts negative indices. Terraform 1.10.0
  through 1.10.4 can crash for tuples, so use 1.10.5 or later
  (`terraform-1.10.0`).
- `&&` and `||` short-circuit in Terraform, avoiding evaluation of a
  right-hand expression once the result is known (`terraform-1.12.0`).
- OpenTofu `regex` and `regexall` accept long Unicode property names such as
  `\p{Letter}`; `fileset` matches escaped glob metacharacters in filenames
  (`opentofu-1.11.0`).
- OpenTofu `yamldecode` accepts YAML `<<` merge tags whose value is a sequence
  of mappings (`opentofu-1.12.0`).

```hcl
locals {
  service = yamldecode(<<-YAML
    base: &base {retries: 3}
    timing: &timing {timeout: 30}
    service:
      <<: [*base, *timing]
  YAML
  )
}
```

## Templates and provider functions

### Provider-contributed functions

Terraform providers expose functions as
`provider::provider_name::function_name(...)`. The built-in `terraform`
provider supplies `decode_tfvars`, `encode_tfvars`, and `encode_expr`
(`terraform-1.8.0`).

OpenTofu providers can derive their available functions from provider
configuration. Use 1.7.5 or later for complete behavior: earlier fixes cover
tests in 1.7.1, variables and outputs in 1.7.2, child modules in 1.7.4, and
partially unknown arguments in 1.7.5. OpenTofu schema output also reports
provider functions (`opentofu-1.7.0`, `opentofu-1.8.0`).

OpenTofu provider functions work in `for_each` expressions in `dynamic`
blocks, and indexed provider references such as `null.alias[each.key]` are
valid in `.tf.json` (`opentofu-1.11.0`).

### Dynamic template strings

Terraform `templatestring` renders dynamically obtained text. Its first
argument must directly reference a named string object in the current module;
the second argument supplies interpolation values (`terraform-1.9.0-guide`).

```hcl
locals {
  rendered = templatestring(data.http.template.response_body, {
    APP_NAME = var.app_name
  })
}
```

OpenTofu also supplies `templatestring` and permits recursive `templatefile`
calls, with a default maximum depth of 1024 (`opentofu-1.7.0`).

Terraform checks filesystem-function results for apply-time consistency. Use
1.13.5 or later when `templatefile` calls impure functions or filesystem
functions run in provider configuration (`terraform-1.13.0`).

## Validation and unknown values

Terraform input validation conditions can refer to other variables, locals,
and data sources (`terraform-1.9.0-guide`).

```hcl
variable "endpoint" {
  type    = string
  default = ""

  validation {
    condition     = !var.enabled || length(var.endpoint) > 0
    error_message = "Set endpoint when enabled."
  }
}
```

Terraform 1.9.0 through 1.9.3 can run irrelevant validations during a destroy
plan and fail with incomplete state; 1.9.4 fixes this
(`terraform-1.9.0`).

For OpenTofu (`opentofu-1.11.0`):

- Assigning an object with attributes absent from the target object type
  produces a warning.
- `issensitive(unknown)` is unknown, so it cannot decide plan-time-only
  `count` or `for_each` unless the argument is known.
- `tofu validate` can validate non-root modules declaring provider
  `configuration_aliases`.

Terraform validates invalid `list`, `import`, `backend`, and `cloud` blocks in
child modules and reports errors or warnings (`terraform-1.15.9`).

Terraform 1.13 alpha builds accepted `terraform plan -allow-deferral`, unknown
`count` and `for_each` values for modules, resources, and data sources, and
more flexible provider responses to unknown values. Those experiments are not
available in stable Terraform 1.13 (`terraform-1.13.0`).

## Ephemeral values and write-only arguments

### Terraform phase-scoped values

Terraform supports `ephemeral = true` variables and outputs, provider-defined
`ephemeral` resources, `ephemeralasnull`, and `terraform.applying`
(`terraform-1.10.0-guide`). Values are omitted from plan and state, can differ
between plan and apply, and resources open and close independently for each
operation phase. Managed-resource write-only arguments are not part of that
initial feature.

Terraform later adds provider-declared write-only managed-resource arguments
(`terraform-1.11.0-guide`). They accept ephemeral or ordinary values, are sent
on each operation, and are neither stored nor diffed. Increment a stored
provider-specific version argument to expose rotation.

```hcl
resource "aws_db_instance" "main" {
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = var.password_version
}
```

If an ephemeral resource input is unknown during planning but becomes known
later, Terraform defers opening it until apply while retaining dependency
ordering (`terraform-1.11.0-guide`). Use Terraform 1.11.1 or later when a value
is both sensitive and ephemeral, 1.11.3 or later for zero-instance modules
containing ephemeral resources (`terraform-1.11.0`), and 1.12.2 or later for
partially ephemeral output values (`terraform-1.12.0`).

### OpenTofu phase-scoped values

OpenTofu supports ephemeral inputs, outputs, resources, and write-only managed
resource attributes (`opentofu-1.11.0`). OpenTofu later rejects ephemeral
values in `count` (`opentofu-1.12.0`).

## Module and provider configuration

### OpenTofu early evaluation

OpenTofu permits variables and locals in module sources, module versions, and
backend configuration (`opentofu-1.8.0`). These expressions are evaluated
early; provider configuration is not dynamically evaluated by that feature.
Use 1.8.5 or later with reinitialization or `-backend-config` to avoid false
backend-change reports.

OpenTofu 1.8.3 adds sensitivity handling for early module and backend inputs.
Set `TOFU_ENABLE_STATIC_SENSITIVE=1` on that line; the behavior becomes the
default in 1.9. OpenTofu 1.9 prompts for missing early inputs and rejects
sensitive module-source or backend values that initialization would expose
(`opentofu-1.8.0`, `opentofu-1.9.0`).

An OpenTofu `.tofu` file overrides the identically named `.tf` file, allowing
portable configuration and product-specific extensions to coexist
(`opentofu-1.8.0`). OpenTofu 1.12 adds `const = true` for inputs that must be
compatible with static evaluation and a `language` block that separates the
OpenTofu constraint from other software constraints; its normal form makes
1.12 the module minimum unless the interim compatibility form is used
(`opentofu-1.12.0`).

### Terraform dynamic modules

Terraform module `source` and `version` can use variables and locals, and
commands accept the variable values needed to resolve them
(`terraform-1.15.0`). Use 1.15.5 or later for a dynamic module version that
evaluates to `null`, and 1.15.6 or later for installation involving null,
sensitive, or ephemeral module-source values.

OpenTofu 1.9.1 is required for GitHub module sources whose branch name
contains slashes (`opentofu-1.9.0`). OpenTofu 1.11 S3 module sources follow
AWS CLI and SDK credential search rules (`opentofu-1.11.0`); OpenTofu 1.12
`s3::http://` sources use plaintext HTTP except for official AWS hosts
(`opentofu-1.12.0`).

### Module interface contracts

OpenTofu input variables and outputs accept deprecation messages. Use 1.10.7
or later for complex values and tests: 1.10.6 fixes multiple deprecated-mark
crashes, and 1.10.7 fixes tests consuming deprecated outputs
(`opentofu-1.10.0`).

Terraform variables and outputs accept `deprecated`, and warnings include
provider-supplied deprecations on resource attributes and blocks. Terraform
outputs can declare `type`, and `convert(value, type)` performs explicit
conversion (`terraform-1.15.0`).

### Iterated provider configurations and lifecycle enablement

OpenTofu alternate provider configurations accept `for_each` for dimensions
such as regions (`opentofu-1.9.0`). Resources and modules can use nested
`lifecycle { enabled = CONDITION }` for zero-or-one instances
(`opentofu-1.11.0`). Starting in 1.11.4, modules with local provider
configurations reject `enabled`, matching restrictions on `count`, `for_each`,
and `depends_on`.

OpenTofu `prevent_destroy` can refer to other symbols in the module
(`opentofu-1.12.0`).
