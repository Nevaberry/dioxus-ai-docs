# Storage and Volumes

## Dynamic host volumes

Since 1.10.0, Nomad can create host volumes through the CLI or API without
restarting clients, and stateful deployments can use them.

```shell
nomad volume create ./internal-plugin.volume.hcl
```

Jobs consume dynamic host volumes with `volume` and `volume_mount` blocks. The
scheduler tracks availability, but Nomad does not interpret the underlying
storage, so a volume may use local or highly available network storage.

Nomad Enterprise can evaluate volume specifications with Sentinel during
creation, apply per-namespace host-volume capacity quotas, and validate a
requested node pool against the namespace's node-pool configuration.

## Volume CLI and visibility

Since 1.10.0, `nomad volume status` shows volume capabilities.
`nomad volume delete` accepts a volume ID prefix and a wildcard namespace. CSI
volume and plugin events are included in the event stream.

## Quota storage schema

Since 1.10.0, the quota `variables_limit` field and API
`QuotaSpec.VariablesLimit` are deprecated for removal in 1.12. Use
`region_limit.storage.variables` and
`QuotaSpec.RegionLimit.Storage.Variables`.

The Go API type of `QuotaSpec.RegionLimit` changes from `Resources` to
`QuotaResources`.

## Scheduling capacity

In the `1.11-upgrade` guidance, available storage for scheduling is calculated
as `totalBytes - client.reserved.disk` instead of free disk space, and the
`unique.storage.bytesfree` attribute is removed. Reserve at least the disk space
consumed by the host operating system.
