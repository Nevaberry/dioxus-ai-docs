# Networking, Routing, and Services

## DNS and coordination connectivity

### Tailnet-only DNS-over-TCP (since 1.84.0)

Linux, Windows, and macOS correctly use DNS-over-TCP fallback when the upstream
DNS server is reachable only through the tailnet.

### DNS with an exit node (since 1.90.1)

While using an exit node, clients can still send all domains to DNS resolvers
configured in the admin console's DNS nameserver settings.

### MagicDNS without a manager (since 1.94.1)

On Linux, MagicDNS resolves when `resolv.conf` is used without a DNS manager.

### Removed 4via6 names (since 1.102.2)

Deprecated 4via6 MagicDNS name formats are no longer accepted. Migrate every
reference to a supported name form before upgrading.

## Exit nodes, subnet routes, and app routing

### App connectors and `via` (since 1.84.0)

App connectors are generally available for securing tailnet access to SaaS
applications. The generally available grants `via` field can require traffic
to pass through selected app connectors, exit nodes, or subnet routers.

### Recommended exit-node tracking (since 1.86.0)

On Linux, Windows, and macOS, `auto:any` tracks the recommended exit node and
switches when availability or network conditions change:

```console
tailscale up --exit-node=auto:any
tailscale set --exit-node=auto:any
```

Windows, macOS, iOS, and tvOS expose the same behavior as the **Recommended**
picker option.

### Linux routing health (since 1.98.1)

Linux reports misconfigured IP forwarding for subnet routers and exit nodes
as a health check. It also sets `src_valid_mark` with `connmark` firewall rules
so reverse-path filtering does not drop routed packets.

## Tailscale Services, Serve, and Funnel

### PROXY protocol (since 1.92.1)

Serve and Funnel can send a PROXY protocol header before proxied traffic so
the destination receives the original client's source IP address and port.
Configure the destination to expect the header.

### Remote Service targets (since 1.92.1)

A Tailscale Service may use a remote target as its service destination.

### Generally available Services (since 1.94.1)

Tailscale Services are generally available, and `tsnet` nodes can host them.
Clients on every platform accept Service virtual IPs regardless of
`--accept-routes`. Operator egress proxies can send traffic to those VIPs.

### Automatic advertisement (since 1.96.2)

Services are advertised automatically at startup. Set the following value to
disable automatic advertisement:

```text
TS_EXPERIMENTAL_SERVICE_AUTO_ADVERTISEMENT=false
```

### Proactive certificate renewal (since 1.102.2)

Idle servers renew TLS certificates even without incoming traffic and emit a
warning when no valid certificate is cached.

### Funnel regression repair (since 1.102.2)

Version 1.102.2 restores incoming Funnel connections broken in 1.102.1.

## Peer Relays and DERP

### Self-signed DERP certificates (since 1.82.0)

Clients can pin self-signed IP-address certificates for DERP. This supports
deployments that cannot use Let's Encrypt or another WebPKI certificate.

### Singapore DERP address rotation (since 1.88.1)

Singapore DERP servers use new IPv4 and IPv6 addresses. Only deployments with
custom firewall rules that pin those addresses need changes; refresh the
rules from the DERP map.

### Static Peer Relay endpoints (since 1.92.1)

Assign static endpoints with:

```console
tailscale set --relay-server-static-endpoints=<endpoint-list>
```

### GCP-managed custom DERP certificates (since 1.94.1)

Linux custom DERP servers can use Google Cloud Platform Certificate Manager.

### EC2 endpoint discovery (since 1.96.2)

Peer Relays advertise addresses discovered through the Amazon EC2 Instance
Metadata Service and expose `tailscaled_peer_relay_endpoints` as a user
metric.

## Tailscale SSH and proxy security

### Publickey-first SSH clients (since 1.80.0)

As of 1.80.2, Linux, macOS, and FreeBSD again accept SSH clients that skip the
`none` authentication method and begin with `publickey`, restoring the
behavior from 1.78.x and earlier.

### CONNECT proxy verification (since 1.86.0)

The stable line restores hostname verification when the control-plane
connection uses a CONNECT HTTPS proxy. It also fixes a CSRF issue that could
cause web-interface login failures and improves proxy auto-detection and PAC
handling on Windows 10 version 1607 and earlier.

### Direct-IP SSH (since 1.88.1)

Tailscale SSH works when the destination is specified by IP address and
MagicDNS is disabled.

### Unix account and socket checks (since 1.102.2)

Unix-socket forwarding honors symlink permissions. Tailscale SSH rejects UIDs
and numeric-only usernames, so replace configurations that use numeric SSH
identities.
