# State, Backends, Locking, and Installation

## S3 credential workflow transition (`1.7.0`)

The S3 backend defaults `use_legacy_workflow` to `false`, following AWS CLI and
SDK credential precedence and preferring backend configuration over environment
variables. Setting it to `true` was only a temporary compatibility measure.

OpenTofu `1.8.0` removes `use_legacy_workflow`; delete the argument before
upgrading because the standard workflow is the only supported behavior.

## Local-state crash persistence (`1.7.0`)

Local state does not immediately persist every in-memory `state.Write()`. A
hard crash during apply may leave no in-progress state file to inspect, matching
other state managers. Do not treat the absence of such a file as proof that no
remote operations occurred.

## HTTP backend headers (`1.7.0`)

The HTTP backend accepts user-defined request headers in backend configuration,
supporting services that require custom authentication or routing headers.

## Initialization-time backend values (`1.8.0`)

Backend configuration can use variables and locals available during early
evaluation. Keep all dependencies resolvable during `tofu init`; sensitive
values are prohibited from 1.9 because initialization would expose them. See
[language-modules-and-lifecycle.md](language-modules-and-lifecycle.md) for the
full early-evaluation contract.

## AzureRM timeout and HTTP tracing (`1.9.0`)

The AzureRM backend accepts `timeout_seconds`, defaulting to 300 seconds. HTTP
backend trace logs include request and response bodies; logs can therefore
contain sensitive backend data and require secret-safe handling.

## OCI module and provider distribution (`1.10.0`)

Modules support the `oci:` source-address scheme, and OCI registries can serve
as provider mirrors. Both module and provider artifacts can therefore use OCI
registry distribution, including for air-gapped environments.

## Native S3 state locking (`1.10.0`)

The S3 backend can lock state directly in S3 rather than relying on DynamoDB.
Use 1.10.2+ when the bucket requires server-side encryption; that patch sends
the `x-amz-server-side-encryption` header for the lockfile.

## PostgreSQL tables and locking (`1.10.0`)

The `pg` backend accepts `table_name` and `index_name`, allowing separate state
tables in one database. Finer-grained locks prevent unrelated configurations
from contending.

Do not mix 1.10-or-newer and older OpenTofu processes in the same database.
Their incompatible locking implementations can allow conflicting writes and
state loss.

## Concurrent global provider cache (`1.10.0`)

Multiple OpenTofu processes can share the global provider cache if the
filesystem supports file locking. Use 1.10.5+ to avoid a lock-contention bug
with `TF_PLUGIN_CACHE_DIR`, and retain a valid `.terraform.lock.hcl` in every
project that uses the cache.

## Backend operations and proxies (`1.10.0`)

The HTTP backend supports `tofu force-unlock`. The OSS backend honors standard
proxy variables, including `NO_PROXY`.

`skip_s3_checksum` also disables the AWS SDK's S3 integrity checks. This can
help incomplete S3-compatible services but broadens the verification bypass;
enable it only for a known compatibility requirement.

## Provider installation compatibility (`1.10.0`)

During `tofu init`, a lock entry for certain providers on
`registry.terraform.io` can select the same version rebuilt and republished on
`registry.opentofu.org`. This mapping applies only to providers that OpenTofu
rebuilds and republishes, not arbitrary third-party providers.

For unsigned provider ZIP sources, the lock file records a locally verified
`zh:` archive checksum alongside `h1:`. This improves verification when the
same artifact is later installed from a different source.

## AzureRM migration and authentication (`1.11.0`)

The AzureRM backend ignores deprecated `endpoint`/`ARM_ENDPOINT` and
`msi_endpoint`/`ARM_MSI_ENDPOINT`. Use `MSI_ENDPOINT` instead of the latter and
do not set `environment` with `metadata_host`. Refresh the working directory
with `tofu init -reconfigure`, not `-migrate-state`, because state is not being
moved.

Authentication controls include:

- `use_cli`, defaulting to `true`.
- `use_aks_workload_identity`, defaulting to `false`.
- `client_id_file_path` and `client_secret_file_path`.
- Inline `client_certificate`.

## S3 module credentials and backend additions (`1.11.0`)

S3 module source addresses use AWS CLI/SDK credential discovery instead of the
old custom sequence. An upgrade can select a different credential source and
adds schemes such as IAM roles for service accounts.

The S3 backend can tag state snapshot and lock objects and can use buckets in
the `eusc-de-east-1` AWS European Sovereign Cloud region. From 1.11.5, the GCS
backend has `universe_domain` for sovereign GCP services.

## Cross-platform provider lock hashes (`1.12.0`)

When `tofu init` installs directly from OpenTofu Registry, it records the full
set of `zh:` and `h1:` hashes for all supported platforms. The first
initialization after upgrading can add many `h1:` entries to
`.terraform.lock.hcl`.

When initialization uses another source, continue to run
`tofu providers lock`. A `network_mirror` can opt to trust all hashes reported
by that mirror.

## Private module download credentials (`1.12.0`)

A module registry can instruct OpenTofu to reuse its API credentials for
package downloads. When the registry serves the package itself, this removes
the need for a separate `.netrc` credential.

## Backend authentication and encryption (`1.12.0`)

The S3 backend discovers credentials issued by `aws login`. The AzureRM backend
adds Azure DevOps and Azure Pipelines workload identity federation and supports
Customer-Provided Keys and Customer-Managed Keys for server-side encryption.

## S3 module HTTP scheme (`1.12.0`)

For a non-AWS origin, a module source beginning with `s3::http://` uses
plaintext HTTP rather than silently switching to HTTPS. Official AWS hostnames
remain the exception. Treat an explicit non-AWS HTTP address as unencrypted
transport and avoid sending credentials or sensitive modules over it.
