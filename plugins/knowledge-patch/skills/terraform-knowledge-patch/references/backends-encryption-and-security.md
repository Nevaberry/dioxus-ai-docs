# Backends, Encryption, Installation, and Security

Backend migrations and authentication, state encryption, package installation, security updates, and supported platforms.

## S3 and object-storage backends

### Additional OSS backend environment variables

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

The `oss` backend accepts more of the standard environment variables used by the corresponding provider, allowing backend authentication and configuration to reuse provider-style environment settings.

### Backend validation and S3 authentication changes

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

`terraform validate` now checks that the configured backend type exists, required backend attributes are present, and backend-specific validation succeeds. The S3 backend can authenticate through `aws login`; after upgrading, `AWS_USE_FIPS_ENDPOINT` and `AWS_USE_DUALSTACK_ENDPOINT` must contain `true` or `false`, and other non-empty values are no longer interpreted as true.

### Cross-platform provider checksums

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

When installing from a registry, `tofu init` now records the full set of supported-platform `zh:` and `h1:` provider hashes, so the first initialization after upgrade can add many `h1:` entries to `.terraform.lock.hcl`. A separate `tofu providers lock` is generally needed only when initialization uses an alternative installation source; a `network_mirror` can also opt to trust all hashes reported by that mirror.

### Module-source HTTP handling

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

An `s3::http://` module source now uses plaintext HTTP for non-AWS origins; official AWS hostnames retain their special handling. Earlier releases silently changed any URL using the `s3` source type to HTTPS.

### Native S3 state locking

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

The S3 backend can lock state directly in S3 without a DynamoDB table by enabling `use_lockfile`. Use 1.10.2 or later when lock files require S3 server-side encryption, because that release fixes the missing `x-amz-server-side-encryption` header.

```hcl
terraform {
  backend "s3" {
    use_lockfile = true
  }
}
```

### OCI Object Storage backend

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

Terraform now includes a backend implementation for storing state in OCI Object Storage.

### S3 backend credential-chain default

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

The S3 backend now defaults `use_legacy_workflow` to `false` and searches for credentials in the same order as AWS SDKs and the AWS CLI. Setting `use_legacy_workflow = true` temporarily restores the old order, but the option and legacy workflow are deprecated for removal in a future minor release.

### S3 legacy credential workflow removed

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

The S3 backend no longer accepts `use_legacy_workflow`; remove this temporary legacy credential-chain setting before upgrading to OpenTofu 1.8.

### S3 locking migration away from DynamoDB

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

Terraform 1.11 deprecates the S3 backend's DynamoDB-related locking arguments in favor of `use_lockfile`, the argument for native lock files.

### S3 module and state behavior

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

S3 module-package installation now follows the AWS CLI and SDK credential search order, which can select a different credential source after upgrade and adds support for schemes such as IAM roles for service accounts. The S3 backend can tag state and lock objects and can use the `eusc-de-east-1` European Sovereign Cloud region.

### S3 role assumption and native locking

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

The S3 backend removes its deprecated assume-role attributes; role-assumption settings must now use the `assume_role` block. It also supports S3-native state locking, acquires both S3 and DynamoDB locks when both mechanisms are configured, and requires at least 1.10.1 to write lock files to buckets with Object Lock enabled.

### Security updates across the 1.8 line

*OpenTofu 1.8.0 — batch `opentofu-1.8.0`.*

OpenTofu 1.8.0 updates the module getter for CVE-2024-6257, with a possible slowdown for large modules. Releases 1.8.2, 1.8.8, and 1.8.9 add Go toolchain and networking/cryptography fixes for CVE-2024-24790, CVE-2024-45336, CVE-2024-45337, CVE-2024-45338, CVE-2024-45341, and CVE-2025-22866.

## Other backends and state encryption

### AzureRM backend migration and authentication

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

The `azurerm` backend adds `use_cli` (default `true`), `use_aks_workload_identity` (default `false`), `client_id_file_path`, `client_secret_file_path`, and `client_certificate`. It now ignores the deprecated `endpoint`/`ARM_ENDPOINT` and `msi_endpoint`/`ARM_MSI_ENDPOINT` settings, uses `MSI_ENDPOINT` instead, and makes `environment` mutually exclusive with `metadata_host`; update an initialized backend with `tofu init -reconfigure`, not `-migrate-state`.

OpenTofu 1.11.3 dynamically refreshes Azure DevOps OIDC tokens, and 1.11.5 makes MSI authentication honor the configured client ID.

### Backend and encrypted initialization controls

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

The AzureRM backend adds `timeout_seconds`, defaulting to 300 seconds, while HTTP backend trace logs now include request and response bodies. `tofu init -backend=false` no longer tries to read state-encryption keys.

### Backend compatibility

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

The HTTP backend accepts user-defined headers, with `Authorization` propagation fixed in 1.7.2. The S3 backend again honors lowercase `http_proxy` and `https_proxy` from 1.7.3 and no longer requires permission to use the default `env:` workspace prefix.

### Backend compatibility controls

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

For the S3 backend, `skip_s3_checksum` now also disables the AWS SDK's default integrity checks, improving compatibility with incomplete S3-compatible implementations. The HTTP backend supports `tofu force-unlock`, and the OSS backend now honors standard proxy variables including `NO_PROXY`.

### Encryption configuration additions

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

The new `azure_vault` key provider can source state and plan encryption keys from Azure Key Vault. Apply-time input values can now configure encryption as long as every non-ephemeral variable still matches the value used during planning; starting in 1.11.4, JSON-form encryption method keys accept either normal expression syntax or template interpolation.

### Encryption helper compatibility

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

JSON encryption configuration now accepts direct quoted references in `key_provider` expressions as well as template interpolation. An external key-provider program consistently receives JSON `null` when OpenTofu requests only the encryption key.

### Encryption providers and constraints

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

OpenTofu 1.7's AES-GCM method requires 16-, 24-, or 32-byte keys and should use key derivation or regular KMS rotation to avoid key saturation. Its initial key providers are PBKDF2 (minimum 16-character passphrase; defaults of a 32-byte key, 600,000 iterations, 32-byte salt, and SHA-512), AWS KMS (`kms_key_id` and `key_spec`, with S3-backend authentication), GCP KMS (`kms_encryption_key` and `key_length`, with GCS-backend authentication), and OpenBao Transit (`key_name`, with `BAO_TOKEN`/`BAO_ADDR` support). The OpenBao provider is compatible with Vault 1.14 but not later BUSL releases.

Documented encryption methods and key providers are guaranteed for only one additional minor release. A deprecation warning during `plan` or `apply` means the configuration should migrate before the following upgrade.

### Encryption rollover and rollback

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

To rotate a passphrase, key provider, or method, make the new method primary and place the old method in `fallback`: reads try both, while writes always use the new method. Provider and method names are stored in encrypted metadata, so do not rename them directly; `encrypted_metadata_alias` gives a key provider a stable metadata name. To remove encryption, make `unencrypted` primary and retain the encrypted method as fallback until the data has been rewritten. Starting in 1.7.7, encryption-configuration changes automatically apply their migration.

### Expanded Azure backend authentication

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

The Azure backend adds `use_cli`, `use_aks_workload_identity`, `client_id_file_path`, `client_certificate`, and `client_secret_file_path` as it aligns with AzureRM provider authentication. Starting in 1.11.2, Azure DevOps Pipelines OIDC token refresh can use `oidc_request_url`, `oidc_request_token`, and the new `ado_pipeline_service_connection_id`; `subscription_id` is also optional in some setups, avoiding an unnecessary management-plane API call.

### External and chained state-encryption keys

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

State encryption can obtain keys from external programs, and the PBKDF2 key provider adds a `chain` parameter for deriving a new key from another provider. Configurations with multiple key providers and methods now load only those needed for the current operation, including when decrypting `terraform_remote_state` data.

### PostgreSQL backend state partitioning and upgrade boundary

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

The `pg` backend accepts `table_name` and `index_name`, allowing multiple states in one database and more granular locking between configurations. Do not let OpenTofu 1.10 and older OpenTofu versions use the `pg` backend in the same database: the locking implementations are incompatible and concurrent writes can cause data loss.

### Registry and backend authentication

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

Module registries can tell OpenTofu to reuse registry API credentials for package downloads, avoiding a separate `.netrc` entry when the registry serves its own packages. The S3 backend discovers credentials created by `aws login`, and the AzureRM backend supports Azure DevOps and Azure Pipelines workload identity federation.

### State and plan encryption

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

OpenTofu can encrypt local or backend state and saved plan files at rest through `terraform.encryption`; the same inner configuration can be supplied in `TF_ENCRYPTION`, which merges with configuration files and takes precedence over them. Encryption does not prevent state loss or replay attacks, and it cannot hide values from the person running `tofu`, so back up both the state and its keys before enabling it.

For an existing plaintext state, explicitly allow one migration read with the `unencrypted` method:

```hcl
variable "state_passphrase" {
  sensitive = true
}

terraform {
  encryption {
    key_provider "pbkdf2" "state" {
      passphrase = var.state_passphrase
    }
    method "aes_gcm" "state" {
      keys = key_provider.pbkdf2.state
    }
    method "unencrypted" "migrate" {}
    state {
      method = method.aes_gcm.state
      fallback { method = method.unencrypted.migrate }
    }
  }
}
```

Run `tofu apply` to rewrite the state, then remove the fallback and optionally set `enforced = true`; repeat the process in `plan {}` for saved plans. New projects omit the `unencrypted` method and fallback. Encryption variables and locals must resolve during `tofu init` and therefore cannot depend on state data or provider-defined functions.

## Provider and module installation

### Authenticated provider artifact downloads

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

`terraform init` now uses credentials configured in `.netrc` for provider download and checksum URLs returned by provider registries, allowing those artifact endpoints to require authentication.

### Concurrent global provider caching

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

When its filesystem supports locking, the global provider cache is safe for concurrent use by multiple OpenTofu processes. Shared `TF_PLUGIN_CACHE_DIR` users should use 1.10.5 or later to avoid a lock-contention bug and should keep valid `.terraform.lock.hcl` files in every project.

### Development-override initialization

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

`terraform init` skips dependencies that are declared in development overrides while still installing dependencies absent from those overrides, so provider development overrides no longer prevent normal dependency installation.

### Provider installation compatibility

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

Terraform 1.12.1 restores provider installation without sending `HEAD` requests, correcting the 1.12.0 regression for endpoints that cannot handle those requests.

### Provider locking can use the global plugin cache

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

`terraform providers lock -enable-plugin-cache` uses the configured global plugin cache while calculating provider locks, avoiding separate downloads during the lock operation.

### Provider migration and lock-file checksums

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

During `tofu init`, lock entries for selected `registry.terraform.io` providers can resolve to project-rebuilt equivalents on `registry.opentofu.org`; this mapping does not apply generally to third-party providers. For unsigned provider-package sources, OpenTofu also records the locally verified archive's `zh:` checksum alongside `h1:`, improving verification when reinstalling the same package from another source; use 1.10.2 or later when configurations explicitly retain the original registry hostname.

### Registry and sovereign-cloud controls

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

Registry retry counts and request timeouts can now be set in CLI configuration instead of only through environment variables. Starting in 1.11.5, the GCS backend accepts `universe_domain` for sovereign Google Cloud services.

### Release archive layout changed in 1.8.2

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

Packaged releases now include a license file alongside the Terraform binary. Extraction scripts that expect only the binary should name it explicitly, for example `unzip terraform_1.8.2_linux_amd64.zip terraform`.

### Security and provider-function patch boundaries

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

OpenTofu 1.10.7 fixes denial-of-service risks from malicious module tar archives and pathological TLS certificate chains, while 1.10.8 and 1.10.9 add further TLS and query-parsing fixes; installations staying on 1.10 should therefore use at least 1.10.9. A fix for provider-defined functions used in an import block's `id` expression is listed for the still-unreleased 1.10.10.

## Security and platform boundaries

### CA certificates in the official container image

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

The official Terraform Docker image now includes the `ca-certificates` package for certificate handling in downstream images.

### Encrypted remote state

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

`remote_state_data_sources` configures decryption separately for `terraform_remote_state`: `default` supplies a common method, while `remote_state_data_source "name"` overrides one source. Override selectors may be `name`, `module.name`, or `module.name[0]`; matching `encrypted_metadata_alias` values let producer and consumer configurations use different local key-provider names.

### Linux kernel requirement

*Terraform 1.12.0 — batch `terraform-1.12.0`.*

Terraform 1.12 on Linux requires kernel 3.2 or later; support for older kernels has been removed.

### macOS source-build requirement

*Terraform 1.14.0 — batch `terraform-1.14.0`.*

Building Terraform 1.14 requires macOS Monterey or later because it is built with Go 1.25.

### OpenTofu 1.10 platform and image boundaries

*OpenTofu 1.10.0 — batch `opentofu-1.10.0`.*

Linux now requires kernel 3.2 or later and macOS requires version 11 Big Sur or later. The `ghcr.io/opentofu/opentofu` image is no longer supported as a base for custom images; on Windows, only true symbolic links count as symlinks, so a `TEMP` path traversing directory junctions may fail and should use directory symlinks instead.

### Platform, transport, and patch boundaries

*OpenTofu 1.11.0 — batch `opentofu-1.11.0`.*

OpenTofu now requires macOS 12 Monterey, rejects SHA-1 TLS signatures, and rejects malformed SSH certificates that use a certificate key as their own signature key. Use at least 1.11.4 when installing provider or module archives because it prevents excessive processing of maliciously crafted ZIP files; 1.11.3 also releases HTTP backend locks when an apply is interrupted.

The still-unreleased 1.11.6 also fixes `tofu apply -refresh-only` configurations containing ephemeral resources.

### Provisioner and platform deprecations

*OpenTofu 1.12.0 — batch `opentofu-1.12.0`.*

WinRM connections used by `remote-exec` and `file` provisioners warn in 1.12 and are expected to become errors in 1.13, so Windows targets should migrate to SSH. The 1.12 series is the last planned to support macOS 12; official 32-bit `386` and `arm` packages remain available throughout 1.12 and 1.13, but are planned for removal in a later series.

### Security update in 1.10.5

*Terraform 1.10.0 — batch `terraform-1.10.0`.*

Terraform 1.10.5 updates `github.com/hashicorp/go-slug` to 0.16.3 for CVE-2025-0377.

### Security update in 1.7.8

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

OpenTofu 1.7.8 updates its Go toolchain for CVE-2024-45336 and CVE-2024-45341 and also addresses GO-2024-2947 and GO-2024-2948.

### Security update in 1.8.4

*Terraform 1.8.0 — batch `terraform-1.8.0`.*

Terraform 1.8.4 updates `golang.org/x/net` to a release that addresses CVE-2023-45288.

### Security updates in the 1.9 line

*Terraform 1.9.0 — batch `terraform-1.9.0`.*

Terraform 1.9.1 updates the module getter for CVE-2024-6257, though `init` and `get` can become slower for large Git repositories. Terraform 1.9.3 also addresses CVE-2024-6104 and CVE-2024-24791 through dependency and toolchain updates.

### SSH provisioner security update

*Terraform 1.7.0 — batch `terraform-1.7.0`.*

Terraform 1.7.0 includes an upstream mitigation for CVE-2023-48795, which can affect `local-exec` and `file` provisioners that connect to remote hosts over SSH.

### Upgrade and security boundaries

*OpenTofu 1.9.0 — batch `opentofu-1.9.0`.*

The 1.9 release ends support for OpenTofu 1.6, so remaining 1.6 installations should upgrade to at least 1.7. Using `ghcr.io/opentofu/opentofu` as a custom image base is deprecated for removal in 1.10, and the 1.9.1 line records Go toolchain updates for CVE-2024-45336, CVE-2024-45341, and CVE-2025-22866.

### Windows platform and provisioner support

*Terraform 1.15.0 — batch `terraform-1.15.0`.*

Terraform now publishes Windows ARM64 builds, and SSH-based `file` and `remote-exec` provisioners support PowerShell again.

### Windows, TLS, and security compatibility

*Terraform 1.11.0 — batch `terraform-1.11.0`.*

Terraform 1.11.1 temporarily restores the earlier Windows symlink behavior for configurations using non-symlink junctions and updates `golang.org/x/oauth2` for CVE-2025-22868. Terraform 1.11.4 disables X25519Kyber768Draft00 in TLS to prevent timeouts with some AWS network firewalls.

### XDG directory support

*OpenTofu 1.7.0 — batch `opentofu-1.7.0`.*

OpenTofu now supports the XDG Base Directory Specification for user-level files, allowing its paths to follow XDG-configured locations.

