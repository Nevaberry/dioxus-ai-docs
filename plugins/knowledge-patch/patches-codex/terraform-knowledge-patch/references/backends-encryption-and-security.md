# Backends, Encryption, Installation, and Security

## S3 credentials and locking

Terraform 1.7 changes the S3 backend's default `use_legacy_workflow` to `false`, following AWS SDK and CLI default-provider-chain order (`terraform-1.7.0`). The `true` compatibility setting temporarily restores the old order but is deprecated. OpenTofu 1.8 removes the argument entirely (`opentofu-1.8.0`).

Terraform 1.10 removes deprecated flat assume-role attributes; put them in an `assume_role` block (`terraform-1.10.0`). It also adds native S3 state locking. When native and DynamoDB locking are both configured, both locks are acquired.

Terraform 1.11 deprecates DynamoDB locking arguments. Migrate to S3-native lock files, using both mechanisms only during transition (`terraform-1.11.0`).

```hcl
terraform {
  backend "s3" {
    bucket       = "example-state"
    key          = "prod/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}
```

Terraform 1.15 accepts credentials established by `aws login`. It strictly parses `AWS_USE_FIPS_ENDPOINT` and `AWS_USE_DUALSTACK_ENDPOINT` as `true` or `false`; other non-empty strings no longer mean true (`terraform-1.15.0`).

OpenTofu 1.10 makes `skip_s3_checksum` disable the AWS SDK's default S3 integrity checks too; this helps incomplete S3-compatible servers at the cost of verification. Use 1.10.2 or later when lockfiles require the configured server-side-encryption header (`opentofu-1.10.0`).

OpenTofu 1.11 S3 module sources follow AWS CLI/SDK credential search, including IAM roles for service accounts, so an upgrade can select a different credential. The S3 backend can tag state and lock objects and supports `eusc-de-east-1` (`opentofu-1.11.0`).

OpenTofu 1.12 honors plaintext HTTP for `s3::http://` module sources unless the origin is an official AWS hostname; older releases ignored the scheme and used HTTPS (`opentofu-1.12.0`).

## Azure backends

OpenTofu 1.9 adds AzureRM `timeout_seconds`, defaulting to 300 seconds (`opentofu-1.9.0`).

```hcl
terraform {
  backend "azurerm" {
    timeout_seconds = 600
  }
}
```

Terraform 1.11 adds Azure backend `use_cli`, `use_aks_workload_identity`, `client_id_file_path`, `client_certificate`, and `client_secret_file_path`. Terraform 1.11.2 refreshes Azure DevOps Pipelines OIDC tokens with `ado_pipeline_service_connection_id` plus `oidc_request_url` and `oidc_request_token`; `subscription_id` becomes optional if no management-plane call is required.

OpenTofu 1.11 ignores deprecated `endpoint`/`ARM_ENDPOINT` and `msi_endpoint`/`ARM_MSI_ENDPOINT`; use `MSI_ENDPOINT`, and do not combine `environment` with `metadata_host`. Reinitialize with `tofu init -reconfigure`, not `-migrate-state`. New authentication fields include `use_cli` (default true), `use_aks_workload_identity`, `client_id_file_path`, `client_secret_file_path`, and inline `client_certificate`. Use 1.11.3 or later for refreshed Azure DevOps OIDC tokens and 1.11.5 or later for MSI to honor an explicit client ID.

## Other backends and locks

Terraform 1.12 adds an OCI Object Storage backend (`terraform-1.12.0`).

OpenTofu 1.10 `pg` backends accept `table_name` and `index_name` and use finer-grained locks. Never mix 1.10 and older OpenTofu processes in one database: their lock protocols are incompatible and can permit conflicting writes and data loss.

OpenTofu 1.10 makes `tofu force-unlock LOCK_ID` work with the HTTP backend and makes the `oss` backend honor standard HTTP/HTTPS proxy variables, including `NO_PROXY`.

OpenTofu 1.11.5 adds the GCS backend `universe_domain` option for sovereign GCP services. OpenTofu 1.12 adds `-lock=false` and `-lock-timeout=DURATION` to `tofu console`; an interrupted HTTP-backend apply also releases its state lock correctly.

```shell
tofu console -lock-timeout=30s
```

Terraform 1.15.0 briefly made `terraform validate` check required and backend-specific attributes inside backend blocks. Terraform 1.15.1 removed attribute validation because configurations can be completed through `-backend-config`; structural validation still applies.

## OpenTofu state and plan encryption (`opentofu-1.7.0`)

OpenTofu can encrypt local or backend state and saved plans at rest with AES-GCM. Initial key providers include PBKDF2, AWS KMS, GCP KMS, and OpenBao. Encryption does not prevent state loss, replay of old artifacts, or disclosure to the `tofu` process.

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "state" {
      passphrase = var.state_passphrase
    }
    method "aes_gcm" "state" {
      keys = key_provider.pbkdf2.state
    }
    state {
      method   = method.aes_gcm.state
      enforced = true
    }
    plan {
      method   = method.aes_gcm.state
      enforced = true
    }
  }
}
```

Encryption variables and locals must resolve during `tofu init`; they cannot depend on state data or provider-defined functions.

### Migration and rollover

Once encryption is enabled, existing plaintext is rejected unless an `unencrypted` fallback is explicit. Reads try the primary method then fallbacks; writes always use the primary. Back up state and keys, configure the old or plaintext method as fallback, apply to rewrite the artifact, and only then remove the fallback and enforce encryption. OpenTofu 1.7.7 automatically applies encryption-configuration migrations.

```hcl
method "unencrypted" "migrate" {}

state {
  method = method.aes_gcm.state
  fallback {
    method = method.unencrypted.migrate
  }
}
```

### Environment and remote state

`TF_ENCRYPTION` supplies an encryption block body, merges with checked-in configuration, and takes precedence. Keep `enforced = true` for state and plan in configuration so a missing environment variable cannot silently write plaintext.

Encrypted `terraform_remote_state` consumers need their own mapping under `remote_state_data_sources`; use `default` for all consumers or named mappings for different methods.

```hcl
remote_state_data_sources {
  default {
    method = method.aes_gcm.state
  }
}
```

## Encryption extensions

OpenTofu 1.9 key providers accept `encrypted_metadata_alias` (`opentofu-1.9.0`). OpenTofu 1.10 adds external-program key providers and PBKDF2 `chain`, integrating key sources not implemented in-process. OpenTofu 1.11 adds `azure_vault` for Azure Key Vault. Apply may receive encryption input values, but every non-ephemeral value must equal the plan-time value; 1.11.4 JSON encryption configuration accepts both expression syntax and template interpolation for keys.

## Provider and module distribution

Terraform 1.8 `terraform providers lock -enable-plugin-cache` can reuse packages in the configured global plugin cache (`terraform-1.8.0`). Release archives include the license from 1.8.2, so extraction scripts that expect one file should name it explicitly:

```shell
unzip terraform_1.8.2_linux_amd64.zip terraform
```

Terraform 1.11 uses matching `.netrc` credentials for provider package downloads and checksum URLs returned by registries. Its official container image includes `ca-certificates`.

When combined provider constraints both select and exclude the same prerelease, Terraform 1.9 gives the negative constraint precedence. For example, `1.2.0-beta.1, !1.2.0-beta.1` excludes that version. Terraform 1.13 `init` succeeds when a constraint has at least one valid matching provider version (`terraform-1.13.0`).

Terraform 1.15 `init` skips providers covered by development overrides but still installs dependencies that those overrides do not supply.

OpenTofu 1.10 supports `oci:` module sources and OCI provider mirrors. Multiple processes coordinate global provider-cache access on locking filesystems; use 1.10.5 or later with `TF_PLUGIN_CACHE_DIR` and keep a valid lockfile because earlier patch releases can report lock contention.

When a lockfile names certain `registry.terraform.io` providers, OpenTofu only seeks an equivalent at `registry.opentofu.org` for providers rebuilt and republished by the OpenTofu project. Use 1.10.2 or later when explicitly retaining the Terraform hostname. For unsigned provider ZIPs, OpenTofu records a locally verified `zh:` archive checksum alongside `h1:`.

OpenTofu 1.11 moves registry retry counts and timeouts into CLI configuration. OpenTofu 1.12 initialization from OpenTofu Registry records official `zh:` and `h1:` hashes for all supported platforms, which may add many lockfile entries. `tofu providers lock` remains useful with alternative installation sources; a `network_mirror` can opt to trust every hash it reports. Private module registries can tell clients to reuse registry API credentials for package downloads.

OpenTofu 1.9 deprecates using `ghcr.io/opentofu/opentofu` as a custom-image base and 1.10 removes it; migrate derived images to the supported custom-image process.

## Platform boundaries

- Terraform 1.12 requires Linux kernel 3.2 or later.
- Terraform 1.14 builds require macOS Monterey or later because the release uses Go 1.25.
- Terraform 1.15 adds Windows ARM64 builds, 1.15.4 adds Linux s390x, and SSH `file` and `remote-exec` provisioners again support PowerShell targets.
- OpenTofu 1.10 requires macOS 11 or later. On Windows, only true symbolic links count as symlinks; a `TEMP` path traversing directory junctions can fail.
- OpenTofu 1.11 requires macOS 12 or later. On Windows, `tofu.rc` precedes `terraform.rc`; empty quoted values in `TF_CLI_ARGS*` become zero-length arguments, and sensitive prompts locate `stty` through `PATH`.
- OpenTofu 1.12 is the last planned macOS 12 line. WinRM provisioners warn on every use ahead of expected removal in 1.13; migrate to SSH. Official 32-bit `386` and `arm` packages remain through at least 1.13 but are planned for later removal.

## Security and observability

Terraform 1.7 updates SSH dependencies to mitigate CVE-2023-48795 for `local-exec` and `file` provisioner connections.

Terraform 1.9.1 updates module fetching for CVE-2024-6257; 1.9.3 includes fixes for CVE-2024-6104 and CVE-2024-24791 through HTTP and Go dependency updates (`terraform-1.9.0`).

OpenTofu 1.9 HTTP backend trace logging includes request and response bodies. Treat trace logs as state- and credential-bearing. `-show-sensitive` likewise exposes masked values and requires secret-safe handling.

OpenTofu 1.10 initialization tracing is experimental and initially covers only `tofu init`; use 1.10.6 or later because earlier telemetry failures could panic. Use 1.10.9 or later for fixes covering malicious tar files, pathological certificate chains, wildcard constraints, certificate-error CPU exhaustion, unbounded query parsing, and TLS message boundaries. The 1.10.7 HTTPS fixes do not update HTTP stacks embedded in provider plugins.

OpenTofu 1.11 rejects SHA-1 TLS handshake signatures and SSH remote-provisioner certificates whose signature key is itself a certificate key. Use 1.11.4 or later against malicious provider or module ZIPs and at least 1.11.2 when Helm or Kubernetes provider configuration contains irrelevant plan-time unknowns.

OpenTofu 1.12 removes `OPENTOFU_USER_AGENT`, so integrations cannot globally replace the default HTTP User-Agent. On Unix, `tofu login` honors `BROWSER` only when it names one command that accepts the URL as its sole argument; unset it to restore platform-default launching.

Terraform 1.15.9 mitigates CVE-2026-14978, where Unicode normalization could cause `.terraformignore`-excluded files to be uploaded to HCP Terraform or Terraform Enterprise (`terraform-1.15.9`). Upgrade when ignored files must not leave the working directory.
