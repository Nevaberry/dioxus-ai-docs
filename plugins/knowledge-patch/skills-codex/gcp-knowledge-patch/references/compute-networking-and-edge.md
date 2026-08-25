# Compute, Networking, and Edge

Use this reference for compute, networking, and edge compatibility details and current behavior.

## Networking, regions, and connectivity

### Compute Engine boot-disk IAM relaxation (2026-07-2)

`iam.serviceAccounts.actAs` is no longer required for several operations on the boot disk of an instance with an attached service account: standard or archive snapshots, disk cloning, machine or custom images, asynchronous cross-region replication, and creating an instance disk from an instant snapshot.


### Python UDF execution and observability (2026-04)

Preview Python UDFs add vectorized Apache Arrow `RecordBatch` execution, Cloud Monitoring metrics, and the `container_request_concurrency` option. They also gain 10 GiB image-storage and 30-mutations-per-minute quotas per project and region, while costs appear in `INFORMATION_SCHEMA.JOBS.external_service_costs` and the Job API's `ExternalServiceCosts` field.


## Managed instance groups and VM fleet operations

### Managed instance group distribution monitoring (2026-07-2)

The Cloud Monitoring **GCE MIG Instance Distribution Monitoring** dashboard shows real-time VM distribution across zones, machine types, and instance states, including fallback behavior for groups that use location or instance flexibility.


### Regional MIG repairs in alternate zones (2026-07-2)

At GA, a regional managed instance group can allow VM repair in an alternate zone when the VM cannot be repaired in its original zone.


### VM Extension Manager policies (2026-07-2)

GA zonal and global VM Extension Manager policies can automatically install and manage extensions such as the Ops Agent across a VM fleet and enforce consistent extension state. Cloud Logging exposes extension-enforcement and guest-agent activity logs for troubleshooting.


## Compute storage and encryption

### Customer-supplied encryption key deprecation (2026-07-2)

Customer-supplied encryption keys for Compute Engine disks, snapshots, images, and machine images are deprecated and will be disabled on July 20, 2027; migrate affected resources before that deadline.


### Hyperdisk Balanced Storage Pool IOPS density (2026-07-2)

The maximum IOPS per GiB is now 30 for standard-performance Hyperdisk Balanced Storage Pools and 6 for advanced-performance pools, increased from 4 IOPS per GiB.


### Hyperdisk ML large-attachment minimum throughput (2026-07-2)

For a Hyperdisk ML volume attached to more than 20 instances, the minimum provisioned throughput is 20 MiB/s per instance instead of 100 MiB/s.


## Compute behavior and limits

### Automatically deployed BigQuery ML open models (2026-03)

GA BigQuery ML remote models can automatically deploy open models to Vertex AI, manage the underlying resources, use Compute Engine reservation affinity, and automatically or immediately undeploy the model.


### BigQuery-managed open-model endpoints (2025-10)

In Preview, BigQuery ML can manage open models as Vertex AI endpoints through SQL, including automatic or immediate undeployment, custom deployment machine types, and Compute Engine reservation affinity.
