# Backends, Encryption, Installation, and Security

## S3 backend migrations

### Credential chain and legacy workflow

Terraform's S3 backend defaults `use_legacy_workflow` to `false` and searches
credentials in AWS SDK and CLI default-chain order. Setting the switch to
`true` temporarily restores the earlier ordering, but the switch is deprecated
(`terraform-1.7.0`). OpenTofu removes `use_legacy_workflow`; delete it before
upgrading (`opentofu-1.8.0`).

OpenTofu S3 module sources also adopt AWS CLI and SDK credential lookup,
including newer methods such as IAM roles for service accounts, so an upgrade
can select different credentials (`opentofu-1.11.0`).

### Assume-role and endpoint settings

Terraform removes deprecated flat assume-role attributes. Put the values in
an `assume_role` block (`terraform-1.10.0`). Terraform's S3 backend can also
use credentials established by `aws login`; `AWS_USE_FIPS_ENDPOINT` and
`AWS_USE_DUALSTACK_ENDPOINT` accept only `true` or `false`, not arbitrary
non-empty values (`terraform-1.15.0`).

### Native state locks

Terraform S3-native locking can coexist with DynamoDB locking, in which case
both locks are acquired (`terraform-1.10.0`). DynamoDB-related S3 arguments
are deprecated; migrate to `use_lockfile = true` and use dual locking only as
a temporary bridge (`terraform-1.11.0`).

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

### Compatibility with S3-like services

OpenTofu's `skip_s3_checksum` also disables the AWS SDK's default integrity
checks, improving compatibility with incomplete implementations at the cost
of those checks. Use OpenTofu 1.10.2 or later when lock objects need the
configured server-side-encryption header (`opentofu-1.10.0`).

OpenTofu's S3 backend can tag state and lock objects and supports
`eusc-de-east-1` (`opentofu-1.11.0`). An OpenTofu `s3::http://` module source
uses plaintext HTTP unless it targets an official AWS hostname
(`opentofu-1.12.0`).

## OpenTofu state and plan encryption

### Initial configuration

OpenTofu can encrypt local or backend state and saved plans with AES-GCM,
using PBKDF2, AWS KMS, GCP KMS, or OpenBao key providers
(`opentofu-1.7.0`). Encryption does not prevent artifact loss, replay, or
disclosure to the running process.

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

Encryption inputs may use variables and locals only when they resolve during
`tofu init`; they cannot depend on state data or provider functions.

### Plaintext migration and key rotation

Back up both artifacts and keys. Enabling encryption rejects existing
plaintext unless `unencrypted` is an explicit fallback. Reads try the primary
method and then fallbacks; writes always use the primary. Apply once to rewrite
artifacts before removing the fallback and enforcing encryption. Use the same
sequence for key or method rotation. OpenTofu 1.7.7 automatically applies
encryption-configuration migrations (`opentofu-1.7.0`).

```hcl
method "unencrypted" "migrate" {}

state {
  method = method.aes_gcm.state
  fallback {
    method = method.unencrypted.migrate
  }
}
```

### Environment and remote-state consumers

`TF_ENCRYPTION` contains an encryption-configuration body, merges with code,
and takes precedence. Keep `state { enforced = true }` and
`plan { enforced = true }` in code so a missing environment variable cannot
silently write plaintext. Consumers of encrypted `terraform_remote_state`
must configure `remote_state_data_sources`, with a `default` mapping or named
mappings for alternate methods (`opentofu-1.7.0`).

### Later key providers and metadata

- Encryption key providers accept `encrypted_metadata_alias`
  (`opentofu-1.9.0`).
- External programs can supply keys, and PBKDF2 supports chaining
  (`opentofu-1.10.0`).
- `azure_vault` can source a key from Azure Key Vault. Apply-time encryption
  inputs are accepted, but each non-ephemeral input must equal its plan-time
  value; 1.11.4 accepts expression syntax or template interpolation for keys
  in JSON encryption configuration (`opentofu-1.11.0`).

## AzureRM and other backends

### AzureRM timeouts and authentication

OpenTofu's AzureRM backend accepts `timeout_seconds`, defaulting to 300
seconds (`opentofu-1.9.0`).

Terraform adds `use_cli`, `use_aks_workload_identity`, `client_id_file_path`,
`client_certificate`, and `client_secret_file_path`. Terraform 1.11.2 refreshes
Azure DevOps Pipelines OIDC tokens using
`ado_pipeline_service_connection_id`, `oidc_request_url`, and
`oidc_request_token`; it also makes `subscription_id` optional where no
management API call is needed (`terraform-1.11.0`).

OpenTofu ignores deprecated `endpoint`/`ARM_ENDPOINT` and
`msi_endpoint`/`ARM_MSI_ENDPOINT`; use `MSI_ENDPOINT`, do not combine
`environment` with `metadata_host`, and reinitialize with
`tofu init -reconfigure`, not `-migrate-state`. Its backend adds `use_cli`
(default true), `use_aks_workload_identity`, client ID and secret file paths,
and inline certificates. Use 1.11.3 for refreshed Azure DevOps OIDC tokens and
1.11.5 for MSI to honor an explicit client ID (`opentofu-1.11.0`).

### OCI, GCS, OSS, HTTP, and PostgreSQL

- Terraform supports OCI Object Storage as a backend
  (`terraform-1.12.0`).
- OpenTofu's GCS backend adds `universe_domain` in 1.11.5 for sovereign GCP
  services (`opentofu-1.11.0`).
- OpenTofu's OSS backend honors HTTP and HTTPS proxy variables, including
  `NO_PROXY` (`opentofu-1.10.0`).
- `tofu force-unlock LOCK_ID` works with the HTTP backend
  (`opentofu-1.10.0`). An interrupted HTTP-backed apply releases its lock, and
  `tofu console` accepts `-lock=false` and `-lock-timeout=DURATION`
  (`opentofu-1.12.0`).
- OpenTofu PostgreSQL backends accept `table_name` and `index_name` and use
  finer-grained locks. New and old lock implementations must not share a
  database (`opentofu-1.10.0`).

### Validation boundary

Terraform 1.15.0 made `terraform validate` check backend blocks and their
required and backend-specific attributes. Terraform 1.15.1 stopped validating
attributes inside backend blocks because configurations may be completed with
`-backend-config` (`terraform-1.15.0`). Terraform 1.15.9 still diagnoses
invalid backend and cloud blocks in child modules (`terraform-1.15.9`).

The Terraform `-state` flag on `plan`, `apply`, and `refresh` is deprecated.
Configure a local backend path instead (`terraform-1.10.0`).

## Provider and module installation

### Package caches and lock files

Terraform `providers lock -enable-plugin-cache` can reuse a configured global
plugin cache (`terraform-1.8.0`). Terraform 1.14.1 includes providers required
only by tests when generating locks (`terraform-1.14.0`).

OpenTofu coordinates concurrent access to the global provider cache on
filesystems with locking. Use 1.10.5 or later with `TF_PLUGIN_CACHE_DIR` and
retain valid lock files; earlier releases can still report contention errors
(`opentofu-1.10.0`).

When OpenTofu installs directly from its registry, it records official `zh:`
and `h1:` hashes for all supported platforms. This can add many `h1:` entries
and usually removes the need for a separate `tofu providers lock`; that command
still matters with alternate installation sources. A `network_mirror` can
trust every hash reported by the mirror (`opentofu-1.12.0`).

For unsigned provider archives, OpenTofu records a locally verified `zh:`
archive checksum alongside `h1:` content checksums (`opentofu-1.10.0`).

### Registry and artifact authentication

Terraform uses matching `.netrc` credentials for provider download and
checksum URLs returned by registries (`terraform-1.11.0`). OpenTofu private
module registries can declare that package downloads reuse registry API
credentials (`opentofu-1.12.0`).

When combined Terraform provider requirements both select and exclude the same
prerelease, the negative constraint wins (`terraform-1.9.0`). Terraform
initialization succeeds when a provider constraint has at least one valid
matching provider version (`terraform-1.13.0`).

OpenTofu module sources and provider mirrors support `oci:` distribution
(`opentofu-1.10.0`). When migrating a lock file from
`registry.terraform.io`, OpenTofu selects a corresponding
`registry.opentofu.org` package only for providers rebuilt and republished by
the OpenTofu project. Use 1.10.2 when retaining the Terraform registry hostname
explicitly (`opentofu-1.10.0`).

OpenTofu registry retries and timeouts are configurable in CLI configuration;
it also supports sovereign-cloud discovery where the selected service offers
it (`opentofu-1.11.0`).

Terraform `init` skips providers covered by development overrides but installs
other dependencies (`terraform-1.15.0`).

### Images and release archives

Terraform release archives include a license file starting in 1.8.2. Scripts
that expect only the executable should name it explicitly while extracting
(`terraform-1.8.0`). The official Terraform image includes `ca-certificates`
(`terraform-1.11.0`).

The `ghcr.io/opentofu/opentofu` derived-image base workflow is deprecated in
OpenTofu 1.9 and removed in 1.10; use the supported custom-image process
(`opentofu-1.9.0`).

## Security and platform boundaries

### Trace and output handling

OpenTofu HTTP backend trace logs include request and response bodies and can
contain state or authentication data. Restrict collection and retention
(`opentofu-1.9.0`). The `-show-sensitive` flag also makes plan and apply output
secret-bearing (`opentofu-1.9.0`).

### Security patch floors

- Terraform 1.7 incorporates the upstream mitigation for CVE-2023-48795 in
  SSH used by remote `local-exec` and `file` provisioners
  (`terraform-1.7.0`).
- Terraform 1.9.1 updates module fetching for CVE-2024-6257; 1.9.3 incorporates
  CVE-2024-6104 and CVE-2024-24791 fixes (`terraform-1.9.0`).
- OpenTofu 1.10.9 includes fixes for malicious tar archives, pathological TLS
  certificate chains, wildcard constraints, certificate-error CPU use,
  unbounded query parsing, and TLS message boundaries. The 1.10.7 HTTPS fixes
  do not update transport code embedded in provider plugins
  (`opentofu-1.10.0`).
- OpenTofu rejects TLS SHA-1 signatures and SSH provisioner certificates whose
  signature key is itself a certificate key. Use 1.11.4 for malicious ZIP
  processing and 1.11.2 when unused Helm or Kubernetes configuration contains
  plan-time unknowns (`opentofu-1.11.0`).
- Terraform 1.15.9 mitigates CVE-2026-14978, where Unicode normalization could
  upload files excluded by `.terraformignore` to HCP Terraform or Terraform
  Enterprise (`terraform-1.15.9`).

OpenTofu initialization tracing is experimental and initially covers only
`tofu init`; use 1.10.6 or later so telemetry failures warn rather than panic
(`opentofu-1.10.0`).

### Host and provisioner requirements

- Terraform requires Linux kernel 3.2 or later (`terraform-1.12.0`). Building
  Terraform 1.14 requires macOS Monterey or later because it uses Go 1.25
  (`terraform-1.14.0`). Terraform 1.15 adds Windows ARM64, 1.15.4 adds Linux
  s390x, and SSH `file` and `remote-exec` support PowerShell again
  (`terraform-1.15.0`).
- OpenTofu 1.10 requires macOS 11 or later. On Windows only true symbolic links
  count, so a `TEMP` path through directory junctions can fail
  (`opentofu-1.10.0`). OpenTofu 1.11 requires macOS 12; on Windows `tofu.rc`
  takes precedence over `terraform.rc`, empty quoted `TF_CLI_ARGS` values are
  zero-length arguments, and sensitive prompts locate `stty` through `PATH`
  (`opentofu-1.11.0`).
- OpenTofu 1.12 warns on each WinRM `remote-exec` or `file` connection in
  preparation for removal. It is the last planned macOS 12 line; official
  32-bit `386` and `arm` packages continue through at least 1.13 but are
  planned for later removal (`opentofu-1.12.0`).

`OPENTOFU_USER_AGENT` is removed, so integrations cannot replace the default
User-Agent globally. On Unix, `tofu login` honors `BROWSER` only when it names
a single command that accepts the URL as its sole argument
(`opentofu-1.12.0`).
