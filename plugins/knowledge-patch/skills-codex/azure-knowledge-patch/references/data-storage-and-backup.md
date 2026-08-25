# Data, storage, and backup

Use this reference for current compatibility details and exact command or schema changes.

## Azure Backup

### Azure Files Vault Standard backup policies (2.69.0)

The `az backup` command group now supports AFS Vault Standard policies.

### Backup cost-management settings (2.89.0)

Azure Backup CLI operations now support cost-management settings.

### Backup reconfiguration to another vault (2.78.0)

The new `az backup protection reconfigure` command can reconfigure protection
to use an alternate vault.

### Deleted Backup vault recovery (2.79.0)

The new `az backup vault deleted-vault` command group can list and undelete
deleted Backup vaults.

### New Azure Backup workload support (2.74.0)

The `az backup container`, `item`, `policy`, and `protection` command groups
now support ASE backup operations, and `az backup` supports HANA Snapshot.

## Azure NetApp Files

### Azure NetApp Files clone splitting (2.78.0)

`az netappfiles volume splitclonefromparent` splits a clone from its parent;
volume creation also accepts `--grow-pool-clone-split`.

### Azure NetApp Files configuration changes (2.73.0)

`az volume-group create` no longer requires `--proximity-placement-group`.
NetApp account create/update accepts `--federated-client-id` for cross-tenant
customer-managed keys and `--nfs-v4-id-domain` for NFSv4 user-ID mapping.

### Azure NetApp Files cool-access tiering (2.70.0)

`az netappfiles volume create` and `az netappfiles volume update` accept
`--cool-access-tiering-policy`.

### Azure NetApp Files encryption-key transitions (2.70.0)

`az netappfiles account change-key-vault` changes the Key Vault or Managed HSM
used to encrypt an account's volumes. `get-key-vault-status` supplies Key Vault
information for `transitiontocmk`, which transitions all volumes in a VNet to
a different Microsoft-managed or Key Vault key source; it fails when targeted
volumes share an encryption sibling set with another account's volumes.

### Azure NetApp Files ransomware and quota reports (2.85.0)

NetApp Files volume create/update accepts
`--desired-ransomware-protection-state`. The new
`az netappfiles volume ransomware-report` group exposes advanced ransomware
reports, while `az netappfiles volume list-quota-report` lists volume quota
reports.

### DMS location and NetApp endpoint type (2.80.0)

`az dms project create` no longer requires `--location`. NetApp volume create
and update no longer accept the read-only `--endpoint-type` argument.

### Flexible Azure NetApp Files throughput (2.78.0)

Pool and volume creation accept `Flexible` as a service level, and
`az netappfiles pool create` accepts `--custom-throughput-mibps`.

### NetApp Files Breakthrough Mode (2.89.0)

`az netappfiles volume create` accepts `--breakthrough-mode` to select whether
the volume operates in Breakthrough Mode.

### NetApp Files Cache and Bucket resources (2.87.0)

The new `az netappfiles cache` and `az netappfiles volume bucket` command
groups manage Cache and Bucket resources.

### NetApp Files subvolume deprecations (2.88.0)

The `az netappfiles subvolume` command group is deprecated, as is
`--enable-subvolumes` on NetApp Files volume create and update. Both are
announced for removal in a future release.

### NetApp Files volume interface changes (2.87.0)

For `az netappfiles volume create`, the default for `--network-features` is
now `Standard`. The `az netappfiles volume update
--remote-volume-resource-id` option is deprecated.

### NetApp Files volume-group networking and replication filtering (2.81.0)

`az netappfiles volume-group create` accepts `--network-features` for volume
groups. `az netappfiles volume replication list` accepts `--exclude` to omit
deleted replications.

### Oracle Azure NetApp Files volume groups (2.74.0)

`az netappfiles volume-group create` now supports Oracle in ANF Volume Groups.

## Azure SQL

### Cross-subscription SQL geo-replication (2.75.0)

`az sql db replica create` can specify the partner subscription ID when
creating a cross-subscription geo-replica.

### Soft-deleted SQL server lifecycle (2.84.0)

`az sql server create` and `update` accept `--soft-delete-retention-days`.
The new `az sql server deleted-server show` and `list` commands inspect
deleted servers, and `az sql server restore` restores one.

### SQL long-term retention and failover groups (2.76.0)

`az sql ltr-policy set` removes the unused `--access-tier` option, so callers
must stop passing it. `az sql failover-group create` now supports multiple
partner failover groups.

### SQL long-term-retention immutability (2.78.0)

The `az sql db ltr-backup` group adds commands for LTR immutability.

### SQL Managed Instance memory sizing (2.82.0)

`az sql mi create` and `update` can set the managed instance's memory size in
GB.

### SQL serverless-to-provisioned updates (2.79.0)

When `az sql db update` moves a database from serverless to provisioned, it
no longer overwrites the selected service-level objective.

### Versionless SQL TDE keys (2.84.0)

Azure SQL server and database commands now support versionless Transparent
Data Encryption keys.

## Azure Storage and Files

### Azure Files NFS operations (2.71.0)

The storage share, directory, and file commands support NFS file shares, and
`az storage file hard-link create` creates hard links for NFS files.

### Azure Files restore after source-account deletion (2.77.0)

`az backup restore restore-azurefileshare` now supports restores whose source
storage account has been deleted by including the required source resource ID
in the request.

### File-service transport encryption requirements (2.83.0)

`az storage account file-service-properties update` adds
`--require-smb-encryption-in-transit` and
`--require-nfs-encryption-in-transit`.

### Managed-identity OAuth for SMB shares (2.78.0)

`az storage account create` and `update` accept `--enable-smb-oauth`, allowing
managed identities to access SMB shares through OAuth.

### NFS file listing (2.79.0)

`az storage file list` now handles NFS shares; `--include` remains unsupported
for those shares.

### NFS file-share symbolic links (2.78.0)

`az storage file symoblic-link create` and `show` manage symbolic links on
NFS file shares.

### OAuth file listing without Reader access (2.83.0)

`az storage file list` now works with OAuth when the caller does not have
Reader access.

### OAuth for Azure Files batch transfers (2.75.0)

`az storage file upload-batch` and `az storage file download-batch` now
support OAuth login.

### Provisioned Azure Files controls (2.70.0)

`az storage account create --sku` adds `StandardV2_LRS`, `StandardV2_ZRS`,
`PremiumV2_LRS`, and `PremiumV2_ZRS` for provisioned v2 accounts, and
`az storage account file-service-usage` reports file-service usage. Share
create/update gains `--paid-bursting-enabled`,
`--paid-bursting-max-bandwidth-mibps`, and `--paid-bursting-max-iops` for
provisioned v1, plus `--provisioned-bandwidth-mibps` and `--provisioned-iops`
for provisioned v2.

### Storage account and blob-service controls (2.87.0)

Storage account create/update accepts the `Smart` value for `--access-tier`
and adds `--allowed-copy-scope`. Blob-service-properties update can configure
static website enablement, index documents, and the 404 document through
`--enable-static-website`, `--index-document`,
`--default-index-document-path`, and `--error-document-404-path`; object
replication policy create/update also accepts `--tags-replication`.

### Storage failover and listing behavior (2.80.0)

`az storage account failover --failover-type` now accepts `Unplanned`.
`az storage file list` now returns its additional information even when no
protocol is explicitly selected.

### Storage IPv6 endpoints and network rules (2.83.0)

Storage account create/update adds `--publish-ipv6-endpoint`, while
`az storage account network-rule add` and `remove` add `--ipv6-address`.

### Storage SAS expiration actions (2.75.0)

`az storage account create` and `az storage account update` accept
`--sas-expiration-action` as part of the account's SAS policy.

### Storage-account migration confirmation (2.73.0)

`az storage account migration start` now asks for confirmation before
migrating an account between redundancy options.

### Storage-account network security perimeters (2.79.0)

The `az storage account network-security-perimeter-configuration` group adds
`list`, `show`, and `reconcile` operations for network security perimeters.

### Storage-account zone placement (2.78.0)

`az storage account create` and `update` accept `--zones` and
`--zone-placement-policy` for zones and availability-zone pinning.

### User-delegation SAS expansion (2.82.0)

`az storage blob generate-sas`, `az storage container generate-sas`,
`az storage fs generate-sas`, `az storage fs file generate-sas`, and
`az storage fs directory generate-sas` accept `--user-delegation-oid`; the
filesystem-file command is new. `az storage share generate-sas`,
`az storage file generate-sas`, and `az storage queue generate-sas` add that
option together with `--as-user`.

## Cosmos DB

### Cosmos DB burst capacity (2.68.0)

`az cosmosdb create` and `az cosmosdb update` accept
`--enable-prpp-autoscale` to enable or disable the burst-capacity feature.

### Cosmos DB fleets and local authentication (2.82.0)

`az cosmosdb fleet` is the new command group for Cosmos DB fleets. Account
create and update also accept `--disable-local-auth` so local authentication
can be disabled.

### Cosmos DB region offlining (2.70.0)

`az cosmosdb offline-region` can take a region in a Cosmos DB account offline.

### Cosmos DB restore validation behavior (2.76.0)

`az cosmosdb restore` no longer performs the CLI-side validations that could
time out for large restores or report incorrect errors; restore requests now
proceed without those checks.

### Cosmos DB SQL full-text policies (2.74.0)

`az cosmosdb sql container` now supports Full Text Policy configuration.

### Fabric workspaces in Cosmos DB ACL bypasses (2.84.0)

`az cosmosdb update --network-acl-bypass-resource-ids` now accepts Microsoft
Fabric workspace resource IDs.

## Data and messaging services

### Cross-tenant user-delegation SAS (2.86.0)

The blob, container, share, file, queue, and filesystem `generate-sas`
commands accept `--user-delegation-tid` to issue a user-delegation SAS for a
different tenant.

### Event Hubs network security perimeter configuration (2.76.0)

`az eventhubs namespace nsp-configuration show` and `list` expose namespace
network security perimeter configuration.

### Geo-priority replication (2.79.0)

Storage-account create and update accept
`--enable-blob-geo-priority-replication` for Geo SLA. Object-replication
policy create and update accept `--priority-replication` for priority
replication.

### IoT Hub device streams move to an extension (2.77.0)

The `az iot hub devicestream` command group is now supplied by the
`azure-iot` extension rather than Azure CLI itself.

### IoT Hub minimum TLS version (2.70.0)

`az iot hub update` accepts `--min-tls-version` to change the hub's minimum
TLS version.

### Object-replication metrics (2.78.0)

`az storage account or-policy create` and `update` accept `--enable-metrics`
to enable object-replication metrics.

### Redis zoning and system-identity connections (2.69.0)

`az redis create` and `az redis update` gain `--zonal-allocation-policy` for
choosing cache zones. `az webapp connection create redis` gains
`--system-identity`.

### Snapshot virtual-directory access (2.71.0)

`az storage share create` accepts
`--enable-snapshot-virtual-directory-access` for snapshot virtual-directory
access.

### Standard-policy TVM protection (2.73.0)

`az backup protection enable-for-vm` now supports protecting a TVM with a
standard policy.

### TLS 1.0 and 1.1 inputs are coerced to TLS 1.2 (2.83.0)

On storage account create/update, passing `--min-tls-version tls1_0` or
`tls1_1` now sets the value to `tls1_2`.

## MySQL Flexible Server

### Cross-subscription MySQL operations (2.83.0)

MySQL flexible-server `restore`, `geo-restore`, and `replica create` now
support targeting a different subscription.

### Deleting on-demand MySQL backups (2.82.0)

`az mysql flexible-server backup delete` can delete an on-demand backup.

### MySQL 8.4 upgrades (2.77.0)

`az mysql flexible-server upgrade --version 8.4` is now supported.

### MySQL Accelerated Logs (2.78.0)

`az mysql flexible-server create` and `update` support Accelerated Logs for
the GeneralPurpose tier.

### MySQL backup and accelerated restore controls (2.72.0)

MySQL flexible-server creation accepts `--backup-interval`. Restore accepts
`--faster-restore` to enable automatic IOPS scaling, and replica creation
accepts `--faster-provisioning` for the same behavior while provisioning.

### MySQL backup interval updates (2.76.0)

MySQL flexible-server create/update exposes the revised
`--storage-redundancy` option and `--backup-interval`; unlike the earlier
create-only support, update can now set the backup interval.

### MySQL BC storage-redundancy default (2.74.0)

`az mysql flexible-server create` now defaults storage redundancy to local
redundancy for BC SKUs; pass the redundancy explicitly when provisioning must
not inherit this changed default.

### MySQL Fabric Mirroring controls (2.89.0)

`az mysql flexible-server mirroring enable` and `disable` manage Fabric
Mirroring for a flexible server.

### MySQL flexible-server default changes (2.71.0)

In a breaking change, `az mysql flexible-server create` changes the defaults
for both `--auto-scale-iops` and `--version`. Reproducible provisioning should
pass both values explicitly rather than inheriting the CLI defaults.

```bash
az mysql flexible-server create --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER" --auto-scale-iops "$AUTO_SCALE_IOPS" \
  --version "$MYSQL_VERSION"
```

### MySQL flexible-server storage redundancy (2.68.0)

`--storage-redundancy` is available on flexible-server create, restore,
replica create, and geo restore to request HA storage with zone redundancy.

### MySQL maintenance batches (2.89.0)

`az mysql flexible-server update` accepts `--maintenance-batch` with
`Default`, `Batch1`, or `Batch2` for a custom-managed maintenance window. If
the option is omitted, the server's existing batch is preserved.

```bash
az mysql flexible-server update --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER" --maintenance-batch Batch1
```

### MySQL storage-redundancy argument removed (2.87.0)

MySQL flexible-server backup create, restore, geo-restore, and replica
operations no longer accept `--storage-redundancy`; remove it from scripts
before upgrading the CLI.

## PostgreSQL Flexible Server

### Announced PostgreSQL flexible-server interface changes (2.86.0)

Create, replica-create, restore, geo-restore, and revive-dropped operations
now warn of an upcoming breaking behavioral change involving network
resources. Flexible-server creation also announces the deprecation of
`--cluster-option`; treat both interfaces as transitional in automation.

### Capability-gated PostgreSQL 17 upgrades (2.72.0)

`az postgres flexible-server upgrade --version` now checks the server
capability API and permits PostgreSQL 17 when that capability is available.

### PostgreSQL 11 and 12 end-of-life handling (2.75.0)

`az postgres flexible-server create` extends its end-of-life handling to
PostgreSQL 11 and 12, so provisioning should not rely on creating either
version.

### PostgreSQL authentication during creation (2.71.0)

`az postgres flexible-server create` can add an administrator while
`--active-directory-auth` is enabled. When `--password-auth` is disabled, the
command no longer generates an otherwise unusable password.

### PostgreSQL autonomous tuning and version 18 upgrades (2.82.0)

The `az postgres flexible-server index-tuning` group is deprecated and
redirects to `az postgres flexible-server autonomous-tuning`. Use its
`list-index-recommendations` and `list-table-recommendations` commands;
`az postgres flexible-server upgrade` also supports PostgreSQL 18.

### PostgreSQL cluster, list, and replica arguments (2.82.0)

Elastic-cluster creation has a database-name field that defaults to `None`.
The `backup`, `db`, `firewall-rule`, `identity`, `long-term-retention`,
`microsoft-entra-admin`, `migration`, `parameter`, and `replica` list commands
accept `--ids`; `replica create --name` can choose the read-replica name.

### PostgreSQL command and creation removals (2.80.0)

The Single Server groups `az postgres server`, `az postgres db`, and
`az postgres server-logs` are removed. Flexible-server creation no longer has
a default for `--version` and drops `--create-default-database` and
`--database-name`.

### PostgreSQL command and version removals (2.73.0)

`az postgres flexible-server stop-replication` is removed; use
`az postgres flexible-server replica promote`. Flexible-server create and
upgrade also no longer support PostgreSQL 12.

### PostgreSQL disk-tier restriction and legacy HA updates (2.77.0)

Premium SSD v2 can no longer be used with the Burstable compute tier by
`az postgres flexible-server create`, `update`, or `restore`. For existing
PostgreSQL 11 and 12 servers, `az postgres flexible-server update` now
bypasses Fabric mirroring validation so that high-availability status can be
changed.

### PostgreSQL elastic-cluster replicas (2.76.0)

`az postgres flexible-server replica create` and `promote` now support elastic
clusters.

### PostgreSQL flexible-server argument changes (2.87.0)

Flexible-server create/update removes `--high-availability`; use
`--zonal-resiliency` instead. Upgrade no longer constrains `--version` with a
CLI enum, and backup creation no longer requires a backup name because one is
generated automatically.

The `backup`, `db`, `firewall-rule`, `migration`, and `replica` create
commands now consistently use `--name` and `--server-name`; update scripts
whose old parameter names differ.

### PostgreSQL flexible-server creation defaults (2.73.0)

Creation now defaults `--create-default-database` to Disabled and the
PostgreSQL version to 17. The default SKU is selected from the location
capability API, so scripts needing stable choices should pass these values
explicitly.

### PostgreSQL flexible-server elastic clusters (2.68.0)

Create an elastic cluster with `--cluster-option ElasticCluster`, include
elastic clusters in list results with `--show-cluster`, and scale one with
the update command's `--node-count`. The flexible-server `identity` and
`fabric-mirroring` command groups also support system-assigned managed
identity and database mirroring to Fabric.

### PostgreSQL HA storage and mirroring (2.82.0)

For PostgreSQL 17 or later, an HA-enabled flexible server may now start Fabric
mirroring, reversing the earlier HA restriction. Flexible-server create and
update also expose zonal resiliency for HA and allow HA with `PremiumV2_LRS`
storage.

### PostgreSQL index-tuning options (2.70.0)

`az postgres flexible-server index-tuning` gains operations for tuning
options.

### PostgreSQL long-term-retention removal (2.85.0)

The `az postgres flexible-server long-term-retention` command group now
announces its upcoming removal; avoid introducing new automation that
depends on it.

### PostgreSQL multi-tenant identity and maintenance events (2.88.0)

Flexible-server create, restore, geo-restore, and replica create accept
`--federated-client-id` and `--backup-federated-client-id` for multi-tenant
application registration. The new `az postgresql flexible-server
maintenance-event` list, show, apply-now, and reschedule commands manage
maintenance events.

### PostgreSQL network-mode migration (2.84.0)

The new `az postgres flexible-server migrate-network` command migrates a
flexible server's network mode.

### PostgreSQL Premium SSDv2 behavior (2.86.0)

Read-replica creation accepts `--storage-type PremiumV2_LRS`. Increasing the
storage size of a Premium SSDv2 server no longer requires a restart, while
create and upgrade now reject SSDv2 for PostgreSQL versions earlier than 14.

### PostgreSQL restore time and HA mirroring restriction (2.69.0)

`az postgres flexible-server geo-restore` gains `--restore-time`. Fabric
mirroring start/stop/update-databases operations are disabled for HA servers.

### PostgreSQL SSDV2 replica and geo-restore support (2.83.0)

PostgreSQL flexible-server create, georestore, and replica operations now
allow SSDV2 servers to create replicas and perform geo-restores.

### PostgreSQL update prompts and public access (2.73.0)

Some flexible-server update operations now ask for user confirmation, which
changes unattended command behavior. Creation now disables public network
access when its public-access argument is `None`.

### Validation-only PostgreSQL upgrades (2.89.0)

`az postgres flexible-server upgrade` accepts `--validate-only` for PVC,
allowing validation without applying the upgrade.
