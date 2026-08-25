# Service Discovery

## Kubernetes and Consul migration (`3.0.0`)

Kubernetes discovery no longer supports `discovery.k8s.io/v1beta1`
EndpointSlices or `networking.k8s.io/v1beta1` Ingresses. Clusters exposing only
those beta APIs cannot serve the corresponding roles. Endpoint discovery now
recognizes sidecar containers.

Consul catalog discovery supports server-side catalog filters, reducing the
result set before target processing.

## OpenStack load balancers (`3.2.0`)

OpenStack discovery includes Octavia load balancers.

## Scaleway address metadata (`3.3.0`)

Scaleway exposes `__meta_scaleway_instance_public_ipv4_addresses` and
`__meta_scaleway_instance_public_ipv6_addresses`. It no longer sets the older
`__meta_meta_scaleway_instance_public_ipv4` when the public address is IPv6.

## STACKIT and Hetzner filtering (`3.5.0`)

STACKIT Cloud has a native discovery provider. Hetzner discovery accepts
`label_selector` to filter servers before relabeling:

```yaml
hetzner_sd_configs:
  - role: hcloud
    label_selector: environment=production
```

## Kubernetes namespace metadata (`3.6.0`)

Attach namespace metadata to Kubernetes targets:

```yaml
kubernetes_sd_configs:
  - role: pod
    attach_metadata:
      namespace: true
```

## Unified AWS discovery (`3.8.0`)

The unified AWS discovery option covers EC2, Lightsail, and ECS services.

## Refresh attribution (`3.9.0`)

Most `prometheus_sd_refresh` metrics have a `config` label containing the job
name, making refresh behavior attributable to a discovery configuration.

## MSK and provider build tags (`3.10.0`)

AWS discovery adds an MSK role. Custom builds can remove all bundled providers
with the `remove_all_sd` Go build tag and selectively restore providers with
`enable_<sd name>_sd` tags.

## Provider additions and metadata migrations (`3.11.0`)

Consul Health API filtering uses `health_filter` from 3.11.2; the general
`filter` is no longer incorrectly sent to the Health API.

For Hetzner `robot`, migrate `__meta_hetzner_datacenter` to
`__meta_hetzner_robot_datacenter`; the old label remains compatible there.
For `hcloud`, migrate location labels from
`__meta_hetzner_hcloud_datacenter_location` and
`__meta_hetzner_hcloud_datacenter_location_network_zone` to
`__meta_hetzner_hcloud_location` and
`__meta_hetzner_hcloud_location_network_zone`. The old hcloud datacenter form
was scheduled to stop working after July 1, 2026.

AWS discovery adds ElastiCache and RDS roles, and EC2 once again honors its
configured `endpoint`. Azure discovery supports Workload Identity and accepts
an empty `client_id` for system-assigned managed identity.

Kubernetes pod discovery accepts node-role selectors. Pod targets expose
`__meta_kubernetes_pod_deployment_name`,
`__meta_kubernetes_pod_cronjob_name`, and
`__meta_kubernetes_pod_job_name`. DualStack EndpointSlice policies no longer
create duplicate targets.

Monitor the consumer-delivery time with
`prometheus_sd_last_update_timestamp_seconds`.

## New providers, external IDs, and IPv6 (`3.12.0`)

Prometheus discovers DigitalOcean Managed Databases and Outscale Cloud VMs;
the latter uses `outscale_sd_configs`.

ECS, MSK, RDS, and ElastiCache configurations accept `external_id`. EC2 can use
IPv6 target addresses; when both families exist, private IPv4 remains default.

Removing a scrape job removes its per-job `prometheus_sd_refresh*` and
`prometheus_sd_discovered_targets` series.

## RDS filtering (`3.13.0`)

RDS discovery supports server-side instance filters.

## Provider removals and reliability (`3.13.2-3.14.0`)

Hetzner `hcloud` targets no longer expose `__meta_hetzner_datacenter` because
the Cloud API removed it. Relabel rules must use the replacement location
labels. Oracle Cloud Infrastructure compute targets are available through
`oci_sd_configs`.

Offline `promtool check config` no longer contacts AWS IMDS when `region` is
omitted for EC2, ECS, RDS, MSK, ElastiCache, or Lightsail.

Docker and Docker Swarm discovery time out unresponsive `unix`, `npipe`, and
`tcp` hosts instead of freezing on stale targets. Docker Swarm avoids panics on
plugin and network-attachment services, and IPv6-only containers are discovered.
