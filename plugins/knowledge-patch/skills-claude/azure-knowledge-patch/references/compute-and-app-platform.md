# Compute and application platform

## Virtual machines and scale sets

### Output and argument compatibility

- `2.68.0` changes `az disk` and `az snapshot` output to align with the service;
  retest JSON/table parsers.
- `2.69.0` gallery-application output uses case-sensitive `supportedOSType`,
  not `supportedOsType`; `az vm list-sizes` removes unused `--ids`.
- `2.71.0` deprecates `az vm list-sizes` and the image list pagination flags
  `--marker` and `--show-next-marker`; later image lists use continuation-token
  pagination.
- `2.75.0` VMSS create/update removes
  `--scheduled-event-additional-publishing-target-event-grid-and-resource-graph`.

### Disk encryption, security, and agents

- `2.68.0` VM create and `vm encryption enable` accept
  `--encryption-identity`; `2.69.0` adds it to VMSS create and encryption
  enable. Confidential VM creation automatically installs guest attestation.
- `2.71.0` VM/VMSS create/update accept explicit `--security-type Standard`.
  From `2.72.0`, the CLI injects Standard only when explicitly supplied.
- `2.72.0` VM/VMSS create/update add WireServer and IMDS modes with their
  access-control-profile reference IDs, plus `--key-incarnation-id`.
- `2.77.0` disk create/grant-access support Confidential VM OS disks.
- `2.78.0` disk create/update add `--supported-security-option` and
  `--action-on-disk-delay`.
- `2.80.0` VM/VMSS create/update add `--add-proxy-agent-extension` to control
  implicit ProxyAgent installation.
- `2.87.0` VM/VMSS creation supports fully cached ephemeral OS disks with
  `--ephemeral-os-disk-enable-full-caching`.

### Scheduled events and resilience

- `2.68.0` VM create/update add `--additional-scheduled-events`,
  `--enable-user-reboot-scheduled-events`, and
  `--enable-user-redeploy-scheduled-events`.
- `2.70.0` availability-set create/update adds the same policy controls.
- `2.79.0` availability-set update adds `--enable-all-instance-down` and
  `--scheduled-events-api-version`.
- `2.88.0` VM/VMSS create/update/show expose both profile options;
  availability-set create/show now do too.
- `2.76.0` VMSS create supports `--enable-automatic-repairs`.
- `2.82.0` VMSS `list-instances --resiliency-view` and
  `get-resiliency-view` expose per-instance resiliency.

### Zone placement and balancing

- `2.69.0` VMSS create/update add `--zone-balance`; scale supports edge zones.
- `2.72.0` VM create adds `--zone-placement-policy`, `--include-zones`, and
  `--exclude-zones`; VM create/update can align regional disks to the VM zone.
- `2.73.0` VMSS create/update add automatic zone balancing strategy/behavior
  and `--skuprofile-rank` list ordering for instance-mix VM sizes.
- `2.85.0` VMSS create `--zone-placement-policy Auto` adds include/exclude/max
  zone constraints; update gets max-zone count. Create/update add per-zone
  instance percentage policy and maximum value.
- `2.88.0` VMSS update receives zone-placement policy and include/exclude zones.

### Sizing, movement, and applications

- `2.68.0` VMSS security posture exclusion is now a string list, and
  create/update add `--security-posture-reference-is-overridable`.
- `2.73.0` VM and VMSS creation now supply the auxiliary tokens that were
  previously missing.
- `2.81.0` VM and VMSS `application set --enable-automatic-upgrade` enables
  automatic application upgrades.
- `2.84.0` VM create accepts `--data-disk-mbps` and `--data-disk-iops`.
- `2.87.0` VM/VMSS creation defaults to `Standard_D2s_v5` instead of
  `Standard_DS1_v2`; pass `--size`/`--vm-sku`. VM create/update support zone
  movement, and `vm deallocate --force-deallocate` forces deallocation.

## Disks, snapshots, images, and migration

### Disk creation and restore

- `2.71.0` `az disk config update` changes disk size through PATCH.
- `2.76.0` `az vm disk attach` can implicitly create disks from snapshots or
  restore points and set their size/SKU.
- `2.77.0` snapshot create adds instant-access duration for Premium SSD v2 and
  Ultra Disk snapshots.
- `2.78.0` disk attach can name disks implicitly created from snapshots/disks
  or disk restore points.
- `2.85.0` restore-point collection create/update supports instant access, and
  restore-point create sets its duration.

### Shared Image Gallery

- `2.71.0` image-version create/update can block deletion before end of life.
- `2.72.0` image-version maps OS/data VHD storage-account arguments to
  `properties.storageProfile.*DiskImage.source.storageAccountId`; this breaks
  callers expecting the old property path.
- `2.73.0` shared/community image definition/version list replaces marker
  pagination with `--max-items` and `--next-token`.
- `2.76.0` new in-VM access-control-profile and profile-version groups manage
  image access from VMs.
- `2.86.0` gallery create/show supports managed identity, and
  `az sig identity` manages it after creation.

### Availability-set and spot migrations

`2.78.0` adds validation/start/cancel/conversion operations under
`az vm availability-set` plus `az vm migrate-to-vmss`. Since `2.76.0`, use
`az compute-recommender spot-placement-score`, not
`spot-placement-recommender`.

## App Service and Functions

### Plans, SKUs, operating systems, and scaling

- `2.72.0` App Service plan create supports Pv4 and Pmv4 families.
- `2.73.0` App Service Environment operations no longer support ASEv2;
  Function Flex plan update can change zone redundancy.
- `2.78.0` plan create/update add `--async-scaling-enabled`.
- `2.80.0` Function plan create supports zone redundancy on Elastic Premium.
- `2.82.0` `appservice list-locations --managed-instance-enabled` discovers
  managed-instance locations.
- `2.86.0` a Linux web-app plan defaults to `P0V3` when SKU is omitted and
  recognizes `PREMIUM0V3` for elastic scale.
- `2.88.0` plan create defaults to Linux unless `--hyper-v` is explicit; use
  `--is-linux false` for Windows.
- `2.89.0` managed-instance plans are stable and support Premium V3 `P0V3`,
  `P1-3V3`, and `P1-5MV3` SKUs.

### Deployment slots, containers, and deployment diagnostics

- `2.69.0` Function deployment-slot create adds `--https-only`; Linux
  `webapp list-runtimes` no longer emits JBoss `_byol` IDs.
- `2.70.0` adds Linux Web App `sitecontainers`; webapp up/deploy and zip-source
  deployment add `--enable-kudu-warmup`.
- `2.71.0` a new deployment slot inherits source-slot VNet integration.
- `2.76.0` webapp create adds `--domain-name-scope`; `sitecontainers convert`
  switches classic and sitecontainers configuration.
- `2.86.0` webapp up/deploy add `--enriched-errors`; sitecontainers conversion
  can convert Docker Compose multi-container apps.
- `2.89.0` `webapp troubleshoot status` reports the latest startup attempt.

### Runtime discovery and logging

- `2.84.0` access-restriction show always returns camelCase. Web App runtime
  discovery uses service data and includes formerly missing Java versions.
- `2.87.0` `webapp list-runtimes` now returns objects containing `os`,
  `runtime`, `version`, `config`, `support`, and `end_of_life`, not strings.
  Use `--runtime`/`--support`; `--linux` and `--show-runtime-details` are gone.
- `2.87.0` adds `az webapp log startup` list/show for Linux startup logs.

`2.84.0` Maps account create now supplies a default SKU. Pass `--sku`
explicitly when provisioning must not depend on that CLI default.

### Security, certificates, and routing

- `2.84.0` API version `2024-11-01` Web App configuration and Web/Function VNet
  integration use the site-level outbound VNet routing property.
- `2.84.0` webapp create/update add end-to-end encryption; creation adds minimum
  TLS version and cipher suite.
- `2.85.0` logicapp create and webapp up add domain-name scope; webapp update
  adds `--platform-release-channel`.
- `2.87.0` webapp create adds `--site-scoped-certs`; Function App
  update-strategy config can be set or shown.
- `2.88.0` Function SSL config supports site-scoped certificates for Flex
  Consumption, and flex migration supports Linux Consumption apps with certs.

### Function migration and discovery

`2.71.0` Flex Consumption location listing accepts `--details` and `--runtime`.
`2.77.0` adds the `az functionapp flex-migration` group for CV1-to-Flex
migration. `2.88.0` broadens it to Linux Consumption apps with certificates.
In `2.74.0`, Web App config set stops client-side worker-count validation.

## App Configuration

### Schema, filters, serialization, and snapshots

- `2.69.0` import/export and feature show/list understand the Microsoft feature-
  management schema. Set misspelled `AZURE_APPCONFIG_FM_COMPATIBILE` for old
  file compatibility. Restore/show/list/revision datetime inputs accept zones.
- `2.75.0` key-value export/import/list/delete, restore, and revision-list gain
  tag filters; import/export/restore add `--dry-run`.
- `2.76.0` store create/update sets revision retention; feature list/delete/set
  support tag filters.
- `2.77.0` key-value import can read an AKS ConfigMap.
- `2.78.0` export escapes keys only for properties files; set/import accept JSON
  comments.
- `2.87.0` `kv set-snapshot-reference` creates a snapshot-reference value, and
  list can resolve values from one.

### Authentication, SKU, telemetry, and perimeter

- `2.70.0` login auth mode supports custom token audiences.
- `2.72.0` store create/update supports Developer SKU.
- `2.83.0` commands accept `anonymous` auth mode.
- `2.85.0` store create/update can link Application Insights; feature set can
  enable feature-flag telemetry.
- `2.87.0` store create/update and the perimeter-configuration group support
  Network Security Perimeters.

## Batch, AI, HDInsight, and other application services

### Azure Batch removals and additions

In `2.69.0`, certificate create/list/show/delete, node reimage, and node remote-
desktop are removed. Pool create removes application licenses, certificate
references, OS family, and OS version; pool set/reset removes certificate
references.

The same release adds job-manager application packages and all-tasks-complete
to job create; job-schedule create also gains job metadata and manager-task
environment, while schedule set/reset adds maximum retry count and wall time.
Job disable, node reboot/scheduling-disable, and pool autoscale evaluation take
`--json-file`. Pool create adds start-task environment/max retries; pool reset
adds start-task resource files and target-node communication mode.

In `2.80.0`, pool create removes `--target-communication` and
`--resource-tags`; pool reset/set remove target communication.

### AI Foundry and Cognitive Services

- `2.78.0` Cognitive account create adds project-management permission;
  account update can change OpenAI and AIServices kinds both ways.
- `2.80.0` adds Cognitive account connection, project, project connection, and
  `az cognitiveservice agent` groups.
- `2.82.0` Cognitive agent create can create/deploy a hosted agent.
- `2.83.0` agent log show streams hosted-agent console logs; create/start add
  `--show-logs`, and start adds `--timeout`.
- `2.89.0` Cognitive account compute manages compute clusters.

### HDInsight, IoT, Redis, and ARO

- `2.70.0` IoT Hub update adds `--min-tls-version`.
- `2.73.0` ARO create uses a revised best-practice VM SKU selection; pin SKU
  if automation expects one.
- `2.77.0` IoT Hub device-stream commands move from core CLI to `azure-iot`.
- `2.79.0` HDInsight create supports Entra-enabled clusters and managed-
  identity WASB; credential show/update reads and changes cluster credentials.
- `2.69.0` Redis create/update adds `--zonal-allocation-policy`; Web App Redis
  Service Connector creation accepts system identity. `2.70.0` adds the same
  system-identity connection for Container Apps and Fabric SQL workspace/DB
  UUID selection for Web App connections.
- `2.71.0` Service Connector adds workload-specific
  `connection create neon-postgres` commands for Neon Postgres Serverless.
