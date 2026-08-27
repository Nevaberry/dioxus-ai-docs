# State and plan encryption

## Encryption graph (`1.7-state-encryption`)

OpenTofu can encrypt local or backend state and saved plans independently. An encryption configuration declares a key provider, passes its result to a method, and selects that method for `state`, `plan`, or both.

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

`TF_ENCRYPTION` accepts the body of the `encryption` block and merges over configuration in code. `enforced = true` prevents plaintext output if, for example, an environment-supplied method is absent.

Variables and locals used here normally must resolve during `tofu init`; they cannot depend on state or provider-defined functions. OpenTofu 1.11 adds apply-time inputs for encryption, but every non-ephemeral input supplied during apply must equal its planned value.

## Plaintext migration and key rollover

Enabling encryption does not by itself authorize reading existing plaintext. Configure the new method as primary and the old representation explicitly as a fallback:

```hcl
method "unencrypted" "migration" {}

state {
  method = method.aes_gcm.main
  fallback {
    method = method.unencrypted.migration
  }
}
```

Reads try the primary and then fallbacks. Every write uses the primary, so a successful `tofu apply` rewrites state and lets you remove the fallback. The same sequence migrates keys or methods.

To decrypt intentionally, make `unencrypted` primary, retain the old encrypted method as fallback, disable enforcement, apply successfully, and only then remove encryption configuration.

OpenTofu 1.9 automatically applies encryption-configuration changes as migration. The primary/fallback model still defines which old representations remain readable and which method writes the new artifact.

## Metadata and upgrade compatibility

Encrypted artifacts store metadata tied to key-provider and method names. Renaming either can make data unreadable. Roll names with a fallback, or assign a stable `encrypted_metadata_alias` before names need to differ, including between a producing configuration and a remote-state consumer.

Documented providers and methods are guaranteed for only one additional minor release. `tofu plan` and `tofu apply` warn when an encryption component is deprecated; migrate it before the following minor upgrade.

## Remote-state data-source decryption

Configure decryption for `terraform_remote_state` separately from encryption of the current project's state. A default can cover all data sources, while named entries override it. Labels can address `<name>`, `<module>.<name>`, or an indexed form such as `<module>.<name>[0]`.

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

Keep metadata aliases stable across producer and consumer configurations.

## PBKDF2 and AES-GCM

PBKDF2 accepts either a passphrase of at least 16 characters or a chained provider result. Its defaults are:

- 32-byte output key
- 600,000 iterations
- 32-byte salt
- SHA-512, with SHA-256 also supported

AES-GCM requires a 16-, 24-, or 32-byte provider key.

```hcl
method "aes_gcm" "main" {
  keys = key_provider.aws_kms.main
}
```

Prefer a derivation provider or a managed key system with rotation over a short static key. Repeated AES-GCM key reuse eventually reaches key-saturation limits.

## Managed key providers

- `aws_kms`: `kms_key_id`, `key_spec`, and S3-style authentication.
- `gcp_kms`: `kms_encryption_key`, `key_length`, and GCS-style authentication.
- `azure_vault`: `vault_uri`, `vault_key_name`, and `key_length`; authentication always uses Entra ID.
- `openbao`: `key_name`, optional `BAO_TOKEN` and `BAO_ADDR`, and an optional transit-engine path.

OpenTofu 1.12 security patches address defects involving OpenBao-wrapped encryption data; use the latest patch in the release series.

## External key providers and methods

Experimental external hooks can fetch keys or implement encryption. A key provider runs one command; an external method has separate encryption and decryption commands and can optionally receive a provider result.

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

The external program first emits one of these protocol headers:

```json
{"magic":"OpenTofu-External-Key-Provider","version":1}
{"magic":"OpenTofu-External-Encryption-Method","version":1}
```

A key provider receives `null` for encryption or stored metadata for decryption, then returns base64 encryption and decryption keys plus optional metadata. An external method receives and returns a base64 `payload` and an optional base64 `key`.

In JSON-form encryption method configuration, OpenTofu 1.11.4 accepts `keys` as either a normal expression or template interpolation; earlier 1.11 builds required interpolation.
