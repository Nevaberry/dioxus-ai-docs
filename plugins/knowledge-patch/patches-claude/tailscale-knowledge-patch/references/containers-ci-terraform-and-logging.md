# Containers, CI, Terraform, and Log Storage

Use this reference for container behavior, CI runners and authentication,
Terraform provider resources, tsrecorder secrets, log storage, and operational
metrics.

## Containers

### HTTP-only Serve configuration (since 1.80.0)

The container image can load `TS_SERVE_CONFIG` when HTTPS is disabled for the
tailnet, provided the configuration defines no HTTPS endpoint.

### Duplicate flags and `TS_EXTRA_ARGS` (since 1.84.0)

CLI commands reject duplicate flags. This initially prevented container
`TS_EXTRA_ARGS` from setting `--accept-dns`; container image 1.84.2 restores
that use.

### iptables-only hosts (since 1.92.1)

Container image 1.92.3 restores use of `iptables` on hosts without `nftables`
support.

### OAuth and workload identity (since 1.94.1)

Container image 1.94.1 supports OAuth and workload identity federation
authentication.

## CI integrations

### GitHub Actions runners and cache (since 1.82.0)

The Tailscale GitHub Action is generally available on macOS and Windows
runners. Set `use-cache` to `'true'` to cache Tailscale binaries.

### Provider-native tokens (since 1.94.1)

GitHub Actions and GitLab CI GitOps integrations support provider-native
identity-token authentication.

## Terraform provider

### Provider 0.18 resources (since 1.80.0)

- `tailscale_logstream_configuration` manages streaming to Amazon S3 and
  S3-compatible services.
- `tailscale_tailnet_key` supports import.
- Optional `tailscale_acl.reset_acl_on_destroy` resets the tailnet policy file
  to its default when the resource is destroyed.

### Provider 0.19 log-stream controls (since 1.82.0)

Provider 0.19.0 adds `uploadPeriodMinutes` and `compressionFormat` to
`tailscale_logstream_configuration`.

## Recording and log sinks

### Auth keys from files (since 1.92.1)

`tsrecorder` 1.92.3 reads an authentication key from the file named by
`TS_AUTHKEY_FILE`:

```console
export TS_AUTHKEY_FILE=/run/secrets/tailscale-auth-key
```

### Flow-log node details (since 1.92.1)

Network flow logs automatically record node information about the logging node
and the peers with which it communicates.

### Google Cloud Storage (since 1.94.1)

Network flow logs and configuration audit logs can be streamed to Google Cloud
Storage.

## Metrics

### Client and Peer Relay metrics (since 1.94.1)

Clients expose `tailscaled_home_derp_region_id`. Monitor forwarded Peer Relay
traffic with `tailscaled_peer_relay_forwarded_packets_total` and
`tailscaled_peer_relay_forwarded_bytes_total`.

### Peer Relay endpoint gauge (since 1.96.2)

Peer Relays expose `tailscaled_peer_relay_endpoints` as a user metric.

### Serve traffic for Services (since 1.102.2)

`tailscaled_serve_outbound_bytes_total` and
`tailscaled_serve_inbound_bytes_total` report bytes sent to and received from
peers on Serve connections for Tailscale Services.
