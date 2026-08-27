# Service Discovery

Use this reference for discovery API compatibility, cloud-provider roles,
target metadata, filtering, diagnostics, and discovery self-metrics.

## Kubernetes discovery

### Remove beta discovery API dependencies (3.0.0)

Kubernetes discovery no longer supports `discovery.k8s.io/v1beta1`
EndpointSlices or `networking.k8s.io/v1beta1` Ingresses. Clusters exposing only
those beta APIs are incompatible with the corresponding roles.

### Discover sidecar containers (3.0.0)

Endpoint discovery recognizes sidecar containers when constructing targets.

### Attach namespace metadata (3.6.0)

Enable namespace metadata on a discovery configuration:

```yaml
kubernetes_sd_configs:
  - role: pod
    attach_metadata:
      namespace: true
```

### Select pod nodes by role (3.11.0)

Kubernetes configurations using the pod role can include node-role selectors.

### Use controller-name metadata (3.11.0)

Pod targets expose `__meta_kubernetes_pod_deployment_name`,
`__meta_kubernetes_pod_cronjob_name`, and
`__meta_kubernetes_pod_job_name` for their controlling deployment, cronjob, or
job.

### De-duplicate DualStack targets (3.11.0)

Kubernetes discovery no longer emits duplicate targets for `*DualStack`
EndpointSlice policies.

## Consul, Hetzner, and Scaleway

### Filter Consul catalog results server-side (3.0.0)

Consul catalog discovery supports server-side filters, reducing the result set
before target processing.

### Expose Scaleway public addresses accurately (3.3.0)

Scaleway targets expose `__meta_scaleway_instance_public_ipv4_addresses` and
`__meta_scaleway_instance_public_ipv6_addresses`. The old
`__meta_meta_scaleway_instance_public_ipv4` is no longer set when the public
address is IPv6.

### Filter Hetzner servers (3.5.0)

Use `label_selector` to filter servers during discovery:

```yaml
hetzner_sd_configs:
  - role: hcloud
    label_selector: environment=production
```

### Filter the Consul Health API correctly (3.11.0)

From 3.11.2, use `health_filter` for Health API filtering. The general `filter`
parameter is no longer incorrectly applied to that API.

### Migrate Hetzner labels (3.11.0)

For the `robot` role, replace `__meta_hetzner_datacenter` with
`__meta_hetzner_robot_datacenter`; the old label remains for compatibility.
For `hcloud`, migrate
`__meta_hetzner_hcloud_datacenter_location` and
`__meta_hetzner_hcloud_datacenter_location_network_zone` to
`__meta_hetzner_hcloud_location` and
`__meta_hetzner_hcloud_location_network_zone`. The `hcloud` form of
`__meta_hetzner_datacenter` was scheduled to stop working after July 1, 2026.

### Stop relying on the removed Hetzner label (3.13.2-3.14.0)

Hetzner `hcloud` targets no longer expose `__meta_hetzner_datacenter`, following
its removal from the Hetzner Cloud API. Rewrite relabeling that used it.

## AWS discovery

### Use unified AWS discovery (3.8.0)

The unified AWS discovery option covers EC2, Lightsail, and ECS services.

### Discover MSK (3.10.0)

The AWS discovery roles include Amazon Managed Streaming for Apache Kafka.

### Discover ElastiCache and RDS (3.11.0)

AWS roles include ElastiCache and RDS. EC2 discovery again honors its configured
`endpoint`.

### Supply role-assumption external IDs (3.12.0)

ECS, MSK, RDS, and ElastiCache configurations accept optional `external_id`.

### Prefer IPv4 but support IPv6 targets (3.12.0)

EC2 discovery can use IPv6 target addresses. When both address families exist,
private IPv4 remains the default.

### Filter RDS instances (3.13.0)

RDS discovery supports instance filters, reducing results before target
processing.

### Validate AWS configuration offline (3.13.2-3.14.0)

`promtool check config` no longer contacts AWS IMDS when `region` is omitted
from EC2, ECS, RDS, MSK, ElastiCache, or Lightsail discovery configuration.

## Azure and additional cloud providers

### Discover OpenStack Octavia (3.2.0)

OpenStack discovery includes Octavia load balancers.

### Discover STACKIT Cloud targets (3.5.0)

STACKIT Cloud service discovery removes the need to maintain those targets as
static configuration.

### Use Azure identities (3.11.0)

Azure discovery supports Azure Workload Identity. An empty `client_id` selects
system-assigned managed identity.

### Discover DigitalOcean managed databases (3.12.0)

DigitalOcean Managed Databases are available as discovery targets.

### Discover Outscale VMs (3.12.0)

Use `outscale_sd_configs` to discover Outscale Cloud VM targets.

### Discover OCI compute (3.13.2-3.14.0)

Use `oci_sd_configs` for Oracle Cloud Infrastructure compute targets.

## Diagnostics, metrics, and custom builds

### Trace relabeling in the target UI (3.8.0)

The target UI can display each relabeling step for a discovered target, showing
how labels changed or why the target was dropped.

### Attribute refresh metrics to jobs (3.9.0)

Most `prometheus_sd_refresh` metrics include a `config` label containing the job
name.

### Remove bundled providers from custom builds (3.10.0)

Custom builds can use the `remove_all_sd` Go build tag, then selectively restore
providers with `enable_<sd name>_sd` tags.

### Track the last consumer update (3.11.0)

`prometheus_sd_last_update_timestamp_seconds` reports when the latest discovery
update was sent to consumers.

### Clean up metrics when jobs disappear (3.12.0)

Removing a scrape job deletes its per-job `prometheus_sd_refresh*` and
`prometheus_sd_discovered_targets` series.

### Make Docker discovery fail promptly and safely (3.13.2-3.14.0)

Docker and Docker Swarm discovery time out unresponsive `unix`, `npipe`, and
`tcp` hosts rather than freezing on stale targets. Swarm no longer panics on
plugin or network-attachment services, and IPv6-only containers are discovered.
