# State and Plan Encryption

## Configuration graph (`1.7-state-encryption`)

OpenTofu encrypts local or backend state and saved plans independently. The
configuration graph connects a key provider to a method and selects that method
for `state`, `plan`, or both. `TF_ENCRYPTION` accepts the contents of the
`encryption` block and merges over the configuration written in code.

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = var.state_passphrase
    }
    method "aes_gcm" "main" {
      keys = key_provider.pbkdf2.main
    }
    state {
      method   = method.aes_gcm.main
      enforced = true
    }
    plan {
      method   = method.aes_gcm.main
      enforced = true
    }
  }
}
```

`enforced = true` prevents plaintext output when, for example, an environment-
supplied method is absent. Variables and locals used here must resolve during
`tofu init`; they cannot depend on state data or provider-defined functions.

## Plaintext migration, decryption, and rollover (`1.7-state-encryption`)

Enabling encryption alone does not authorize OpenTofu to read an existing
plaintext artifact. Make the new method primary and explicitly allow the old
representation as a fallback. Reads try the primary and then fallbacks; every
write uses the primary. After a successful `tofu apply` rewrites state, remove
the fallback.

```hcl
method "unencrypted" "migration" {}

state {
  method = method.aes_gcm.main
  fallback {
    method = method.unencrypted.migration
  }
}
```

Use the same procedure to rotate keys or methods. To decrypt deliberately,
reverse the configuration: make `unencrypted` primary, retain the old encrypted
method as a fallback, disable enforcement, apply successfully, and only then
remove encryption configuration.

From `1.9.0`, changing encryption configuration automatically applies the
migration. This does not remove the need to preserve readable old methods or
metadata during a rollover.

## Stored metadata and compatibility (`1.7-state-encryption`)

Encrypted artifacts store metadata tied to key-provider and method names.
Renaming either can make the artifact unreadable. Roll names with a fallback,
or assign a stable `encrypted_metadata_alias` before producer and consumer
names need to differ, including between a state producer and a remote-state
consumer.

Documented key providers and methods are guaranteed for only one additional
minor release. `tofu plan` and `tofu apply` warn when a deprecated provider or
method must be migrated before the next minor upgrade.

## Remote-state data source decryption (`1.7-state-encryption`)

Configure decryption for `terraform_remote_state` separately from the current
project's state. A default can cover all data sources, and named entries can
override it. Labels may target `<name>`, `<module>.<name>`, or indexed forms
such as `<module>.<name>[0]`.

```hcl
remote_state_data_sources {
  default {
    method = method.aes_gcm.shared
  }
  remote_state_data_source "database.primary[0]" {
    method = method.aes_gcm.database
  }
}
```

## Key providers and AES-GCM (`1.7-state-encryption`)

The PBKDF2 provider accepts a passphrase of at least 16 characters or a chained
provider result. Defaults are a 32-byte key, 600,000 iterations, a 32-byte salt,
and SHA-512; SHA-256 is also supported.

Cloud-backed providers are:

- `aws_kms`: `kms_key_id`, `key_spec`, and S3-style authentication.
- `gcp_kms`: `kms_encryption_key`, `key_length`, and GCS-style authentication.
- `azure_vault`: `vault_uri`, `vault_key_name`, `key_length`, and Entra ID.
- `openbao`: `key_name`, optional `BAO_TOKEN` and `BAO_ADDR`, and a Transit
  engine path.

```hcl
method "aes_gcm" "main" {
  keys = key_provider.aws_kms.main
}
```

AES-GCM requires a 16-, 24-, or 32-byte provider key. Prefer a derivation
provider or a key-management system with rotation to a short static key;
repeated use of one AES-GCM key eventually reaches key-saturation limits.

## External key providers and methods (`1.7-state-encryption`)

Experimental external hooks can fetch keys or implement encryption. A key
provider runs one `command`; an external method has `encrypt_command` and
`decrypt_command` arrays and may consume a key-provider result.

```hcl
key_provider "external" "keys" {
  command = ["./keys"]
}
method "external" "cipher" {
  encrypt_command = ["./cipher", "--encrypt"]
  decrypt_command = ["./cipher", "--decrypt"]
  keys            = key_provider.external.keys
}
```

The external program first emits a protocol declaration:

- Key provider: `{"magic":"OpenTofu-External-Key-Provider","version":1}`.
- Method: `{"magic":"OpenTofu-External-Encryption-Method","version":1}`.

Key-provider input is `null` for encryption or stored metadata for decryption.
It returns base64 encryption and decryption keys plus optional metadata. Method
input and output carry a base64 `payload` and optional base64 `key`.

## Apply-time encryption inputs (`1.11.0`)

Input values can be supplied during apply for state and plan encryption. Every
non-ephemeral input must still equal its planned value. From 1.11.4, JSON-form
method configuration accepts `keys` as either a normal expression or template
interpolation; it no longer requires interpolation.

## Backend encryption additions (`1.12.0`)

The AzureRM backend supports Customer-Provided Keys and Customer-Managed Keys
for server-side encryption. OpenBao-wrapped encryption data in early 1.12
releases was affected by a security defect; follow the current patch-level
floor in [upgrade-security-and-platforms.md](upgrade-security-and-platforms.md).
