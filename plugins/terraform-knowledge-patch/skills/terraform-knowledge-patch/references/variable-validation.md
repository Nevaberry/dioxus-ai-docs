# Cross-Object Variable Validation

Introduced in Terraform 1.9.

## What Changed

Previously, `validation` blocks in variable declarations could only reference the variable being validated (`var.this_var`). Now they can reference:

- Other input variables (`var.other_var`)
- Data sources (`data.type.name`)
- Local values (`local.name`)

## Example: Conditional Requirement

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
    error_message = "cluster_endpoint required when create_cluster is false."
  }
}
```

## Example: Validating Against a Data Source

```hcl
data "aws_availability_zones" "available" {}

variable "availability_zone" {
  type = string

  validation {
    condition     = contains(data.aws_availability_zones.available.names, var.availability_zone)
    error_message = "Must be a valid availability zone in the current region."
  }
}
```

## Key Points

- Validation blocks are evaluated after all variables, locals, and data sources are resolved
- Circular references between validation blocks and the objects they reference are not allowed
- This feature significantly reduces the need for custom validation modules or `precondition` blocks in resources
