---
name: tailscale-knowledge-patch
description: Tailscale
version: "1.98.1"
license: MIT
metadata:
  author: Nevaberry
---


# Tailscale Knowledge Patch

Use this skill when planning, configuring, upgrading, automating, or debugging
Tailscale clients, services, policy, containers, Terraform resources, or the
Kubernetes Operator.

Confirm the versions of the components in the user's deployment before applying
version-attributed guidance. A client, container image, Operator, Terraform
provider, and integration can have different release versions. Prefer the
project's manifests, configuration, observed behavior, and tests when they
disagree with general guidance.

## Reference index

| Reference | Read when working on |
| --- | --- |
| [CLI, SSH, Taildrive, and observability](references/cli-ssh-taildrive-and-observability.md) | CLI automation, Tailscale SSH, Taildrive, inspection commands, and client metrics |
| [Client platforms and managed policies](references/client-platforms-and-managed-policies.md) | Windows, macOS, iOS, tvOS, Android, Linux desktops, NAS clients, and MDM policy |
| [Containers, CI, Terraform, and log storage](references/containers-ci-terraform-and-logging.md) | Container images, CI authentication, Terraform resources, recorders, and log sinks |
| [Identity, policy, and security](references/identity-policy-and-security.md) | Grants, posture, node keys, Tailnet Lock, identity federation, and management APIs |
| [Kubernetes Operator](references/kubernetes-operator.md) | Ingress, egress, ProxyGroups, API proxying, Recorder, multi-tailnet access, and CRDs |
| [Networking, Services, DNS, and relays](references/networking-services-dns-and-relays.md) | Serve, Funnel, Services, DNS, routing, DERP, Peer Relays, and certificates |
| [Release compatibility](references/release-compatibility.md) | Stable-release boundaries, withdrawn releases, support floors, and platform packaging |

## Start with compatibility hazards

### Paginate tailnet-listing clients

The list-tailnets endpoint returns 100 tailnets by default as of 1.102.2. API
clients must follow each returned `cursor` until it is empty. Use `totalCount`
when the overall count is required. Do not assume one response is complete.

### Replace removed 4via6 names

Deprecated 4via6 MagicDNS name formats are rejected as of 1.102.2. Locate
stored hostnames in application, connector, and egress configuration and move
them to a supported name form before upgrading.

### Recheck Tailscale SSH identities

As of 1.102.2, Tailscale SSH rejects numeric-only usernames and UIDs. Unix-socket
forwarding also honors symlink permissions. Validate account mappings and socket
paths instead of relying on earlier permissive behavior.

### Account for interactive CLI prompts

Significant CLI actions can request `y/n` confirmation as of 1.88.1. Automation
must not assume every previously non-interactive command still completes without
input; inspect the affected command and choose an explicitly supported
non-interactive path.

### Do not duplicate CLI flags

Commands reject repeated occurrences of the same flag as of 1.84.0. Normalize
arguments assembled from wrappers, environment variables, and scripts. Container
image 1.84.2 specifically restored using `TS_EXTRA_ARGS` to set `--accept-dns`
after the stricter parser broke that case.

### Update removed or relocated controls

- Operator 1.96.5 removes `TS_EXPERIMENTAL_KUBE_API_EVENTS`; configure
  Kubernetes API event capability through Tailscale ACLs.
- On macOS, `tailscale drive` is unavailable as of 1.90.1; share Taildrive
  directories through the GUI.
- `ForceEnabled` is deprecated on macOS and iOS; use `AlwaysOn.Enabled` and,
  where appropriate, `AlwaysOn.OverrideWithReason`.
- `TailscaleOnboardingSeen` is deprecated on macOS; use `OnboardingFlow`.
- Store the external GitOps policy URL in the admin console. That value wins
  over the deprecated policy-file code comment.

## Identity and policy quick reference

### Prefer grants for new policy

Grants are the default syntax for new tailnets and policy files that have never
been edited. The `via` field can require traffic to pass through selected exit
nodes, subnet routers, or app connectors. Existing effective permissions do not
change solely because the default authoring syntax changed.

### Treat key protection as an upgrade concern

Node-key sealing is enabled by default on Linux, Windows, and macOS as of 1.90.1;
existing Linux nodes migrate automatically on upgrade. Encrypted state is a
separate control: Linux can use `tailscaled --encrypt-state`, Windows has the
TPM-backed `EncryptState` policy, and macOS stores state in Keychain.

### Choose the current workload-authentication form

For an externally supplied identity token, use:

```console
tailscale up --client-id=<client-id> --id-token=<identity-token>
```

For automatic workload identity tokens, select the audience:

```console
tailscale up --audience=<audience>
```

Provider-native identity is also available in the Operator, container image,
GitHub Actions, and GitLab CI contexts described in the detailed references.

### Parse only stable Tailnet Lock output

Use `tailscale lock log --json` for stable Authority Update Messages and
`tailscale lock status -json` for stable tailnet key-authority data. Keep the
different flag spellings when reproducing these commands.

## Services, routing, and DNS quick reference

### Expect Service advertisement at startup

Services advertise automatically at startup. Disable this only when needed:

```text
TS_EXPERIMENTAL_SERVICE_AUTO_ADVERTISEMENT=false
```

Service virtual IPs are accepted on every client platform regardless of
`--accept-routes`; `tsnet` can host Services, and Operator egress proxies can
send traffic to the VIPs.

### Preserve source addresses with PROXY protocol

Serve and Funnel can prepend a PROXY protocol header so the destination can
receive the original client IP address and port. Enable it only when the
destination expects and validates that header.

### Diagnose Linux routing before changing firewall rules

Linux reports bad IP-forwarding configuration for subnet routers and exit nodes
as a health check. It also sets `src_valid_mark` with `connmark` rules to keep
reverse-path filtering from dropping routed packets.

### Use machine-readable DNS and readiness checks

```console
tailscale dns status --json
tailscale wait
tailscale ip --assert=100.64.0.1
```

`tailscale dns query` also accepts `--json`. `tailscale wait` waits until
resources are available for binding; `tailscale ip --assert` verifies that a
specific address belongs to the node.

## Kubernetes Operator quick reference

### Select the right high-availability resource

- Use a `ProxyGroup` to give Operator-managed Ingresses or Kubernetes Services
  multiple active proxy replicas and to multiplex applications.
- Use a `ProxyGroup` of type `kube-apiserver` for a highly available Kubernetes
  API server proxy.
- A multi-replica `Recorder` requires S3 storage. The default Recorder is a
  single-replica `StatefulSet` backed by the filesystem.
- Use the `Tailnet` custom resource for multi-tailnet access and
  `ProxyGroupPolicy` to control ProxyGroup creation by namespace.

### Separate recordings, audit events, and authorization

The API proxy can record `kubectl exec`, `attach`, and `debug` sessions. Beta
audit logging can capture proxied API events in addition to, or instead of,
full recordings. Configure event capability through ACLs on Operator 1.96.5 and
later.

### Plan dual-stack egress explicitly

Connector and egress-proxy resources support 4via6 from dual-stack clusters,
and egress `ProxyGroup` resources support IPv6. Do not confuse this transport
support with the removed deprecated 4via6 MagicDNS names.

## Client and operations quick reference

### Use recommended exit-node tracking where desired

```console
tailscale set --exit-node=auto:any
```

`auto:any` tracks the recommended exit node as availability and network
conditions change. Managed Windows and macOS deployments can combine
`ExitNodeID=auto:any` with `ExitNode.AllowOverride` to require an exit node while
letting the user select another one.

### Inspect client state with dedicated commands

```console
tailscale get
tailscale whoami
tailscale service list
```

These expose preferences, user/device identity, and visible Services.
`tailscale status --peers=false` also includes the current device name.

### Opt into the release-candidate track deliberately

```console
tailscale version --track=release-candidate
tailscale update --track=release-candidate
```

Use this track only where testing prerelease builds is intentional. On macOS,
the About view also exposes a Release Channel menu that can keep such builds
updated.

### Route platform-specific behavior to the references

Managed policies and client behavior vary substantially by operating system.
Read the client-platform reference before translating a Windows policy to
macOS/iOS, assuming GUI and CLI parity, or applying a mobile routing default.
