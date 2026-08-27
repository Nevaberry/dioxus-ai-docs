# Compute, Networking, and Edge

Use this reference for Compute Engine instance groups, VM fleet operations, disk behavior, cross-service regional availability, and infrastructure monitoring.

Availability labels and version gates are part of each item. Keep Preview behavior gated, and apply the latest lifecycle entry when an item has several dated updates.

## IAM and encryption migrations

### Compute Engine boot-disk IAM relaxation

*2026-07-2*

`iam.serviceAccounts.actAs` is no longer required for several operations on the boot disk of an instance with an attached service account: standard or archive snapshots, disk cloning, machine or custom images, asynchronous cross-region replication, and creating an instance disk from an instant snapshot.

### Customer-supplied encryption key deprecation

*2026-07-2*

Customer-supplied encryption keys for Compute Engine disks, snapshots, images, and machine images are deprecated and will be disabled on July 20, 2027; migrate affected resources before that deadline.

## Managed instance groups and fleet management

### Managed instance group distribution monitoring

*2026-07-2*

The Cloud Monitoring **GCE MIG Instance Distribution Monitoring** dashboard shows real-time VM distribution across zones, machine types, and instance states, including fallback behavior for groups that use location or instance flexibility.

### Regional MIG repairs in alternate zones

*2026-07-2*

At GA, a regional managed instance group can allow VM repair in an alternate zone when the VM cannot be repaired in its original zone.

### VM Extension Manager policies

*2026-07-2*

GA zonal and global VM Extension Manager policies can automatically install and manage extensions such as the Ops Agent across a VM fleet and enforce consistent extension state. Cloud Logging exposes extension-enforcement and guest-agent activity logs for troubleshooting.

## Disks and storage performance

### Hyperdisk Balanced Storage Pool IOPS density

*2026-07-2*

The maximum IOPS per GiB is now 30 for standard-performance Hyperdisk Balanced Storage Pools and 6 for advanced-performance pools, increased from 4 IOPS per GiB.

### Hyperdisk ML large-attachment minimum throughput

*2026-07-2*

For a Hyperdisk ML volume attached to more than 20 instances, the minimum provisioned throughput is 20 MiB/s per instance instead of 100 MiB/s.

## Regions and network availability

### Bangkok region availability

*2026-01*

BigQuery, Cloud Run, GKE, and Pub/Sub are available in the Bangkok region, `asia-southeast3`.

### Regional availability

*2025-03*

BigQuery, Cloud Run, and Pub/Sub are available in `europe-north2`; Cloud Run also adds `northamerica-south1`, and Cloud Run GPUs add `europe-west1`.
