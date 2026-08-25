# Identity, Policy, and Security

Use this reference for tailnet policy, device posture, key protection,
federated workload identity, Tailnet Lock, and management APIs.

## Tailnet policy and posture

### Country posture (since 1.80.0)

The generally available `ip:country` geolocation attribute can be used in
device posture checks.

### Grants and `via` routing (since 1.84.0)

Grants and the `via` routing field are generally available. `via` can require
traffic to pass through selected exit nodes, subnet routers, or app connectors.
New tailnets and policy files that have never been edited use grants rather
than ACL syntax without changing their effective permissions.

### App connectors (since 1.84.0)

App connectors are generally available for securing tailnet access to SaaS
applications.

### GitOps policy repository URL (since 1.84.0)

Set the external repository URL on the admin console's Policy file management
page. The policy-file code comment is deprecated, and the admin-console value
takes precedence when both are present.

### Visual policy editor (since 1.86.0)

A beta visual policy editor can manage the tailnet policy file.

## Tailnet Lock and node keys

### Tailnet Lock availability (since 1.84.0)

Tailnet Lock is generally available. It can require verification of new node
keys supplied by the coordination server before those keys are trusted.

### Seamless node-key renewal (since 1.90.1)

Clients preserve existing connections while re-authenticating during node-key
renewal.

### Node-key sealing (since 1.90.1)

Node-key sealing is generally available and enabled by default on Linux,
Windows, and macOS. Existing Linux nodes migrate automatically to sealed node
keys during upgrade.

### Stable Tailnet Lock JSON (since 1.92.1 and 1.94.1)

`tailscale lock log --json` returns Authority Update Messages in a stable form.
`tailscale lock status -json` returns tailnet key-authority data in a stable
form. Preserve the different option spellings in scripts.

## Encrypted state

### State controls and posture (since 1.86.0)

The `tsStateEncrypted` posture attribute reports whether client state is
encrypted at rest.

- Linux supports TPM-backed storage with `tailscaled --encrypt-state`.
- Windows provides the TPM-backed `EncryptState` policy.
- macOS uses `EncryptState` to store state in Keychain. The App Store client
  always uses Keychain, and 1.86.4 applies policy changes without restarting
  the system extension.

```console
tailscaled --encrypt-state
```

## Workload identity federation

### Supplied identity tokens (since 1.92.1)

Pass a client ID and identity token to `tailscale up`:

```console
tailscale up --client-id=<client-id> --id-token=<identity-token>
```

Federated identities can be managed through the Tailscale API,
`tailscale-client-go-v2`, and the Terraform provider.

### Automatic identity tokens (since 1.94.1)

Workload identities can generate tokens automatically. Select their audience
with:

```console
tailscale up --audience=<audience>
```

Provider-native identity-token authentication is supported by the GitHub
Actions and GitLab CI GitOps integrations. Token-exchange errors appear on the
admin console's Trust credentials page.

## Authentication scope and coordination servers

### AuthKey system policy scope (since 1.96.2)

The `AuthKey` system policy applies only when a user is not logged in.

### Apple clients and custom control servers (since 1.80.0)

iOS and tvOS clients can use auth keys with custom coordination servers, and
Apple TV can authenticate into a tailnet with an auth key. Custom coordination
servers using HTTP with an explicit custom port are accepted.

## Tailnet management APIs

### Paginated list-tailnets endpoint (since 1.102.2)

The endpoint returns 100 tailnets by default and accepts `limit` and `cursor`
query parameters. Follow each response cursor until it is empty; use
`totalCount` when the full count is needed.

### API-only tailnets (since 1.102.2)

An alpha API can create, list, and delete API-only tailnets within an
organization.

### Admin console location (since 1.102.2)

Use `console.tailscale.com` for the admin console. Authentication remains at
`login.tailscale.com`, and `login.tailscale.com/admin/` redirects to the new
console.
