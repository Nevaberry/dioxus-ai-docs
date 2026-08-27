# Integrations and Observability

## Terraform provider

### Provider 0.18 capabilities (with Tailscale 1.80.0)

- `tailscale_logstream_configuration` manages log streaming to Amazon S3 and
  S3-compatible services.
- `tailscale_tailnet_key` supports import.
- Optional `tailscale_acl.reset_acl_on_destroy` resets the tailnet policy file
  to its default when the resource is destroyed.

The reset option is destructive to the managed policy; enable it only when
that lifecycle behavior is intended.

### Provider 0.19.0 log controls (with Tailscale 1.82.0)

`tailscale_logstream_configuration` adds `uploadPeriodMinutes` and
`compressionFormat` configuration.

## Tailnet APIs and console

### Paginated tailnet listing (since 1.102.2)

The list-tailnets endpoint returns 100 tailnets by default and accepts `limit`
and `cursor` query parameters. Continue requesting each returned `cursor`
until it is empty. Use `totalCount` when the caller needs the overall count.

### Alpha organization tailnets (since 1.102.2)

An alpha API can create, list, and delete API-only tailnets within an
organization. Keep alpha-dependent clients isolated from stable API
assumptions.

### Admin console address (since 1.102.2)

The admin console is at `console.tailscale.com`. Authentication remains at
`login.tailscale.com`; the former `login.tailscale.com/admin/` path redirects
to the new console.

## Log streaming and audit data

### Flow-log node details (since 1.92.1)

Network flow logs automatically include node information for the logging node
and the peers with which it communicates.

### Google Cloud Storage (since 1.94.1)

Network flow logs and configuration audit logs can be streamed to Google
Cloud Storage.

### Linux Tailscale SSH audit events (since 1.94.1)

Successful Tailscale SSH authentication on Linux emits a `LOGIN` message to
the kernel audit subsystem.

## Client, relay, and Service metrics

### Home DERP region (since 1.94.1)

Clients expose `tailscaled_home_derp_region_id`.

### Peer Relay traffic (since 1.94.1)

Monitor forwarded Peer Relay traffic with:

- `tailscaled_peer_relay_forwarded_packets_total`
- `tailscaled_peer_relay_forwarded_bytes_total`

### Peer Relay endpoints (since 1.96.2)

Peer Relays expose `tailscaled_peer_relay_endpoints` as a user metric. They
also advertise addresses discovered through the Amazon EC2 Instance Metadata
Service.

### Serve traffic for Services (since 1.102.2)

Client metrics report bytes sent to and received from peers over Tailscale
Serve connections for Tailscale Services:

- `tailscaled_serve_outbound_bytes_total`
- `tailscaled_serve_inbound_bytes_total`
