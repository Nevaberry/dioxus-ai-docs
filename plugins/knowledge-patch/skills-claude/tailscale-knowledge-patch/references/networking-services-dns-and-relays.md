# Networking, Services, DNS, and Relays

Use this reference for Serve, Funnel, Tailscale Services, DNS, exit-node and
subnet routing, DERP, Peer Relays, and TLS certificates.

## Serve, Funnel, and Services

### PROXY protocol (since 1.92.1)

Serve and Funnel can send a PROXY protocol header before proxied traffic so the
destination receives the original client's source IP address and port. The
destination must be configured to expect the header.

### Remote Service destinations (since 1.92.1)

A Tailscale Service can use a remote target as its service destination.

### Services and `tsnet` hosting (since 1.94.1)

Tailscale Services are generally available, and `tsnet` nodes can host them.
Clients on every platform automatically accept Service virtual IPs regardless
of `--accept-routes`. Operator egress proxies can send traffic to those VIPs.

### Automatic Service advertisement (since 1.96.2)

Services advertise automatically at startup. Disable the behavior with:

```text
TS_EXPERIMENTAL_SERVICE_AUTO_ADVERTISEMENT=false
```

### Funnel correction (since 1.102.2)

Version 1.102.2 restores incoming Funnel connections that failed under 1.102.1.

## DNS

### DNS-over-TCP through the tailnet (since 1.84.0)

Linux, Windows, and macOS can correctly fall back to DNS over TCP when the
upstream DNS server is reachable only through the tailnet.

### Admin-configured resolvers with an exit node (since 1.90.1)

Clients using an exit node can still send all domains to DNS resolvers
configured in the admin console's DNS nameserver settings.

### MagicDNS with plain `resolv.conf` (since 1.94.1)

On Linux, MagicDNS resolves when `resolv.conf` is used without a DNS manager.

### Machine-readable DNS output (since 1.96.2)

Both `tailscale dns query` and `tailscale dns status` accept `--json`:

```console
tailscale dns status --json
```

### Removed 4via6 names (since 1.102.2)

Deprecated 4via6 MagicDNS name formats are no longer accepted. Update stored
references to a supported name form.

## Exit-node and subnet routing

### Recommended exit-node tracking (since 1.86.0)

On Linux, Windows, and macOS, `auto:any` tracks the recommended exit node and
switches as node availability or network conditions change. Windows, macOS,
iOS, and tvOS offer the same behavior through the Recommended picker.

```console
tailscale up --exit-node=auto:any
tailscale set --exit-node=auto:any
```

### Linux routing health (since 1.98.1)

Linux reports misconfigured IP forwarding for subnet routers and exit nodes as
a health check. It sets `src_valid_mark` with `connmark` firewall rules so
reverse-path filtering does not drop routed packets.

## DERP certificates and endpoints

### Pin self-signed DERP certificates (since 1.82.0)

Clients can pin self-signed IP-address certificates for DERP deployments that
cannot use Let's Encrypt or another WebPKI certificate.

### Singapore DERP address rotation (since 1.88.1)

Singapore DERP servers use new IPv4 and IPv6 addresses. Update custom firewall
rules that pin the old addresses from the DERP map; deployments without such
rules need no action.

### GCP-managed certificates (since 1.94.1)

Custom DERP servers on Linux can use Google Cloud Platform Certificate Manager.

## Peer Relays

### Static endpoints (since 1.92.1)

Assign static Peer Relay endpoints with
`tailscale set --relay-server-static-endpoints`.

### EC2 endpoint discovery (since 1.96.2)

Peer Relays advertise addresses discovered through the Amazon EC2 Instance
Metadata Service.

## TLS certificate renewal

### Renew certificates on idle servers (since 1.102.2)

Idle servers proactively renew TLS certificates without incoming traffic and
emit warnings when no valid certificate is cached.
