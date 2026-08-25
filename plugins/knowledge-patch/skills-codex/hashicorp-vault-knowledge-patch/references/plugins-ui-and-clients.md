# Plugins, UI, Clients, and Integrations

Use this reference for plugin packaging and registration, SDK/API compatibility,
listener client limits, and GUI navigation.

## Plugin packaging and registration

### External and extracted plugins (`1.19-changelog`)

Enterprise can execute plugins externally, but operators must place the
extracted artifact in the plugin directory before registration; Vault does not
extract it. Community registration also supports an extracted-artifact
directory.

### Official plugin downloads (`1.20-changelog`)

Vault can download official auth and secrets plugins from
`releases.hashicorp.com` as a beta feature. Enterprise CLI registration exposes
this through `-download`.

### Detailed plugin-registration API (`1.20-changelog`)

Use detailed API-client registration variants to receive the registration
response alongside an error. `RegisterPlugin` and `RegisterPluginWithContext`
are deprecated.

### Pinned plugin version overrides (`2.0-changelog`)

Enterprise can override pinned versions while creating/updating database
engines and enabling/tuning auth or secrets backends. The UI recognizes and
updates first-party external plugins and mounts a registered external plugin at
a selected version. Plugin list responses include a SHA-256 sum.

## Client, SDK, and listener compatibility

### SDK Docker test-cluster changes (`1.20-changelog`)

SDK Docker helpers use `github.com/moby/moby` instead of
`github.com/docker/docker`. `DockerClusterNode.UpdateConfig` takes full cluster
options and supports seals, KMS libraries, and entropy augmentation.

### Token-header size limit (`2.0-changelog`)

Listeners cap `X-Vault-Token` and `Authorization: Bearer` at 8 KB by default.
Disable the limit only deliberately:

```hcl
max_token_header_size = -1
```

### Vault Agent API proxy retirement (`upgrade-safety`)

Vault Agent's built-in API proxy is deprecated and pending removal. Migrate
proxy use to Vault Proxy.

## Login and namespace UI

### GUI workload identity federation (`1.19`)

The Enterprise GUI configures workload identity federation for AWS, Azure, and
GCP integrations.

### Web UI login-method configuration (`1.20-changelog`)

Enterprise can configure default and backup login methods. `/vault/auth?with=`
refers only to an auth mount path and shows a simplified form; selecting another
method no longer rewrites it.

### Namespace picker navigation (`1.20`)

The Enterprise GUI namespace picker searches, filters, and navigates without
reauthentication.

### Secrets-engine UI routes (`2.0-changelog`)

Secrets-engine URLs move from `/secrets` to `/secrets-engines`; the list no
longer supports bulk deletion. The UI adds TLS-certificate login.

### Namespace onboarding workflow (`2.0`)

The Enterprise GUI creates a namespace through a guided questionnaire, after
which setup can continue in GUI, CLI, or Terraform.

### Secrets-engine GUI pagination (`upgrade-safety`)

In 1.21 and 2.0, changing **Items per page** away from page 1 can show an empty
or incomplete Secrets Engines table even though mounts exist. Return to page 1
before changing size, or refresh and retry there.
