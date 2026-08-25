# Storage and Data

Use this reference for PersistentVolumes, CSI capacity and mutation, image
volumes, snapshots, storage-version migration, SELinux labeling, and removed
volume integrations.

## PersistentVolume and PVC lifecycle

### Honor Delete reclaim policy in either deletion order (1.33-guide)

Stable finalizers ensure that a PV with reclaim policy `Delete` removes backing
storage even if the PV is deleted before its PVC.

### Update PV node affinity when needed (1.35.0)

`PersistentVolume.spec.nodeAffinity` is mutable after PV creation.

### Reuse one PVC in multiple Pod volumes (1.35.0)

Multiple entries in a Pod's `volumes` list may reference the same
PersistentVolumeClaim.

### Observe when a PVC became unused (1.36.0)

Alpha `PersistentVolumeClaimUnusedSinceTime` makes the PVC protection
controller set an `Unused=True` condition and `lastTransitionTime` when no
non-terminal Pod references the claim.

## CSI capacity and attach limits

### Do not invert mount-point checks (1.33.0)

A false result from CSI `IsLikelyNotMountPoint` does not prove that a path is a
mount point; irregular files can also produce false and may be acceptable.

### Understand capacity scoring (1.33.0)

Alpha default-off `StorageCapacityScoring` replaces `VolumeCapacityPriority`.
The new behavior prefers the node with the most allocatable storage; the old
feature preferred the least.

### Refresh CSI allocatable counts (1.33.0, 1.35-guide)

`MutableCSINodeAllocatableCount` makes
`CSINode.spec.drivers[*].allocatable.count` mutable and uses
`CSIDriver.spec.nodeAllocatableUpdatePeriodSeconds` for periodic refresh. It is
beta and default-on, and an attach failure caused by insufficient capacity also
triggers refresh.

## VolumeAttributesClass

### Modify volume attributes online (1.34-guide)

Stable `storage.k8s.io/v1` `VolumeAttributesClass` supports provider-specific
online changes such as provisioned I/O when the CSI driver implements
`ModifyVolume`.

### Apply class-specific quota (1.33.0)

The `VolumeAttributesClass` ResourceQuota scope matches PVCs using a named
class. Use `scopeSelector.matchExpressions` to cap their count.

### Remove alpha objects (1.35.0)

`storage.k8s.io/v1alpha1` VolumeAttributesClass is removed. Convert clients and
manifests to the stable API before upgrading.

## Image and source volumes

### Use image volumes with runtime checks (1.33.0, 1.35-guide)

The beta `image` source mounts OCI artifacts as data and is enabled by default.
It supports `subPath` and `subPathExpr`, is accepted by Restricted Pod Security,
and exposes request, successful-mount, and mount-error counters. Use a
compatible runtime such as containerd 2.1 or newer.

### Replace `gitRepo` completely (1.33-guide, 1.36-guide)

The API may still admit a `gitRepo` source, but kubelet rejects it. The former
`GitRepoVolumeDriver` escape hatch is permanently gone. Clone from an init
container or use git-sync.

## Storage-version and protocol migrations

### Use native storage-version migration (1.35-guide)

The beta default-on controller handles conflicts and consistency tokens for
schema changes and at-rest re-encryption. Prefer it over manual `kubectl get`
and `kubectl replace` loops.

### Remove StorageVersionMigration alpha (1.35.0)

Use the `v1beta1` API. Delete every `v1alpha1` StorageVersionMigration before
upgrading.

### Upgrade snapshot metadata protocol (1.36.0)

`SnapshotMetadataService` uses `v1beta1`; implementations can no longer use its
`v1alpha1` protocol.

## Snapshots

### Take volume-group snapshots (1.36-guide)

Stable CSI volume-group snapshot APIs create one crash-consistent recovery
point across multiple PVCs and restore the snapshot set into new volumes.

## SELinux volume labeling

### Label eligible volumes at mount time (1.36-guide)

Stable behavior uses `mount -o context=...` rather than recursively rewriting
files when a CSI driver advertises `spec.seLinuxMount`. A Pod can retain
recursive relabeling with
`securityContext.seLinuxChangePolicy: Recursive`:

```yaml
spec:
  securityContext:
    seLinuxChangePolicy: Recursive
```

Audit labels on shared volumes; conflicting Pod labels can prevent startup.

## Removed volume integrations

### Migrate Portworx and flex volumes before upgrade (1.36.0)

The in-tree Portworx plugin and migration gates are removed, with operations
redirected to CSI. Kubeadm no longer mounts the flex-volume directory. A
temporary flex-volume continuation requires a non-distroless custom
controller-manager image, `--flex-volume-plugin-dir`, and an `extraVolumes`
mount for `/usr/libexec/kubernetes/kubelet-plugins/volume/exec`; migrate to CSI
instead.
