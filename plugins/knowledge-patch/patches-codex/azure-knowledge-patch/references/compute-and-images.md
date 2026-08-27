# Compute and images

Use this reference for current compatibility details and exact command or schema changes.

## Disks, snapshots, and restore points

### Confidential disks and instant-access snapshots (2.77.0)

`az disk create` and `az disk grant-access` now support Confidential VM OS
disks. `az snapshot create --instant-access-duration-minutes` sets the instant
access duration for Premium SSD v2 and Ultra Disk snapshots.

### Confidential-VM disk restore encryption (2.76.0)

`az backup restore restore-disks --cvm-os-des-id` selects the Disk Encryption
Set used for a confidential VM's restored OS disk.

### Disk and snapshot output schemas (2.68.0)

The output fields from `az disk` and `az snapshot` have breaking changes to
align them with the backend service. Automation that parses their JSON or
table output must be checked against the 2.68.0 shape.

### Disk PATCH updates and explicit Standard security (2.71.0)

`az disk config update` can change disk size in GB through a PATCH operation.
VM and VM scale-set create/update commands also allow `Standard` as an
explicit security type.

### Fully cached ephemeral OS disks (2.87.0)

VM and VM scale-set creation accept
`--ephemeral-os-disk-enable-full-caching` to use full caching with an
ephemeral OS disk.

### Implicit disk creation during attach (2.76.0)

`az vm disk attach` can create a disk implicitly from snapshots or disk
restore points via `--source-snapshots-or-disks` and
`--source-disk-restore-point`; the implicit disk's size and SKU can also be
set.

### Instant-access restore points (2.85.0)

Restore-point collection create/update accepts `--instant-access`, and
`az restore-point create --instant-access-duration` sets the instant-access
duration.

### Managed-disk security and availability policies (2.78.0)

`az disk create` and `update` accept `--supported-security-option` and
`--action-on-disk-delay`.

### Names for disks created during attach (2.78.0)

`az vm disk attach` accepts `--new-names-of-source-snapshots-or-disks` and
`--new-names-of-source-disk-restore-point` to name newly created disks.

### No-zone disk restores (2.70.0)

`az backup restore restore-disks --target-zone` now accepts `NoZone` as a
valid restore target.

### VM data-disk performance settings (2.84.0)

`az vm create` accepts `--data-disk-mbps` and `--data-disk-iops` to set MBPS
and IOPS for data disks during creation.

### VM disk-encryption identity (2.68.0)

`az vm create` accepts `--encryption-identity` to select the managed identity
used for Azure disk encryption. The same option on `az vm encryption enable`
sets or updates that identity for an existing VM.

### VM zone placement and disk alignment (2.72.0)

`az vm create` gains `--zone-placement-policy`, `--include-zones`, and
`--exclude-zones` for zonal placement. VM create/update also gains
`--align-regional-disks-to-vm-zone` to convert attached regional disks to
zonal disks.

## Images and galleries

### Shared Image Gallery in-VM access controls (2.76.0)

The new `az sig in-vm-access-control-profile` and
`az sig in-vm-access-control-profile-version` groups manage in-VM access
control profiles and their versions.

### Shared Image Gallery managed identity (2.86.0)

`az sig create` can configure a Shared Image Gallery's managed service
identity, `az sig show` returns it, and the new `az sig identity` command
group manages it after creation.

### Shared Image Gallery pagination (2.73.0)

The community/shared image-definition and image-version list commands replace
their old pagination interface with `--max-items` and `--next-token`.

### Shared Image Gallery VHD property remapping (2.72.0)

In a breaking change, `az sig image-version` maps
`--os-vhd-storage-account` to
`properties.storageProfile.osDiskImage.source.storageAccountId` and
`--data-vhds-storage-accounts` to
`properties.storageProfile.dataDiskImages.source.storageAccountId`.

### Shared-image deletion guard (2.71.0)

`az sig image-version create` and `az sig image-version update` accept
`--block-deletion-before-end-of-life` to prevent deletion before the image
version's end-of-life date.

## Scheduled events

### Availability-set scheduled-event policy (2.70.0)

`az vm available-set create` and `az vm available-set update` gain
`--additional-scheduled-events`, `--enable-user-reboot-scheduled-events`, and
`--enable-user-redeploy-scheduled-events`.

### Availability-set scheduled-event profiles (2.79.0)

`az vm availability-set update` accepts `--enable-all-instance-down` and
`--scheduled-events-api-version` for the scheduled-events profile.

### Removed VMSS scheduled-event option (2.75.0)

`az vmss create` and `az vmss update` no longer accept the overlong
`--scheduled-event-additional-publishing-target-event-grid-and-resource-graph`
option. Automation still passing it must be updated.

### Scheduled-events profiles (2.88.0)

`az vm` and `az vmss` create, update, and show operations now surface
scheduled-events profiles through `--scheduled-events-api-version` and
`--enable-all-instance-down`. Availability-set create and show gain the same
support; update already had these options.

### VM scheduled-event policy (2.68.0)

`az vm create` and `az vm update` gain `--additional-scheduled-events`,
`--enable-user-reboot-scheduled-events`, and
`--enable-user-redeploy-scheduled-events` for configuring scheduled-event
policy.

## Virtual machines and scale sets

### Automatic VM application upgrades (2.81.0)

`az vm application set` and `az vmss application set` accept
`--enable-automatic-upgrade` to enable automatic application upgrades.

### Auxiliary tokens during VM creation (2.73.0)

`az vm create` and `az vmss create` now supply auxiliary tokens that were
previously missing.

### Availability-set to VMSS migration (2.78.0)

`az vm availability-set` adds validation, start, cancellation, and conversion
operations for VMSS migration; `az vm migrate-to-vmss` migrates a VM.

### Compute command deprecations (2.71.0)

`--marker` and `--show-next-marker` are deprecated on the shared and community
image-definition and image-version list commands. `az vm list-sizes` is also
deprecated, so new automation should not depend on these interfaces.

### Compute output and option removals (2.69.0)

The gallery-application create/update output field is now
`supportedOSType`, not `supportedOsType`, which is a breaking change for
case-sensitive output consumers. `az vm list-sizes` no longer accepts the
unused `--ids` option.

### Spot placement command replacement (2.76.0)

Use `az compute-recommender spot-placement-score` in place of
`az compute-recommender spot-placement-recommender`.

### Standard VM security is no longer implicit (2.72.0)

VM and VMSS create/update commands now set `--security-type Standard` only
when the caller explicitly supplies it. Automation that needs Standard in the
request must pass the option rather than relying on CLI injection.

### VM and scale-set capabilities (2.69.0)

VM scale-set create/update gains `--zone-balance`; scale now supports edge
zones. Scale-set create and `az vmss encryption enable` gain
`--encryption-identity` for Azure disk-encryption identity, and VM/VMSS
creation automatically installs the guest-attestation extension when the
security type is `ConfidentialVM`.

### VM and VMSS default size (2.87.0)

When no size is supplied, `az vm create` and `az vmss create` now default to
`Standard_D2s_v5` instead of `Standard_DS1_v2`. Pass `--size` or `--vm-sku`
explicitly when provisioning must remain stable across CLI versions.

### VM and VMSS metadata-endpoint controls (2.72.0)

VM and VMSS create/update commands gain `--wire-server-mode` with
`--wire-server-access-control-profile-reference-id`, plus `--imds-mode` with
`--imds-access-control-profile-reference-id`. They also accept
`--key-incarnation-id`.

### VM and VMSS ProxyAgent installation (2.80.0)

`az vm` and `az vmss` create and update accept
`--add-proxy-agent-extension` to control whether the ProxyAgent Extension is
installed implicitly.

### VM scale-set security posture arguments (2.68.0)

`az vmss create` and `az vmss update` gain
`--security-posture-reference-is-overridable`. The existing
`--security-posture-reference-exclude-extensions` option now receives a
string list, so callers can pass multiple excluded extensions.

### VM zone movement and force deallocation (2.87.0)

VM create/update operations accept `--zone-movement`, and existing VMs can be
moved across zones through `az vm update`. `az vm deallocate
--force-deallocate` performs a forced deallocation.

### VMSS automatic repairs (2.76.0)

`az vmss create --enable-automatic-repairs` configures the scale set's
automatic-repairs policy during creation.

### VMSS automatic zone placement (2.85.0)

`az vmss create --zone-placement-policy Auto` can constrain automatic
placement with `--include-zones`, `--exclude-zones`, and `--max-zone-count`;
VMSS update also gains `--max-zone-count`. Create/update can enforce a
per-zone instance percentage with `--instance-percent-policy` and
`--value-max-instance-percent-per-zone`.

### VMSS resiliency views (2.82.0)

`az vmss list-instances --resiliency-view` includes each instance's resiliency
status, while `az vmss get-resiliency-view` retrieves the per-instance view
directly.

### VMSS zone balancing and instance-mix ranking (2.73.0)

VMSS create/update accepts `--enable-automatic-zone-balancing`,
`--automatic-zone-balancing-strategy`, and
`--automatic-zone-balancing-behavior`. It also accepts `--skuprofile-rank` as
a list of ranks for the instance-mix SKU profile's VM sizes.

### VMSS zone-placement updates (2.88.0)

`az vmss update` now accepts `--zone-placement-policy`, `--include-zones`,
and `--exclude-zones`, extending the automatic zone-placement controls to
existing scale sets.
