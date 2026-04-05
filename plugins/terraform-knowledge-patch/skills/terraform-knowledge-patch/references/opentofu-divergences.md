# OpenTofu Divergences

Features in OpenTofu that differ from or don't exist in Terraform.

## State and Plan Encryption (OT 1.7+)

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = var.passphrase
    }
    method "aes_gcm" "main" {
      keys = key_provider.pbkdf2.main
    }
    state {
      method   = method.aes_gcm.main
      enforced = true
    }
    plan {
      method = method.aes_gcm.main
    }
  }
}
```

Key providers: `pbkdf2`, `aws_kms`, `gcp_kms`, `azure_vault`, `openbao`. Supports `fallback {}` for key rollover. Can also be configured via `TF_ENCRYPTION` env var.

## `.tofu` File Extension (OT 1.8+)

`main.tofu` silently overrides `main.tf`. Lets module authors ship OpenTofu-specific syntax alongside Terraform-compatible files.

## Early Evaluation (OT 1.8+)

Variables and locals usable in `backend`, `encryption`, and module `source` blocks — places that require static values in Terraform (until TF 1.15).

## Provider `for_each` (OT 1.9+)

```hcl
provider "aws" {
  for_each = toset(["us-east-1", "eu-west-1"])
  alias    = each.key
  region   = each.key
}
```

Not available in Terraform.

## `lifecycle { enabled = }` (OT 1.11+)

Replaces the `count = var.enabled ? 1 : 0` pattern:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-123"
  instance_type = "t3.micro"
  lifecycle {
    enabled = var.create_instance
  }
}
```

Works on both resources and modules.

## `-exclude` Flag (OT 1.9+)

`tofu plan -exclude=aws_instance.example` — inverse of `-target`. Also `-exclude-file` to read from file.

## OCI Registry Support (OT 1.10+)

Providers and modules can be fetched from OCI (container) registries. Useful for air-gapped environments.
