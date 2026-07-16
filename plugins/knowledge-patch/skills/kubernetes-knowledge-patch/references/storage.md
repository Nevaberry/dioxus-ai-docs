# Storage and Data

Use this reference for PersistentVolumes, CSI, snapshots, volume attributes, image and git volumes, migration, and volume security behavior.

Entries are grouped by task; the parenthetical identifier is the source batch.

## A Pod can reference one PVC through multiple volumes (1.35.0)

Multiple entries in a Pod's `volumes` list may now use the same `PersistentVolumeClaim`.

## CSI allocatable volume counts can be refreshed (1.33.0)

With the alpha `MutableCSINodeAllocatableCount` gate, `CSINode.spec.drivers[*].allocatable.count` becomes mutable and `CSIDriver.spec.nodeAllocatableUpdatePeriodSeconds` controls periodic refreshes, preventing scheduling from relying indefinitely on stale capacity.

## CSI attach-limit refreshes are default-on (1.35-guide)

`MutableCSINodeAllocatableCount` remains beta but is enabled by default, and an insufficient-capacity attach failure now triggers an update of `CSINode.spec.drivers[*].allocatable.count` in addition to periodic refreshes.

## CSI mount-point checks no longer imply the inverse (1.33.0)

CSI drivers using `IsLikelyNotMountPoint` must not interpret a `false` result as proof that a path is a mount point; an irregular file can also produce that result and may still be acceptable.

## CSI tokens can use the secrets channel (1.35-guide)

A CSI driver can set `CSIDriver.spec.serviceAccountTokenInSecrets: true` to receive ServiceAccount tokens in the `NodePublishVolume` secrets field instead of the routinely logged `volume_context` field.

## Image volumes are beta with broader usability (1.33.0)

Image volume sources now support `subPath` and `subPathExpr` and are accepted by the Restricted Pod Security Admission profile; kubelet also exposes request, successful-mount, and mount-error counters for them.

## Image volumes are default-on but runtime-dependent (1.35-guide)

The beta `image` volume source is enabled by default for delivering OCI artifacts as mounted data. It requires a compatible runtime, such as containerd 2.1 or newer.

## Legacy volume integrations require migration (1.36.0)

The in-tree Portworx plugin and its migration gates are removed, with operations redirected to CSI. Kubeadm no longer mounts the flex-volume directory automatically; continued use requires a non-distroless custom controller-manager image, `--flex-volume-plugin-dir`, and an `extraVolumes` mount for `/usr/libexec/kubernetes/kubelet-plugins/volume/exec` before upgrading.

## PersistentVolume deletion now always honors reclaim policy (1.33-guide)

Stable finalizers on relevant PVs ensure that a `Delete` reclaim policy removes the backing storage even when the PV is deleted before its PVC, eliminating the old deletion-order leak.

## PersistentVolume node affinity is mutable (1.35.0)

`PersistentVolume.spec.nodeAffinity` can now be updated after the PersistentVolume is created.

## PVCs can report when they became unused (1.36.0)

With the alpha `PersistentVolumeClaimUnusedSinceTime` gate, the PVC protection controller sets an `Unused=True` condition and `lastTransitionTime` when no non-terminal Pod references the claim.

## ResourceQuota can select a volume class (1.33.0)

The new `VolumeAttributesClass` quota scope matches PVCs using a named volume attributes class, so a `scopeSelector.matchExpressions` rule can cap PVC counts for that class.

## SELinux volume labeling can happen at mount time (1.36-guide)

The GA behavior labels eligible volumes with `mount -o context=...` instead of recursively rewriting files, while CSI drivers advertise support through `spec.seLinuxMount`. Pods can retain recursive relabeling with `securityContext.seLinuxChangePolicy: Recursive`; audit shared-volume labels because conflicts can prevent Pods from starting.

```yaml
spec:
  securityContext:
    seLinuxChangePolicy: Recursive
```

## Snapshot metadata drops `v1alpha1` (1.36.0)

`SnapshotMetadataService` is now `v1beta1`, and implementations can no longer use its `v1alpha1` protocol.

## Storage capacity scoring reverses the old preference (1.33.0)

The alpha, default-off `StorageCapacityScoring` gate replaces `VolumeCapacityPriority`: it prefers the node with the most allocatable storage, whereas the replaced feature preferred the least.

## Storage-version migration is built in (1.35-guide)

Native storage-version migration is beta and enabled by default. Its in-tree controller handles conflicts and consistency tokens, replacing fragile manual `kubectl get` and `kubectl replace` loops for schema upgrades or at-rest re-encryption.

## StorageVersionMigration drops `v1alpha1` (1.35.0)

The migration API is now `v1beta1`, and `v1alpha1` is no longer supported. Delete all `v1alpha1` StorageVersionMigration resources before upgrading.

## The `gitRepo` volume escape hatch is gone (1.36-guide)

The in-tree `gitRepo` plugin is permanently disabled in 1.36 and can no longer be restored with a feature gate; workloads must clone through an init container or a tool such as git-sync.

## The in-tree `gitRepo` volume driver is disabled (1.33-guide)

The API still admits `gitRepo` volumes, but kubelets with `GitRepoVolumeDriver` disabled reject them; use an init container or git-sync instead. The gate can temporarily re-enable the driver, but the gate and remaining plugin code are planned for removal in 1.39.

## Volume attributes can be changed through a stable API (1.34-guide)

`VolumeAttributesClass` is stable for online changes to provider-specific volume properties such as provisioned I/O; the CSI driver must implement the CSI `ModifyVolume` operation.

## Volume group snapshots are stable (1.36-guide)

The CSI volume-group snapshot extension APIs can take one crash-consistent recovery point across several PersistentVolumeClaims and restore the resulting snapshot set into new volumes.

## VolumeAttributesClass drops `v1alpha1` (1.35.0)

The `storage.k8s.io/v1alpha1` VolumeAttributesClass resource is removed; clients and manifests must use the stable API.

