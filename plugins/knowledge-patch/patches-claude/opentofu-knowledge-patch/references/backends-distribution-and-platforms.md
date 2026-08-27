# Backends, distribution, and platforms

## S3 credentials and locking (`1.7.0`, `1.8.0`)

OpenTofu 1.7 changed the S3 backend default for `use_legacy_workflow` to `false`. Credential lookup follows AWS CLI/SDK precedence and prefers backend configuration over environment variables. The `true` setting was only a temporary compatibility escape hatch.

OpenTofu 1.8 removes `use_legacy_workflow` entirely. Remove it from backend configuration before upgrading and verify the credential source chosen by the standard workflow.

OpenTofu 1.10 adds native S3 state locking without DynamoDB. Use 1.10.2 or later if the bucket requires server-side encryption, because that patch sends the `x-amz-server-side-encryption` header for the lockfile.

OpenTofu 1.11 can tag S3 state-snapshot and lock objects and supports the `eusc-de-east-1` AWS European Sovereign Cloud region. OpenTofu 1.12 also discovers credentials issued by `aws login`.

`skip_s3_checksum` now disables both OpenTofu's checksum handling and AWS SDK S3 integrity checks. This helps incomplete S3-compatible implementations but broadens what verification is skipped.

## S3 module source behavior

From 1.11, S3 module addresses use AWS CLI/SDK credential discovery rather than the older custom sequence. An upgrade can select a different credential source and also enables options such as IAM roles for service accounts.

In 1.12, a module source beginning with `s3::http://` uses plaintext HTTP for a non-AWS origin instead of silently upgrading to HTTPS. Official AWS hostnames remain the exception. Treat explicit HTTP origins as unencrypted transport.

## HTTP backend

OpenTofu 1.7 permits user-defined HTTP request headers in backend configuration. OpenTofu 1.9 trace logs include HTTP request and response bodies; keep trace output protected because headers and payloads may be sensitive.

OpenTofu 1.10 adds `tofu force-unlock` support for the HTTP backend.

## AzureRM backend (`1.9.0`, `1.11.0`, `1.12.0`)

The AzureRM backend adds `timeout_seconds` in 1.9, with a default of 300 seconds.

OpenTofu 1.11 ignores deprecated `endpoint`/`ARM_ENDPOINT` and `msi_endpoint`/`ARM_MSI_ENDPOINT`. Use `MSI_ENDPOINT` instead of the latter. Do not configure `environment` together with `metadata_host`. Refresh an existing working directory with `tofu init -reconfigure`, not `-migrate-state`, because authentication changes do not move state.

Authentication controls include:

- `use_cli`, defaulting to `true`
- `use_aks_workload_identity`, defaulting to `false`
- `client_id_file_path`
- `client_secret_file_path`
- inline `client_certificate`

OpenTofu 1.12 adds Azure DevOps and Azure Pipelines workload identity federation. The backend can use both Customer-Provided Keys and Customer-Managed Keys for server-side encryption.

## PostgreSQL backend (`1.10.0`)

The `pg` backend accepts `table_name` and `index_name`, allowing multiple states to occupy separate tables in one database. Finer-grained locking prevents unrelated configurations from contending.

Do not mix OpenTofu 1.10 and older OpenTofu processes against the same database. Their incompatible locks can admit conflicting writes and cause data loss. Coordinate a fleet-wide upgrade or isolate databases and tables.

## Other backend changes

- The GCS backend adds `universe_domain` in 1.11.5 for sovereign GCP services.
- The OSS backend honors standard proxy variables, including `NO_PROXY`, in 1.10.
- Local state no longer writes every in-memory `state.Write()` immediately as of 1.7. A hard crash during apply may leave no in-progress state file, matching other state managers.
- `TF_STATE_PERSIST_INTERVAL` configures the state-write interval from 1.8.

## OCI modules and provider mirrors

OpenTofu 1.10 adds the `oci:` module source scheme and allows OCI registries to act as provider mirrors. Both modules and providers can therefore use registry-based distribution, including in air-gapped environments.

Upgrade to OpenTofu 1.12.6 or 1.11.14 before installing OCI modules or providers (`1.11.14-1.12.6-security`). Earlier builds can resend credentials for the original registry origin to an HTTP redirect target.

Those security releases also reject crafted relative URLs that could otherwise make `tofu init` consume excessive CPU or memory when talking to an attacker-controlled backend or provider/module registry. OpenTofu 1.11.14 is the final planned 1.11 patch; migrate that branch to a newer series.

## Provider installation and lock hashes

During `tofu init`, a lock entry for certain providers on `registry.terraform.io` can select the same version rebuilt on `registry.opentofu.org`. This applies only to providers OpenTofu rebuilds and republishes, not arbitrary third-party providers.

For unsigned provider ZIP sources, the lock file records a locally verified `zh:` archive checksum alongside `h1:`. This improves verification when reinstalling the same archive from another source.

OpenTofu 1.12 records all supported-platform `zh:` and `h1:` hashes when installing directly from OpenTofu Registry. The first initialization after upgrade can therefore add many `h1:` entries to `.terraform.lock.hcl`. Continue using `tofu providers lock` when initialization installs through an alternative source. A `network_mirror` can opt to trust all hashes reported by that mirror.

## Concurrent global provider cache

Multiple 1.10 processes can safely share the global provider cache when the filesystem supports file locking. Use 1.10.5 or later to avoid a `TF_PLUGIN_CACHE_DIR` lock-contention bug, and keep a valid `.terraform.lock.hcl` in every project that shares the cache.

## Registry and module download authentication

OpenTofu 1.11 lets registry retry counts and request timeouts be set in CLI configuration as well as through environment variables.

In 1.12, a module registry can direct OpenTofu to reuse its API credentials for downloading a package served by the registry itself. This avoids a separate `.netrc` credential for the package endpoint.

## Release download tooling (`1.8.0`)

TofuDL is a Go library that locates the latest OpenTofu release, verifies its signature, downloads it, and extracts the binary. It also supplies tooling for mirroring releases into air-gapped environments.

The experimental `libregistry` package provides structured registry metadata and building blocks for independent registry tooling. Treat its API as unstable.

## Container and operating-system boundaries

OpenTofu 1.6 is unsupported as of 1.9 and receives no further security updates. Upgrade to at least 1.7.

The `ghcr.io/opentofu/opentofu` image became deprecated as a base for custom images in 1.9 and is unsupported for that purpose in 1.10. Use a supported base and copy the OpenTofu binary or use purpose-built tooling.

OpenTofu 1.10 requires Linux kernel 3.2+ or macOS 11+. On Windows, junctions are no longer treated as symlinks; if `TEMP` traverses a junction, use a true directory symlink instead.

OpenTofu 1.11 requires macOS 12 Monterey or newer. The 1.12 line is the last planned to support macOS 12. Official 32-bit `386` and `arm` packages continue through 1.13 but are planned for later removal; `amd64` and `arm64` are unaffected.

## Transport and provisioner security

OpenTofu 1.11 rejects SHA-1 signatures during TLS handshakes and incorrectly generated SSH certificates whose signing key is itself a certificate key.

Use 1.11.4 or later where installation can encounter untrusted ZIP archives. Earlier 1.11 releases can spend excessive time processing a malicious archive.

WinRM provisioner connections still work with a warning in 1.12 and are planned to become errors in 1.13. Migrate Windows targets to SSH.

Early 1.12 releases had security defects involving SSH connections, OpenBao-wrapped encryption data, revoked SSH CA keys, and malicious Git URLs capable of reading arbitrary files. The batch minimum was 1.12.4, but the later OCI and relative-URL fixes raise the practical floor to the newest available patch, at least 1.12.6.
