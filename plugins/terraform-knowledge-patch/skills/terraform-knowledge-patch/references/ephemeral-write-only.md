# Ephemeral Resources & Write-Only Attributes

## Ephemeral Resources (1.10)

New `ephemeral` block type — resources that are never persisted to state. Re-read every plan/apply. Use for short-lived credentials or secrets.

```hcl
ephemeral "aws_secretsmanager_secret_version" "db_pass" {
  secret_id = "my-db-password"
}

resource "aws_db_instance" "main" {
  password_wo         = ephemeral.aws_secretsmanager_secret_version.db_pass.secret_string
  password_wo_version = 1
}
```

Variables and outputs can be `ephemeral = true`. Ephemeral values can only flow to contexts that accept them (provider configs, write-only attributes, other ephemeral outputs).

`ephemeralasnull(value)` — replaces ephemeral portions with `null` for bridging to non-ephemeral contexts.

## Write-Only Attributes (1.11)

Provider-defined attributes that accept values but are never stored in state. Named with `_wo` suffix, paired with a `_wo_version` integer. Increment version to trigger rotation.

```hcl
ephemeral "random_password" "db" {
  length = 32
}

resource "aws_db_instance" "main" {
  password_wo         = ephemeral.random_password.db.result
  password_wo_version = 1  # bump to rotate
}
```

The provider sends the write-only value on every apply regardless of version — version changes just signal "this is a new value."
