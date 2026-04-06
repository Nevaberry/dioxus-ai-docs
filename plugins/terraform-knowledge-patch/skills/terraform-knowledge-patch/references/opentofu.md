# OpenTofu-Specific Features

Features available in OpenTofu but not in Terraform (as of TF 1.15 / OT 1.12).

## `enabled` Meta-Argument (OT 1.11)

A cleaner alternative to `count = var.create ? 1 : 0` for conditionally creating resources. Works on any resource or module block.

```hcl
resource "aws_instance" "example" {
  ami           = var.ami
  instance_type = "t3.micro"

  lifecycle {
    enabled = var.create_instance  # true or false
  }
}
```

### Key differences from count

| Aspect | `count` | `enabled` |
|---|---|---|
| Syntax | `count = var.create ? 1 : 0` | `lifecycle { enabled = var.create }` |
| Resource address | `aws_instance.example[0]` | `aws_instance.example` |
| Refactoring | Changing to/from count changes addresses | No address change |
| Multiple instances | Supports `count > 1` | Only true/false |

The main advantage is that `enabled` doesn't change the resource address — no state moves needed when toggling.

## `lifecycle { destroy = false }` (OT 1.12)

Removes an object from state without destroying the real infrastructure. Similar to the `removed` block but declared inline on the resource.

```hcl
resource "aws_instance" "example" {
  ami           = var.ami
  instance_type = "t3.micro"

  lifecycle {
    destroy = false
  }
}
```

When this resource is removed from configuration, OpenTofu will remove it from state but will **not** make an API call to destroy the actual resource.

## `const = true` Variables (OT 1.12)

Marks a variable as requiring a value compatible with static evaluation. The value must be known at parse time — no references to other variables, data sources, or computed values.

```hcl
variable "project_name" {
  type    = string
  default = "myapp"
  const   = true
}
```

This enables the variable to be used in contexts that require static values (e.g., backend configuration, module sources).

## `prevent_destroy` Expressions (OT 1.12)

`prevent_destroy` can now reference input variables and other symbols instead of only accepting literal boolean values.

```hcl
variable "protect_resources" {
  type    = bool
  default = true
}

resource "aws_instance" "critical" {
  ami           = var.ami
  instance_type = "t3.micro"

  lifecycle {
    prevent_destroy = var.protect_resources
  }
}
```

In Terraform, `prevent_destroy` only accepts literal `true` or `false`.
