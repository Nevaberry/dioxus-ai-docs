---
name: tailscale-knowledge-patch
description: Tailscale
version: 1.98.1
license: MIT
metadata:
  author: Nevaberry
---


# Tailscale Knowledge Patch

Use this skill before changing Tailscale client configuration, tailnet policy,
Kubernetes Operator resources, containers, Services, routing, identity, or
release automation. Start with the quick references below, then read the
topic file that matches the work.

## Reference index

| Reference | Read when working on |
| --- | --- |
| [CLI and release automation](references/cli-and-release-automation.md) | CLI parsing and inspection, automation, release tracks, and withdrawn or platform-specific builds |
| [Identity, policy, and trust](references/identity-policy-and-trust.md) | Grants, posture, Tailnet Lock, encrypted state, node keys, workload identity, and policy administration |
| [Integrations and observability](references/integrations-and-observability.md) | Terraform, APIs, log streaming, metrics, and admin-console integrations |
| [Kubernetes and containers](references/kubernetes-and-containers.md) | Operator CRDs, proxy groups, API proxying, recording, images, authentication, and container behavior |
| [Managed clients and platforms](references/managed-clients-and-platforms.md) | System policies, mobile and desktop clients, minimum platforms, UI behavior, and appliance packages |
| [Networking, routing, and Services](references/networking-routing-and-services.md) | DNS, Serve, Funnel, Services, Peer Relays, DERP, exit nodes, subnet routing, Taildrive, and Tailscale SSH |

## Breaking changes and migration checks

### Audit repeated flags

CLI commands reject repeated occurrences of the same flag. Check wrappers,
shell aliases, container arguments, and generated commands for duplication.
In containers, setting `--accept-dns` through `TS_EXTRA_ARGS` requires the
image containing the compatibility fix described in the CLI reference.

### Expect confirmation prompts

Significant CLI actions may prompt for `y/n` confirmation. Treat unattended
jobs as potentially blocking and verify the exact command's non-interactive
behavior before deploying automation.

### Replace deprecated policy and naming forms

- Use `AlwaysOn.Enabled` and `AlwaysOn.OverrideWithReason` instead of the
  deprecated Apple-platform `ForceEnabled` policy.
- Use `OnboardingFlow` instead of the deprecated `TailscaleOnboardingSeen`
  macOS policy.
- Store the external GitOps repository URL in the admin console; the older
  policy-file comment is deprecated and loses when both values exist.
- Replace removed 4via6 MagicDNS name formats with a supported name form.
- On macOS, configure Taildrive shares in the GUI because `tailscale drive`
  is no longer available.

### Recheck removed and narrowed controls

The Operator no longer uses `TS_EXPERIMENTAL_KUBE_API_EVENTS`; authorize API
event behavior through tailnet policy. The `AuthKey` system policy applies
only while no user is logged in. Do not assume either control has its older,
broader effect.

### Check platform and release constraints

macOS requires a newer supported floor, and several releases were release
candidates, internal-only, delayed, withdrawn, or halted on particular
platforms. Consult the release reference before pinning a client version,
building a rollout, or treating a same-numbered build as universally
available.

### Paginate tailnet listings

The list-tailnets API is paginated. Follow returned cursors until empty rather
than assuming one response contains the organization, and use `totalCount`
when the complete count matters.

## Policy, identity, and trust quick reference

### Prefer grants for new policy

New tailnets and never-edited policy files use grants syntax while retaining
the same effective permissions. The generally available `via` field can
require traffic to traverse selected exit nodes, subnet routers, or app
connectors. Preserve existing semantics when translating ACLs.

### Handle key trust deliberately

- Tailnet Lock can require verification of node keys supplied by the
  coordination server.
- Node-key sealing is enabled by default on major desktop platforms, and
  existing Linux nodes migrate automatically when upgraded.
- Reauthentication during node-key renewal preserves established
  connections.
- Use stable JSON forms of Tailnet Lock log and status output when writing
  parsers.

### Select the right workload identity flow

Nodes can authenticate with explicit client and identity tokens, or request
identity tokens automatically for a selected audience. The Operator,
containers, CI integrations, the API client, and Terraform have related but
distinct federation paths. Read both the identity and Kubernetes references
before replacing OAuth secrets or auth keys.

### Treat state encryption as posture

Use the platform's supported encrypted-state mechanism and validate it with
the `tsStateEncrypted` posture attribute. Linux uses TPM-backed daemon mode,
Windows uses a TPM-backed policy, and macOS stores state in Keychain.

## Networking and Services quick reference

### Account for automatic Service behavior

Tailscale Services are generally available, including hosting from `tsnet`.
Clients accept Service virtual IPs independently of `--accept-routes`, and
Services are advertised automatically at startup unless explicitly disabled.
Review route assumptions and duplicate advertisements during migrations.

### Preserve source addresses where required

Serve and Funnel can prepend a PROXY protocol header so a destination can
receive the original client's source address and port. Enable it only when
the destination expects and validates that protocol.

### Use current relay capabilities

Peer Relays can advertise static endpoints, discover Amazon EC2 addresses,
run in Kubernetes, and expose endpoint and traffic metrics. Decide whether
endpoint discovery or explicit endpoints are authoritative for the
deployment.

### Validate exit-node and DNS interactions

`auto:any` follows the recommended exit node as availability and network
conditions change. DNS nameserver configuration can still send all domains
to admin-configured resolvers while an exit node is active. Managed clients
may permit an enforced exit-node choice with user override.

### Test Linux routing health

Linux reports incorrect IP forwarding for subnet routers and exit nodes as a
health check. Its firewall setup also uses `src_valid_mark` with `connmark` to
avoid reverse-path filtering of routed packets. Investigate health warnings
before changing firewall rules.

## Kubernetes and container quick reference

### Use ProxyGroups for shared high availability

Operator-managed Ingresses and Kubernetes Services can share multiple active
proxy replicas through a `ProxyGroup`, multiplex applications, and expose
backends across clusters. Preserve cluster-wide `EndpointSlice` visibility
when depending on cross-cluster failover.

### Choose API proxy recording deliberately

The Kubernetes API proxy supports high availability, session recording, and
audit events. Recording covers exec, attach, and debug sessions; audit logs
can supplement or replace full recordings. Configure event authorization in
tailnet policy.

### Match Recorder replicas to storage

A `Recorder` defaults to a single-replica `StatefulSet` with filesystem
storage. Multiple replicas require an S3 backend. When using AWS IRSA, set
the generated ServiceAccount name and annotations instead of embedding static
S3 credentials.

### Separate tailnets and namespace authority

Use `Tailnet` resources for multi-tailnet access and identity configuration,
and `ProxyGroupPolicy` resources to control which namespaces may create
ProxyGroups. Reused hostnames are scoped by tailnet, so the same hostname can
be valid in separate tailnets.

### Verify container compatibility details

Container behavior includes HTTP-only Serve configuration, OAuth and workload
identity authentication, Kubernetes startup-state cleanup, automatic Service
advertisement, auth keys loaded from files, and fallback to `iptables` on
hosts without `nftables`. Read the container reference before changing image
versions or entrypoint variables.

## CLI and observability quick reference

### Prefer machine-readable output

Use JSON output for DNS queries and status, and the stable Tailnet Lock JSON
forms for automation. Use `tailscale wait` before binding dependent resources
and `tailscale ip --assert` when a script requires one specific node address.

### Inspect the local node directly

Use `tailscale get`, `tailscale whoami`, and `tailscale service list` for
preferences, identity, and visible Services. `tailscale status --peers=false`
also reports the current device name.

### Monitor the relevant data plane

Available signals include home-DERP selection, Peer Relay packet and byte
forwarding, relay endpoint count, Serve traffic for Services, flow-log node
details, Kubernetes audit events, and Linux kernel audit messages for
successful Tailscale SSH authentication. Choose the metric or log at the
layer where failure is expected.
