# Storage and Data

## PersistentVolume lifecycle and mutation

### PersistentVolume deletion now always honors reclaim policy (1.33-guide)

Stable finalizers ensure a `Delete` reclaim policy removes backing storage even
when the PV is deleted before the PVC, closing the old deletion-order leak.

### PersistentVolume node affinity is mutable (1.35.0)

`PersistentVolume.spec.nodeAffinity` may be updated after PV creation.

### A Pod can reference one PVC through multiple volumes (1.35.0)

Several entries in one Pod's `volumes` list may use the same PVC.

### PVCs can report when they became unused (1.36.0)

With alpha `PersistentVolumeClaimUnusedSinceTime`, the PVC protection controller
sets `Unused=True` and `lastTransitionTime` when no non-terminal Pod references
the claim.

## CSI capacity and mutable attributes

### CSI mount-point checks no longer imply the inverse (1.33.0)

Drivers using `IsLikelyNotMountPoint` must not interpret `false` as proof that a
path is mounted; an irregular file can also return false and may be acceptable.

### Storage capacity scoring reverses the old preference (1.33.0)

Default-off alpha `StorageCapacityScoring` replaces `VolumeCapacityPriority` and
prefers the node with most allocatable storage; the old feature preferred least.

### CSI allocatable volume counts can be refreshed (1.33.0)

With alpha `MutableCSINodeAllocatableCount`,
`CSINode.spec.drivers[*].allocatable.count` is mutable and
`CSIDriver.spec.nodeAllocatableUpdatePeriodSeconds` controls periodic refresh.

### CSI attach-limit refreshes are default-on (1.35-guide)

The feature is beta and default-on; an insufficient-capacity attach failure also
triggers a count refresh in addition to the periodic update.

### Volume attributes can be changed through a stable API (1.34-guide)

Stable `VolumeAttributesClass` supports online provider-specific changes such as
provisioned I/O when the CSI driver implements `ModifyVolume`.

### ResourceQuota can select a volume class (1.33.0)

The `VolumeAttributesClass` quota scope lets a
`scopeSelector.matchExpressions` rule cap PVC counts for a named class.

### VolumeAttributesClass drops `v1alpha1` (1.35.0)

`storage.k8s.io/v1alpha1` is removed; use the stable API.

## Storage-version and driver migrations

### Storage-version migration is built in (1.35-guide)

Default-on beta native migration handles conflicts and consistency tokens,
replacing fragile `kubectl get`/`replace` loops for schema upgrades or at-rest
reencryption.

### StorageVersionMigration drops `v1alpha1` (1.35.0)

Use `v1beta1` and delete all `v1alpha1` migration resources before upgrading.

### Legacy volume integrations require migration (1.36.0)

The in-tree Portworx plugin and migration gates are removed; operations redirect
to CSI. Kubeadm no longer mounts the flex-volume directory. Temporary continued
flex use requires a non-distroless custom controller-manager image,
`--flex-volume-plugin-dir`, and an `extraVolumes` mount for
`/usr/libexec/kubernetes/kubelet-plugins/volume/exec` before upgrade.

## Image and source volumes

### Image volumes are beta with broader usability (1.33.0)

Image sources support `subPath` and `subPathExpr`, are accepted by Restricted
Pod Security, and expose request, successful-mount, and mount-error counters.

### Image volumes are default-on but runtime-dependent (1.35-guide)

The beta `image` source is default-on for OCI artifacts mounted as data and
needs a compatible runtime such as containerd 2.1+.

### The in-tree `gitRepo` volume driver is disabled (1.33-guide)

The API admits `gitRepo`, but kubelet rejects it when `GitRepoVolumeDriver` is
off. Use an init container or git-sync. At this point the gate temporarily
restores it, with gate and code planned for removal in 1.39.

### The `gitRepo` volume escape hatch is gone (1.36-guide)

The plugin is permanently disabled and no feature gate restores it.

## Snapshots and SELinux

### Volume group snapshots are stable (1.36-guide)

CSI group snapshot APIs create one crash-consistent recovery point across
several PVCs and restore the set into new volumes.

### Snapshot metadata drops `v1alpha1` (1.36.0)

`SnapshotMetadataService` uses `v1beta1`; implementations cannot use the alpha
protocol.

### SELinux volume labeling can happen at mount time (1.36-guide)

GA behavior labels eligible volumes using `mount -o context=...`; CSI drivers
advertise support with `spec.seLinuxMount`. A Pod can retain recursive relabeling
with `securityContext.seLinuxChangePolicy: Recursive`. Audit shared-volume
labels because conflicts can prevent startup.

## ServiceAccount material for CSI

### CSI tokens can use the secrets channel (1.35-guide)

Set `CSIDriver.spec.serviceAccountTokenInSecrets: true` so tokens reach
`NodePublishVolume` in secrets instead of routinely logged `volume_context`.
