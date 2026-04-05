# Language Features

## Short-Circuit Logical Operators (1.12)

`&&` and `||` now short-circuit — right-hand side is not evaluated if result is determined. Safe to write `var.map != null && var.map["key"] == "value"`.

## `deprecated` Attribute on Variables and Outputs (1.15)

Module authors can deprecate interfaces:

```hcl
variable "old_name" {
  type       = string
  deprecated = "Use var.new_name instead"
}

output "legacy" {
  value      = local.result
  deprecated = "Use output.current instead"
}
```

## `convert()` Function (1.15)

Explicit type conversion: `convert(value, type)` for precise control over type coercion.

## Variables and Locals in Module `source` and `version` (1.15)

```hcl
variable "env" { default = "prod" }

module "app" {
  source  = "hashicorp/consul/aws"
  version = var.consul_version  # was previously static-only
}
```

## Output Type Constraints (1.15)

```hcl
output "ids" {
  type  = list(string)
  value = aws_instance.main[*].id
}
```
