# Data, storage, and Key Vault

## PostgreSQL Flexible Server

### Version and command lifecycle

- `2.72.0` capability-gates upgrades to PostgreSQL 17.
- `2.73.0` creation defaults to PostgreSQL 17 and disables default-database
  creation; its SKU comes from location capabilities. Explicitly set version,
  SKU, and database choice. `stop-replication` is removed in favor of
  `replica promote`; create/upgrade no longer support PostgreSQL 12.
- `2.75.0` extends end-of-life handling to PostgreSQL 11 and 12; do not depend
  on provisioning them.
- `2.80.0` removes Single Server `az postgres server`, `db`, and `server-logs`.
  Flexible-server create no longer defaults `--version` and removes
  `--create-default-database`/`--database-name`.
- `2.82.0` deprecates `index-tuning` in favor of `autonomous-tuning`, including
  list-index and list-table recommendations, and adds PostgreSQL 18 upgrades.
- `2.85.0` announces removal of `long-term-retention`; avoid new automation.
- `2.86.0` announces network-resource behavior changes for create, replica,
  restore, geo-restore, and revive-dropped, and deprecates `--cluster-option`.
- `2.87.0` upgrade stops constraining version through a CLI enum.

### Creation, networking, and HA

- `2.68.0` create supports elastic clusters with
  `--cluster-option ElasticCluster`; list adds `--show-cluster`, update adds
  `--node-count`, and the identity/Fabric-mirroring groups support system
  identity and database mirroring.
- `2.69.0` geo-restore adds `--restore-time`; Fabric mirroring operations are
  disabled for HA servers at this point in the CLI history.
- `2.71.0` create can add an administrator with Entra auth enabled and no
  longer creates an unusable password when password auth is disabled.
- `2.73.0` public access is disabled when the public-access argument is `None`;
  some update operations now prompt, affecting unattended scripts.
- `2.77.0` disallows Premium SSD v2 with Burstable tier for create/update/
  restore. It bypasses Fabric-mirroring validation on existing PostgreSQL 11/12
  servers when changing HA status.
- `2.82.0` allows PostgreSQL 17+ HA servers to start Fabric mirroring, reversing
  the earlier restriction; create/update expose zonal resiliency and allow HA
  with `PremiumV2_LRS`.
- `2.83.0` SSDV2 servers can create replicas and use geo-restore.
- `2.84.0` adds `az postgres flexible-server migrate-network`.
- `2.86.0` replica create accepts `PremiumV2_LRS`; SSDv2 size increases no
  longer restart the server, and create/upgrade reject SSDv2 before version 14.
- `2.87.0` removes create/update `--high-availability`; use
  `--zonal-resiliency`.

### Replicas, clusters, backup, and maintenance

- `2.70.0` adds index-tuning option operations (later redirected to autonomous
  tuning).
- `2.76.0` replica create/promote supports elastic clusters.
- `2.82.0` elastic-cluster database name defaults to `None`. Backup, DB,
  firewall-rule, identity, LTR, Entra admin, migration, parameter, and replica
  list accept `--ids`; replica create `--name` selects the replica name.
- `2.87.0` backup create auto-generates its name. Backup, DB, firewall-rule,
  migration, and replica create now consistently use `--name` and
  `--server-name`; update scripts using older parameter names.
- `2.88.0` create/restore/geo-restore/replica create add federated and backup-
  federated client IDs for multi-tenant registration. The CLI spelling is
  `az postgresql flexible-server maintenance-event`; it supports list, show,
  apply-now, and reschedule.
- `2.89.0` upgrade `--validate-only` performs PVC without applying the upgrade.

## MySQL Flexible Server

### Defaults and storage controls

- `2.68.0` create, restore, replica create, and geo-restore accept
  `--storage-redundancy` for zone-redundant HA storage.
- `2.71.0` changes create defaults for `--auto-scale-iops` and `--version`;
  always pass both for reproducible provisioning.
- `2.72.0` create adds `--backup-interval`; restore adds `--faster-restore`, and
  replica create adds `--faster-provisioning` for automatic IOPS scaling.
- `2.74.0` BC SKU creation defaults storage redundancy to local; pass it when
  another redundancy is required.
- `2.76.0` create/update expose revised storage redundancy and backup interval,
  so update can now change backup interval.
- `2.87.0` backup create, restore, geo-restore, and replica operations remove
  `--storage-redundancy`; remove it from current scripts.

### Versions, logs, backup, mirroring, and maintenance

- `2.77.0` supports upgrade to MySQL 8.4.
- `2.78.0` create/update support Accelerated Logs for GeneralPurpose.
- `2.82.0` backup delete removes an on-demand backup.
- `2.83.0` restore, geo-restore, and replica create can target another
  subscription.
- `2.89.0` mirroring enable/disable controls Fabric Mirroring. Update adds
  `--maintenance-batch Default|Batch1|Batch2`; omission preserves the current
  batch.

```bash
az mysql flexible-server update --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER" --maintenance-batch Batch1
```

## Azure SQL and Database Migration Service

### Database, failover, retention, and recovery

- `2.75.0` SQL DB replica create accepts a partner subscription ID for cross-
  subscription geo-replication.
- `2.76.0` `sql ltr-policy set` removes unused `--access-tier`; failover-group
  create supports multiple partner groups.
- `2.78.0` `sql db ltr-backup` adds LTR immutability commands.
- `2.79.0` serverless-to-provisioned DB update preserves the chosen service-
  level objective.
- `2.82.0` SQL Managed Instance create/update can set memory GB.
- `2.84.0` server/database operations support versionless TDE keys. SQL server
  create/update add soft-delete retention; deleted-server show/list inspect
  deleted servers and server restore recovers one.
- The old SQL control-plane API retirement and non-equivalent operation groups
  are detailed in the deployment/governance reference.

In `2.80.0`, DMS project create no longer requires location.

## Cosmos DB

- `2.68.0` account create/update add `--enable-prpp-autoscale` for burst
  capacity.
- `2.70.0` `az cosmosdb offline-region` takes an account region offline.
- `2.74.0` SQL containers support Full Text Policy.
- `2.76.0` restore removes timeout-prone CLI-side validation and sends the
  restore request directly.
- `2.82.0` adds the `az cosmosdb fleet` group; account create/update can
  disable local auth.
- `2.84.0` network ACL bypass resource IDs accept Microsoft Fabric workspaces.

## Azure Storage accounts and SAS

### Account security, networking, and lifecycle

- `2.75.0` account create/update add `--sas-expiration-action`.
- `2.78.0` account create/update add `--enable-smb-oauth`, zones, and
  zone-placement policy. Object-replication policy create/update adds metrics.
- `2.79.0` the network-security-perimeter-configuration group supports list,
  show, and reconcile. Account create/update add blob Geo SLA priority;
  object-replication policy adds priority replication.
- `2.80.0` account failover accepts `--failover-type Unplanned`.
- `2.83.0` file-service properties add required SMB/NFS encryption-in-transit
  switches; account create/update add IPv6 endpoint publication, network-rule
  add/remove add IPv6 addresses, and TLS 1.0/1.1 input is coerced to TLS 1.2.
- `2.87.0` account create/update accept Smart access tier and allowed copy
  scope. Blob-service properties can configure static website enablement,
  index/default-index path, and 404 document; object replication adds tag
  replication.

### User-delegation SAS

`2.82.0` blob/container/filesystem/filesystem-file/filesystem-directory SAS
commands add `--user-delegation-oid` (filesystem file is new); share/file/queue
also add it with `--as-user`. `2.86.0` extends blob, container, share, file,
queue, and filesystem SAS with `--user-delegation-tid` for another tenant.

### Output and migration prompts

`2.73.0` storage-account redundancy migration now prompts before starting.
`2.75.0` consumption usage represents missing values as JSON null rather than
the string `None`; fixed parsers must change.

## Azure Files and NFS

### Provisioned file shares

`2.70.0` adds account SKUs `StandardV2_LRS`, `StandardV2_ZRS`,
`PremiumV2_LRS`, and `PremiumV2_ZRS` plus file-service usage reporting. Share
create/update adds paid-bursting controls for provisioned v1 and provisioned
bandwidth/IOPS for v2.

### NFS, links, OAuth, and listing

- `2.71.0` share/directory/file commands support NFS; hard-link create manages
  NFS hard links. Share create adds snapshot virtual-directory access.
- `2.75.0` file upload-batch/download-batch support OAuth.
- `2.78.0` the CLI command is spelled `az storage file symoblic-link`; its
  create/show operations manage NFS symlinks.
- `2.79.0` file list supports NFS, but `--include` does not.
- `2.80.0` file list returns additional information without an explicit
  protocol.
- `2.83.0` file list with OAuth works without Reader access.

### Azure Backup for Files

- `2.69.0` Backup supports Azure Files Vault Standard policies.
- `2.77.0` Azure Files share restore works after source-account deletion when
  the source resource ID is supplied.

## Azure NetApp Files

### Encryption, throughput, and data protection

- `2.70.0` account `change-key-vault` changes the Key Vault/Managed HSM used by
  volumes. `get-key-vault-status` feeds `transitiontocmk`, which transitions
  VNet volumes but fails when the target shares an encryption sibling set with
  another account. Volume create/update adds cool-access tiering policy.
- `2.73.0` account create/update adds federated client ID for cross-tenant CMK
  and NFSv4 ID domain; volume-group create no longer requires a proximity
  placement group.
- `2.74.0` volume-group create supports Oracle.
- `2.78.0` volume splitclonefromparent splits clones; create can grow the pool
  during clone split. Pools/volumes accept Flexible service level and pool
  create adds custom throughput.
- `2.81.0` volume-group create adds network features; volume replication list
  can exclude deleted replications.
- `2.85.0` volume create/update adds desired ransomware-protection state;
  ransomware-report and list-quota-report expose reports.
- `2.87.0` volume create defaults network features to Standard; update remote-
  volume-resource-ID is deprecated. New cache and volume-bucket groups manage
  those resources.
- `2.89.0` volume create adds `--breakthrough-mode`.

### Interface removals

`2.80.0` NetApp volume create/update removes read-only `--endpoint-type`.
`2.88.0` deprecates the subvolume group and volume
`--enable-subvolumes`; both are announced for removal.

## Azure Backup and recovery

- `2.70.0` restore-disks accepts `--target-zone NoZone`.
- `2.73.0` VM protection supports trusted VMs with Standard policy.
- `2.74.0` Backup container/item/policy/protection supports ASE and Backup adds
  HANA Snapshot.
- `2.76.0` restore-disks `--cvm-os-des-id` selects the DES for a restored
  confidential VM OS disk.
- `2.78.0` protection reconfigure moves protection to another vault.
- `2.79.0` deleted-vault list/undelete recovers deleted Backup vaults.
- `2.89.0` Azure Backup CLI operations support cost-management settings.

## Key Vault and Managed HSM

### Key operations and network rules

- `2.68.0` key sign/verify accept base64 in `--digest`.
- `2.69.0` Key Vault/HSM update with default action Deny preserves an explicit
  `--bypass` rather than replacing it with the default.
- `2.71.0` Managed HSM creation supports the C SKU family.
- `2.78.0` HSM creation can set IP rules; network-rule add/remove/list/wait
  supports HSM.
- `2.82.0` key create/import add `--default-data-disk-policy` for default SKR.
- `2.87.0` Application Gateway cert use with Managed HSM is described in the
  networking reference.
- `2.88.0` key show/list adds AES key size. Preview `ekm-connection` manages
  External Key Manager connections; key create `--external-key-id` creates an
  EKM-backed HSM key.

### Control-plane lifecycle (`key-vault-api-and-access-control`)

Stable `2026-02-01` and preview `2026-03-01-preview` exist in public Azure,
21Vianet, and Government; production should use stable. Versions before
`2026-02-01` retire February 27, 2027. Preview versions other than
`2026-04-01-preview` are deprecated on 90 days' notice. Data-plane APIs are
unaffected.

Management SDK floors include .NET `Azure.ResourceManager.KeyVault` 1.4.0,
Go `armkeyvault/v2`, and current JavaScript/Python/Java ARM Key Vault clients.
Cloud Shell uses the latest API, so its scripts must already be compatible.

### RBAC default and access-policy opt-out

For vault creation with API `2026-02-01` or later, omitted
`enableRbacAuthorization` means true. Updates do not change an existing model,
and an existing null still means access policies. To retain access policies on
new creation, explicitly set false:

```bash
az keyvault create --name "$vault_name" --resource-group "$resource_group" \
  --enable-rbac-authorization false
```

Changing the property needs `Microsoft.KeyVault/vaults/write`; the portal also
needs `Microsoft.Authorization/roleAssignments/write` to grant roles and avoid
lockout. Enforced per-vault private-endpoint limits require excess endpoints
to be removed or a support exception.
