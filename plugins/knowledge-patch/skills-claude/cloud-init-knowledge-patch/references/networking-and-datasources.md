# Networking and Datasources

Use this reference when generating network configuration, selecting a
datasource, or consuming cloud metadata.

## Network renderers

### Network v1 device support

Network v1 renders bonds, bridges, and VLANs. `network-config` also expresses
`allow_accept_ra` for those device types (26.1). Preserve the setting during
translation or generation; do not treat it as exclusive to another schema or
device class.

Validation should cover each device type independently. Renderer support does
not identify a datasource or cloud platform.

### NetworkManager route metrics

The NetworkManager renderer carries route-metric settings into generated
connection profiles (26.2). Configurations that use metrics to choose between
competing routes can state that preference directly without a renderer-specific
workaround.

When migrating an old workaround:

1. Keep the route metric in the source network configuration.
2. Remove only the duplicate profile mutation.
3. Render the connection profile and confirm the intended metric is present.
4. Test route selection when multiple candidate routes are active.

## OpenStack

### Preserve metadata-supplied bond names

OpenStack bond names come directly from `network_data.json` (26.1). Treat the
supplied name as stable input to later rendering steps.

Audit downstream logic that:

- predicts a bond name before metadata is read;
- replaces supplied names with `bond0`, `bond1`, and similar sequences;
- maps other device configuration to an assumed `bondN` identifier; or
- hard-codes sequential bond names in test fixtures.

Do not synthesize a new name when metadata already provides one.

### Strict identity without DMI

Since 25.1.4, Ec2, OpenStack, and AltCloud systems without DMI do not fall back
to a post-network link-local metadata probe (guidance recorded in 26.1).
Cloud-init remains disabled unless the datasource is identified by:

- DMI data;
- a kernel `ds=` override; or
- `datasource_list` configuration.

For OpenStack, a config drive can provide the required identification. An image
that is deliberately OpenStack-specific can force selection with:

```yaml
datasource_list: [ OpenStack ]
```

Place that configuration in
`/etc/cloud/cloud.cfg.d/91_openstack.cfg`. Do not force OpenStack on a portable
image that can legitimately boot on another platform.

Triage a disabled non-x86 OpenStack instance in this order:

1. Inspect whether usable DMI identity exists.
2. Inspect the kernel command line for a `ds=` override.
3. Inspect merged configuration for an OpenStack `datasource_list` entry.
4. Determine whether an OpenStack config drive is available.

Successful network setup or a later response from link-local metadata is not
proof that cloud-init should have selected the datasource; that fallback path
is no longer performed.

## Azure

### Network rename and ready-report controls

Azure provides `apply_network_config_set_name` (26.2). Disable it when
network-config `set-name` directives must not be applied. Keep this decision
separate from whether network configuration itself is accepted.

The experimental `skip_ready_report` option suppresses the Azure ready report.
Treat it as experimental in image policy and test the control plane behavior
that expects or omits the report.

### Missing custom data

Missing custom data is reported as a provisioning failure (26.2), rather than
silently continuing. Provisioning automation should surface and handle the
failure instead of treating the instance as successfully initialized.

## OpenNebula

OpenNebula accepts a global `SEARCH_DOMAIN` for all interfaces (26.2). It also
accepts `ETHx_ROUTES` values for per-interface static routes.

Keep these scopes distinct:

- Apply `SEARCH_DOMAIN` to every relevant interface.
- Associate each `ETHx_ROUTES` value only with its matching interface.
- Preserve multiple route entries and their interface ownership during
  metadata translation.

## Scaleway

The Scaleway datasource exposes region and availability-zone fields (26.1).
Consumers can use those values for placement-aware behavior.

The datasource no longer handles private-IP metadata. Remove assumptions that
it populates a private-IP value and obtain that information through another
supported source when needed.
