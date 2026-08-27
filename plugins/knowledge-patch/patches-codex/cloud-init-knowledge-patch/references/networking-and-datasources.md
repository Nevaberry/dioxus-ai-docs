# Networking and Datasources

Use this reference when generating network configuration, selecting a
datasource, or consuming cloud metadata. Renderer support and datasource
identity are independent: a network renderer can configure an interface
without proving which datasource cloud-init should select.

## Network rendering

### Network v1 device support

Since 26.1, Network v1 can render all of these device types:

- bonds
- bridges
- VLANs

`network-config` can express `allow_accept_ra` for each of those device types.
Keep that property when normalizing, translating, or regenerating Network v1
data. Do not discard it because the device is not a plain physical interface.

### Route metrics in NetworkManager profiles

Since 26.2, the NetworkManager renderer transfers route-metric settings into
the generated connection profiles. Configurations that use metrics to choose
between competing routes no longer require a renderer-specific workaround.

When migrating such a configuration:

1. Retain the route metric in the input network data.
2. Confirm it appears in the generated NetworkManager connection profile.
3. Remove an older workaround only after verifying that the resulting route
   preference remains correct.

### OpenStack bond names

Since 26.1, OpenStack bond names come directly from `network_data.json` rather
than being forced to `bond0`, `bond1`, and so on. Treat the supplied name as the
stable input to later rendering.

Review downstream code that predicts or rewrites bond names. Tests and device
lookups must use the metadata-provided name instead of assuming a sequential
`bondN` identifier.

### OpenNebula search domains and routes

Since 26.2, OpenNebula network metadata accepts:

- A global `SEARCH_DOMAIN`, applied to all interfaces.
- `ETHx_ROUTES` values, carrying per-interface static routes.

Keep the different scopes intact. Apply the search domain globally and attach
each `ETHx_ROUTES` value only to its corresponding interface.

## Datasource identity

### Non-x86 systems without DMI

The behavior represented in 26.1 has applied since 25.1.4: Ec2, OpenStack, and
AltCloud systems without DMI no longer fall back to probing link-local metadata
after networking. Cloud-init stays disabled until the datasource is identified
by one of the following:

- DMI data
- A kernel `ds=` override
- `datasource_list` configuration

For OpenStack, a config drive can identify the datasource. An image dedicated
to OpenStack can instead force the selection in
`/etc/cloud/cloud.cfg.d/91_openstack.cfg`:

```yaml
datasource_list: [ OpenStack ]
```

Use that override only when binding the image to OpenStack is intentional. A
working network and a responsive link-local metadata endpoint do not restore
the removed fallback.

## Datasource configuration and metadata

### Azure network naming and ready reporting

Since 26.2, the Azure datasource provides
`apply_network_config_set_name`, allowing application of network-config
`set-name` directives to be disabled. Use this control when interface renaming
must remain outside cloud-init's Azure network-config application.

Azure also provides the experimental `skip_ready_report` option, which
suppresses its ready report. Keep this experimental control separate from
interface naming: changing one should not implicitly change the other.

### Azure missing custom data

Since 26.2, missing Azure custom data is reported as a provisioning failure
rather than silently continuing. Automation that watches provisioning must
accept and expose this explicit failure, and tests should no longer expect the
missing-data path to succeed silently.

### Scaleway location fields

Since 26.1, the Scaleway datasource exposes region and availability-zone
fields. It no longer handles private-IP metadata.

Use the location fields directly where region or zone is needed. Remove any
consumer dependency on Scaleway datasource private-IP metadata, because the
datasource will not populate it.

## Platform discovery inputs

### CloudStack virtual-router discovery

Since 26.2, CloudStack can obtain virtual-router information from
NetworkManager leases. Include lease data in discovery diagnosis before adding
or retaining a separate virtual-router workaround.

### Oracle iSCSI-root discovery

Since 26.2, Oracle dracut images can detect an iSCSI root through iBFT. For a
dracut-based Oracle image, check iBFT discovery before assuming the root device
requires a local detection patch.
