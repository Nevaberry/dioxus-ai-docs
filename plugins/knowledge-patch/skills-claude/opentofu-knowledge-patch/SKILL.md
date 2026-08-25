---
name: opentofu-knowledge-patch
description: OpenTofu
version: 1.12.0
license: MIT
metadata:
  author: Nevaberry
---


# OpenTofu Knowledge Patch

Use this skill when writing, reviewing, upgrading, testing, or operating OpenTofu configurations. Check the project's required version and lock file first, then apply only guidance available to that version. Prefer the configuration, provider schemas, tests, and observed CLI behavior when they disagree with general guidance.

## Reference index

| Reference | Topics |
|---|---|
| [backends-distribution-and-platforms.md](references/backends-distribution-and-platforms.md) | Backend migrations, credentials, locking, registries, installation, platforms, and transport security |
| [cli-automation-and-output.md](references/cli-automation-and-output.md) | Planning selectors, JSON and concise output, diagnostics, console, environment variables, and tracing |
| [language-modules-and-lifecycle.md](references/language-modules-and-lifecycle.md) | Early evaluation, modules, provider instances and functions, expressions, imports, moves, lifecycle, and ephemeral data |
| [state-and-plan-encryption.md](references/state-and-plan-encryption.md) | Encryption graph, migration, rollover, remote-state decryption, key providers, and external hooks |
| [testing-and-go-tooling.md](references/testing-and-go-tooling.md) | Mocks, overrides, test variables and providers, cleanup recovery, TofuDL, and registry tooling |

## Security and upgrade gates

### Apply current security patch floors

- OpenTofu 1.6 is unsupported and receives no further security updates; upgrade to at least 1.7.
- Use OpenTofu 1.12.6 or 1.11.14 before installing OCI modules or providers; older builds can disclose origin credentials across redirects.
- Those patch levels also prevent crafted relative URLs from an untrusted registry or backend from exhausting CPU or memory during `tofu init`.
- The 1.11 series ends at 1.11.14; move installations on that branch to a newer release series.
- For any 1.12 deployment, prefer the latest patch. Earlier patches also had defects involving SSH, wrapped encryption data, revoked SSH CA keys, and malicious Git URLs.
- Use 1.11.4 or later when provider or module installation may process untrusted ZIP archives.

### Respect platform and transport boundaries

- OpenTofu 1.10 requires Linux kernel 3.2+ or macOS 11+; 1.11 requires macOS 12+.
- The 1.12 series is the last planned to support macOS 12. WinRM warns in 1.12 and is planned to fail in 1.13; migrate Windows provisioners to SSH.
- OpenTofu 1.11 rejects SHA-1 TLS signatures and malformed SSH certificates whose signing key is itself a certificate key.
- Do not use `ghcr.io/opentofu/opentofu` as a base for custom images on 1.10 or later.

## Breaking backend changes

### Remove the legacy S3 credential switch

The S3 backend changed to standard AWS CLI/SDK credential precedence in 1.7. Its temporary `use_legacy_workflow = true` compatibility switch was removed in 1.8. Delete the argument before upgrading and verify which credential source wins.

S3 module sources adopt the same standard discovery in 1.11. This may silently select a different source, while enabling mechanisms such as IAM roles for service accounts.

### Do not mix PostgreSQL locking generations

OpenTofu 1.10 uses finer-grained PostgreSQL backend locks. Never run it alongside older OpenTofu processes against the same database: incompatible locking can allow conflicting writes and data loss. Use `table_name` and `index_name` to isolate states where appropriate.

### Reconfigure AzureRM authentication

OpenTofu 1.11 ignores deprecated `endpoint`/`ARM_ENDPOINT` and `msi_endpoint`/`ARM_MSI_ENDPOINT`. Replace the latter with `MSI_ENDPOINT`, avoid combining `environment` with `metadata_host`, and refresh the working directory with:

```bash
tofu init -reconfigure
```

Do not use `-migrate-state` for this authentication-only change.

## State and plan encryption

### Configure both artifacts deliberately

Wire a key provider to a method, then select the method independently for `state` and `plan`. Encryption inputs must be resolvable during initialization unless using the apply-time input support added later.

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

`TF_ENCRYPTION` contains the body of the `encryption` block and merges over configuration. `enforced = true` prevents plaintext output when an expected method is missing.

### Migrate with fallbacks and stable names

Make the new method primary and the old encrypted or plaintext representation a fallback. Reads try fallbacks; writes always use the primary, so a successful write performs migration. Reverse the arrangement to decrypt intentionally.

Do not casually rename key providers or methods because encrypted metadata records their names. Use a staged fallback or a stable `encrypted_metadata_alias`. Configure `terraform_remote_state` decryption separately from the current project's state.

## Initialization-time configuration

### Keep early-evaluated values static

Module `source` and `version`, plus backend arguments, may use variables and locals. Their dependency graph must be available during initialization and cannot rely on provider-defined functions or state data. Sensitive values cannot appear in backend configuration or module source locations.

```hcl
variable "module_source" {
  type  = string
  const = true
}

module "network" {
  source = var.module_source
}
```

Use `const = true` when an input is part of the static initialization contract. An OpenTofu-specific `.tofu` file masks the same-named `.tf` file, allowing an OpenTofu form plus a Terraform-compatible fallback.

## Lifecycle and refactoring

### Prefer explicit lifecycle controls

Use `lifecycle.enabled` for resources or modules that should have zero or one instance. It is clearer than conditional `count`, but a module with local provider configurations rejects `enabled` from 1.11.4.

```hcl
module "servers" {
  source = "./servers"

  lifecycle {
    enabled = var.enable_servers
  }
}
```

In OpenTofu 1.12, `prevent_destroy` can depend on module symbols and managed resources can use `lifecycle { destroy = false }` to remove an object from state without destroying it. Use 1.12.4+ when saving a plan that might replace such a resource.

### Refactor declaratively

- Cross-type `moved` blocks can ask providers to migrate state between resource types.
- `removed` blocks may include lifecycle and provisioner configuration.
- An `import` block can use provider-defined `identity` data instead of only a string `id`.
- `replace_triggered_by` now reacts when its referenced resource is itself being replaced.

## Ephemeral and write-only data

OpenTofu 1.11 supports ephemeral variables, outputs, and provider-defined resources. Their values live only in memory for one operation phase and are not stored in plans or state. Provider-defined write-only resource attributes accept secrets without persisting a copy. Both features require provider schema support.

Inputs supplied during apply may configure encryption. Every non-ephemeral input must still equal the value recorded during planning.

## Expressions and provider selection

- Provider functions use `provider::<provider_name>::<function>(...)` and may depend on provider configuration.
- Aliased provider configurations can use `for_each`; resources and modules select instances dynamically.
- `&&` and `||` short-circuit, so a skipped operand cannot fail while dereferencing a null value.
- `element(collection, -1)` selects the final item using wrapped negative indexing.
- A module `version = null` behaves as if the argument were omitted.
- `yamldecode` supports `<<` merge tags whose value is a sequence of mappings.

## Planning and automation

### Select work explicitly

`-exclude=ADDRESS` omits the object and its dependents, complementing `-target`, which selects an object and its requirements. Use `-target-file` and `-exclude-file` for reusable address lists.

```bash
tofu plan -target-file=targets.txt
tofu plan -exclude-file=deferred.txt
```

### Separate human and machine output

- `-concise` removes refresh or progress-like noise from plan and apply while preserving final results.
- `-json-into=FILE` retains normal terminal output and writes the JSON event stream separately.
- `tofu show -json -config [-module=DIR]` inspects configuration without first creating a plan.
- `-show-sensitive` deliberately unmasks sensitive output; use it only where disclosure is acceptable.

## Testing essentials

- Use `mock_provider`, `mock_resource`, and `mock_data` for provider-level fakes.
- Use `override_resource`, `override_data`, and `override_module` for targeted values; overrides can be scoped inside a mock provider.
- `mock_provider` supports `for_each`; test-file variable blocks can call functions.
- Generated mocks follow provider schemas more closely, and invalid mock or override fields are errors. Fix stale shapes instead of relying on permissive validation.
- When cleanup fails, `tofu test` writes state so remaining resources can be recovered and managed.

Read [testing-and-go-tooling.md](references/testing-and-go-tooling.md) before upgrading a test suite, because variable scope, provider references, mock validation, and remote modules have version-dependent behavior.
