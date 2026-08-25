# Identity, Policy, and Trust

## Device posture and encrypted state

### Country posture (since 1.80.0)

The generally available `ip:country` geolocation attribute can participate in
device posture checks.

### Encrypted client state (since 1.86.0)

The `tsStateEncrypted` posture attribute reports whether client state is
encrypted at rest. Configure encryption with the mechanism supported by each
platform:

- Linux: start `tailscaled` with TPM-backed `--encrypt-state` mode.
- Windows: set the TPM-backed `EncryptState` policy.
- macOS: use `EncryptState` to store state in Keychain. The App Store client
  always uses Keychain, and 1.86.4 applies policy changes without restarting
  the system extension.

```console
tailscaled --encrypt-state
```

## Tailnet policy

### Grants and routed access (since 1.84.0)

Grants and the `via` routing field are generally available. `via` can require
traffic to pass through chosen exit nodes, subnet routers, or app connectors.
New tailnets and policy files that have never been edited use grants syntax
instead of ACL syntax without changing their effective permissions.

### GitOps policy location (since 1.84.0)

Set the external policy-repository URL on the admin console's **Policy file
management** page. The older policy-file code comment is deprecated. If both
locations have a value, the admin-console value takes precedence.

### Visual policy editing (since 1.86.0)

A beta visual policy editor can manage the tailnet policy file. Treat the file
as the policy authority when reconciling visual and GitOps changes.

### Kubernetes API events (since 1.96.2)

The Operator environment variable `TS_EXPERIMENTAL_KUBE_API_EVENTS` has been
removed. Express authorization for the capability in Tailscale ACLs instead.

## Tailnet Lock

### General availability (since 1.84.0)

Tailnet Lock can require the tailnet to verify new node keys supplied by the
coordination server before trusting them.

### Stable log JSON (since 1.92.1)

`tailscale lock log --json` returns Authority Update Messages in a stable
format suitable for parsers.

### Stable status JSON (since 1.94.1)

`tailscale lock status -json` returns tailnet key-authority data in a stable
format suitable for parsers:

```console
tailscale lock status -json
```

## Node-key lifecycle

### Seamless renewal (since 1.90.1)

Clients preserve established connections while reauthenticating during
node-key renewal.

### Sealing by default (since 1.90.1)

Node-key sealing is generally available and enabled by default on Linux,
Windows, and macOS. Existing Linux nodes migrate to sealed node keys
automatically when upgraded.

## Authentication and workload identity

### Auth keys with custom coordination servers (since 1.80.0)

iOS and tvOS clients can use auth keys with custom coordination servers, and
Apple TV can authenticate to a tailnet with an auth key. Custom coordination
servers using HTTP on an explicit custom port are accepted.

### Explicit federation tokens (since 1.92.1)

Authenticate a node with workload identity federation by passing a client ID
and identity token to `tailscale up`:

```console
tailscale up --client-id=<client-id> --id-token=<identity-token>
```

Federated identities can also be managed through the Tailscale API,
`tailscale-client-go-v2`, and the Terraform provider.

### Automatic identity tokens (since 1.94.1)

Workload identities can generate identity tokens automatically. Use
`--audience` to select the audience:

```console
tailscale up --audience=<audience>
```

Provider-native identity-token authentication is supported by the GitHub
Actions and GitLab CI GitOps integrations. Token-exchange errors are surfaced
on the admin console's **Trust credentials** page.

### AuthKey policy scope (since 1.96.2)

The `AuthKey` system policy applies only when a user is not logged in. Do not
use it to overwrite the authentication state of an active signed-in user.
