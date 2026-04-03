# Ephemeral Values & Write-Only Arguments

Introduced in Terraform 1.10 (ephemeral variables/outputs/resources) and 1.11 (write-only arguments). Also available in OpenTofu 1.11.

## Ephemeral Variables and Outputs

Ephemeral variables accept sensitive values that must not be stored in state or plan files.

```hcl
variable "session_token" {
  type      = string
  ephemeral = true
}

output "temp_creds" {
  value     = local.creds
  ephemeral = true
}
```

Ephemeral values can only flow into other ephemeral contexts — you cannot assign an ephemeral value to a regular resource argument (unless it's a write-only argument).

## Ephemeral Resources

A third resource mode alongside managed (`resource`) and data (`data`). Ephemeral resources fetch values at plan/apply time and never persist them.

```hcl
ephemeral "aws_secretsmanager_secret_version" "db_master" {
  secret_id = data.aws_db_instance.example.master_user_secret[0].secret_arn
}

locals {
  credentials = jsondecode(ephemeral.aws_secretsmanager_secret_version.db_master.secret_string)
}

# Ephemeral values can be used in provider configuration
provider "postgresql" {
  host     = data.aws_db_instance.example.address
  password = local.credentials["password"]
}
```

### Lifecycle

Ephemeral resources have an **open/renew/close** lifecycle:
- They run during every plan and every apply (not stored between runs)
- If an input references an unknown value, execution defers to apply phase
- Providers can implement renewal for long-running operations

### Reference syntax

Access ephemeral resource attributes via `ephemeral.<type>.<name>.<attribute>`.

## Write-Only Arguments

Managed resource attributes that accept ephemeral values and are never persisted to state. Each write-only argument is paired with a version argument to control when the value is re-sent.

```hcl
ephemeral "random_password" "db" {
  length = 16
}

resource "aws_db_instance" "main" {
  instance_class    = "db.t3.micro"
  engine            = "postgres"
  username          = "admin"

  # Write-only: value is sent to the API but not stored in state
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = 1  # Increment to trigger password update
}
```

### Common write-only attributes

| Resource | Write-only attribute | Version attribute |
|---|---|---|
| `aws_db_instance` | `password_wo` | `password_wo_version` |
| `aws_rds_cluster` | `master_password_wo` | `master_password_wo_version` |
| `aws_secretsmanager_secret_version` | `secret_string_wo` | `secret_string_wo_version` |
| `aws_ssm_parameter` | `value_wo` | `value_wo_version` |
| `google_secret_manager_secret_version` | `secret_data_wo` | `secret_data_wo_version` |
| `kubernetes_secret_v1` | `data_wo` | `data_wo_version` |

### How it works

1. On `terraform apply`, the write-only value is sent to the provider API
2. The value is **not** stored in the state file — only the version number is stored
3. To rotate a secret, increment the `_wo_version` number
4. The provider sees the version change and sends the new value to the API

## Helper Functions

**`ephemeralasnull(value)`** — Converts an ephemeral value to a non-ephemeral null. Useful when you need to use an ephemeral value in a conditional but don't need the actual value in a non-ephemeral context.

**`terraform.applying`** — Returns `true` during the apply phase, `false` during plan. Useful for conditional logic that should only execute during apply.
