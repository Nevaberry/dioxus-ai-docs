# Networking and Datasources

This reference contains the networking and datasource changes from batch
`26.1`, including compatibility behavior introduced in earlier releases where
that behavior is required to understand the current result.

## Network v1 rendering

Network v1 can render bonds, bridges, and VLANs. Code that validates, converts,
or emits network v1 data should therefore retain these device definitions
instead of rejecting them as unsupported.

The `network-config` representation can express `allow_accept_ra` for each of
these device types:

- bonds
- bridges
- VLANs

Preserve this value through parsing and rendering. A translator that keeps the
device but drops `allow_accept_ra` loses part of the supported configuration.

## OpenStack bond naming

Bond names for the OpenStack datasource come directly from
`network_data.json`. Earlier behavior forced sequential names such as `bond0`,
`bond1`, and so on; current integrations must not reproduce that renaming.

Use the metadata-provided bond name in:

- rendered network configuration
- relationships between a bond and its member devices
- downstream references to the bond
- fixtures and assertions that validate OpenStack network data

When an upgrade changes a bond name, first compare the value in
`network_data.json` with any downstream normalizer. A local `bondN` rewrite is
an integration bug under the current naming behavior.

## Strict datasource identity without DMI

Since 25.1.4, datasource selection is stricter on non-x86 systems that do not
provide DMI. The affected datasources are:

- Ec2
- OpenStack
- AltCloud

These systems no longer wait until networking is available and then probe
link-local metadata as a fallback. Without positive datasource identification,
cloud-init stays disabled.

Accepted identification paths are:

1. Matching DMI data, when the platform provides it.
2. A kernel `ds=` override.
3. An explicit `datasource_list` entry.

The important distinction is identity rather than reachability. A metadata
endpoint becoming reachable after network setup does not identify the
datasource through the removed fallback.

### OpenStack mitigations

An OpenStack config drive can provide a path to correct identification. For an
image dedicated to OpenStack, the datasource can instead be forced in
`/etc/cloud/cloud.cfg.d/91_openstack.cfg`:

```yaml
datasource_list: [ OpenStack ]
```

Use an explicit list only when constraining datasource selection is intended.
For a multi-cloud image, prefer a platform-provided identity mechanism rather
than labeling every boot as OpenStack.

### Diagnostic sequence

For a disabled affected instance:

1. Confirm the architecture and whether DMI is present.
2. Inspect the kernel command line for a `ds=` selection.
3. Inspect cloud configuration for `datasource_list`.
4. On OpenStack, check for a config drive.
5. Do not rely on a post-network link-local probe to recover selection.

This sequence avoids conflating a working metadata network path with a selected
datasource.

## Scaleway metadata

The Scaleway datasource exposes region and availability-zone fields. Consumers
that need placement information can read these fields from datasource metadata.

The datasource no longer handles private-IP metadata. Remove dependencies that
expect it to discover or populate a private IP through that metadata path.

When adapting a consumer, treat these as two independent changes:

- location metadata is available through region and availability zone;
- private-IP metadata is no longer supplied by the datasource.

Do not substitute region or availability-zone values for a private address, and
do not infer that the absence of private-IP metadata means the datasource
failed.
