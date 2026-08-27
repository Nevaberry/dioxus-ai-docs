# Plugins, Agents, and Delivery

## Plugin artifacts and registration

### External and extracted artifacts

Enterprise can execute plugins externally, but the operator must place the
extracted artifact in the plugin directory before registration; Vault does not
extract it on demand. Community Edition registration also supports an extracted
artifact directory. (`1.19-changelog`)

### Official downloads

Vault can automatically download official auth and secrets plugins from
`releases.hashicorp.com` as a beta feature. Enterprise exposes this during CLI
registration with `-download`. (`1.20-changelog`)

### Registration APIs and pinned versions

The API client has detailed registration methods that return a registration
response together with an error. `RegisterPlugin` and
`RegisterPluginWithContext` are deprecated. (`1.20-changelog`)

Enterprise can override pinned versions while creating or updating database
engines and while enabling or tuning auth and secrets backends. The UI can
recognize and update first-party external plugins and mount a registered
external plugin at a selected version. Plugin list responses include a SHA-256
sum. (`2.0-changelog`)

### Signing-key compatibility

Enterprise 1.19.17, 1.20.11, 1.21.6, and 2.0.1 cannot register Enterprise
plugins released on or after April 21, 2026 because the renewed signing key
cannot be verified. Existing registrations are unaffected. Use 1.19.18,
1.20.12, 1.21.7, or 2.0.2 or later in the corresponding line.
(`upgrade-safety`)

## Vault Agent and Proxy

`enable_reauth_on_new_credentials` makes supported auto-auth methods
reauthenticate when credentials change. Certificate auto-auth watches its
certificate and key files when this setting is enabled. (`1.19-changelog`)

Vault Agent can perform Enterprise External CA ACME workflows, and Agent
templates re-render after external-CA certificate issuance or renewal.
(`2.0-changelog`)

Vault Agent's built-in API proxy is deprecated and pending removal. Deployments
that require proxy behavior should move to Vault Proxy. (`upgrade-safety`)

## Container delivery

### Runtime identity and memory locking

Containers run as the `vault` user by default from 1.19.16. The 1.19.17 image
required runtime `IPC_LOCK`, but 1.19.18 removed `cap_ipc_lock` from the image.
Containers cannot call `mlock()`, so set `disable_mlock = true` and disable swap
at the runtime or host. (`1.19-changelog`)

### OCI and UBI packaging

Container images are exported as compressed OCI image layouts, and UBI images
use UBI 10 minimal. (`1.19-changelog`)

UBI images no longer contain `gnupg`, `openssl`, or `procps`. Provide tools
needed by entrypoint scripts, health checks, and debugging separately.
(`2.0.4`)

The 1.19.16 Docker image has an unresolved startup failure involving `setfcap`;
affected deployments need the published workaround. (`1.19`)

## SDK test clusters

SDK Docker helpers use `github.com/moby/moby` instead of
`github.com/docker/docker`. `DockerClusterNode.UpdateConfig` takes full cluster
options and supports seals, KMS libraries, and entropy augmentation.
(`1.20-changelog`)

## Terraform delivery

The Enterprise Vault provider supports ephemeral resources and write-only
attributes for KV and database secrets engines. (`1.20`)

The Terraform Cloud secrets engine can generate dynamic team tokens.
(`1.20`)

## Kubernetes secret delivery

Vault Secrets Operator can project protected secrets directly into application
pods as CSI-backed shared volumes, avoiding native Kubernetes Secret objects.
(`1.21`)
