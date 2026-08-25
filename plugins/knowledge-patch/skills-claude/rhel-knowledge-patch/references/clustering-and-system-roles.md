# Clustering and System Roles

Consult this reference for pcs and Pacemaker behavior, fencing and resource agents, cluster migration, role exports, and cross-platform RHEL system-role interfaces.

## Contents

- [pcs, Pacemaker, fencing, and resource agents](#pcs-pacemaker-fencing-and-resource-agents)
- [High-availability role exports](#high-availability-role-exports)
- [Cross-platform system roles](#cross-platform-system-roles)

## pcs, Pacemaker, fencing, and resource agents

### `pcs` automation and safety interfaces (10.0)

Use `--yes` rather than `--force` to confirm destructive actions, and opt into hard resource-agent validation errors with `--agent-validation`. `pcs status wait`, `pcs status query resource`, and `--output-format=json|cmd` for defaults, tags, and fencing provide machine-readable and replayable automation interfaces.

### Pacemaker remote and rule behavior (10.0)

Pacemaker Remote can use X.509 certificates via `PCMK_ca_file`, `PCMK_cert_file`, `PCMK_key_file`, and optional `PCMK_crl_file`; `PCMK_panic_action=off|sync-off` leaves a panicked node shut down. `clone-node-max > 1` now implies global uniqueness, invalid date/duration fields are removed, and `pcs booth ticket cleanup` removes stale Booth tickets from the CIB.

### Pacemaker 4 migration and removals (10.0)

The CIB upgrades to `pacemaker-4.0`, renames `crmd-*` timeout properties, converts legacy master resources and multi-rule locations, and changes concurrent fencing and clone uniqueness defaults. RKT bundles, Nagios/Upstart resource classes, legacy master/slave role names, multiple top-level location rules, and numerous `show|list` forms are removed in favor of `config` commands.

### Cluster resource-agent behavior (10.1)

`IPaddr2` now treats a down underlying link as failure and triggers failover by default; set `check_link_status=false` to restore the old behavior. `awsvip` adds an `interface` parameter, `fence_sbd` falls back to `SBD_DEVICE` when `devices` is omitted, `fence_nutanix` supports AHV, and the new `crypt` agent manages key-file or Clevis/Tang-unlocked encrypted volumes.

### Safer cluster administration (10.1)

`pcs` blocks removal of the last fencing mechanism unless explicitly overridden and automatically runs advanced CIB validation for `status`, `cluster edit`, and `cluster cib-push`. `pcs cluster rename NEW-NAME` renames a cluster, while alert, node-attribute, and utilization configuration can be emitted as `text`, `json`, or replayable `cmd` output.

### Cluster descriptions and validation (10.2)

`pcs cib element description`, `pcs resource description`, and `pcs stonith description` attach text to supported CIB objects. Resource and fencing meta-attribute names are now validated, and disabling `stonith-enabled` emits an unsafe-configuration warning.

### Native nftables cluster blocking (10.2)

The `portblock` resource agent uses nftables by default; set its `firewall` parameter to `iptables` only for legacy behavior. `pcs resource delete` now rejects running unmanaged resources, and offline `-f` deletions warn that live cleanup was skipped; use `--no-stop` rather than the deprecated `--force` meaning when intentionally leaving a resource running.


## High-availability role exports

### Complete `ha_cluster` role exports (10.1)

The `ha_cluster` role now exports primitive, group, clone, and bundle resource definitions plus repository, firewall, SELinux, cloud-agent, and pcsd permission settings. The result is suitable for recreating a cluster or bringing an existing cluster under role management.

### Cluster and storage system-role expansion (10.2)

`ha_cluster` exports location, colocation, order, and ticket constraints plus cluster properties and resource defaults. The storage role can add, remove, resize, and format partitions, and its snapshot requests accept `bootable` for snapm-backed bootable sets.


## Cross-platform system roles

### New cluster, storage, and security system roles (10.0)

New `sudo` and `aide` roles manage sudoers and AIDE, while `systemd_units_user` manages existing users' units. `ha_cluster` can export reusable Corosync configuration and configure ACLs, alerts, utilization and SBD/node options; `storage` adds Stratis pools and `grow_to_fill: true` for resizing LVM physical volumes.

### Podman, networking, and logging role interfaces (10.0)

The Podman role adds registry certificates, credential files, global/per-item credentials, TLS validation, and Pod Quadlets. The network role adds route `src`, `autoconnect_retries`, and `wait_ip=any|ipv4|ipv6|ipv4+ipv6`; logging adds custom configs/templates, `reopen_on_truncate`, and file/directory ownership and modes.

### Logging, metrics, and bootloader system-role interfaces (10.1)

The journald role adds time-based `MaxRetention` handling and `journald_system_keep_free`, while the metrics role adds `metrics_optional_domains`, `metrics_into_spark`, and `metrics_from_spark`. Bootloader kernel entries can mark exactly one kernel `default`, which the role applies with `grubby --set-default`.

### AD, firewall, and Podman system-role interfaces (10.1)

The AD role adds `ad_integration_sssd_realm_preserve_case`, `ad_integration_sssd_remove_duplicate_sections`, and `ad_integration_manage_packages` (default `true`). The firewall role can compose a custom service from existing services, and the Podman role can opt into a full TOML renderer with `podman_use_new_toml_formatter: true`.

### Storage and bootloader role behavior (10.1)

The storage role accepts encrypted or partitioned PVs directly in LVM RAID and can use an `encryption_key` file path. The bootloader role rejects YAML boolean and null values, so values such as `on`, `off`, `yes`, and `no` must be quoted when strings are intended.

### Network and security system-role expansion (10.2)

The firewall role accepts IPv6 `ipset_entries` and `ipset_options`, but one set cannot mix IPv4, IPv6, and MAC entries; it can also resolve PCI interface IDs by ensuring NetworkManager is installed. The metrics role adds Grafana TLS certificate variables, and the SELinux role can label DCCP and SCTP ports.

### Immutable management and upgrade roles (10.2)

RHEL system roles can manage ostree-based immutable hosts except through `nbde_client`. New `analysis`, `remediate`, and `upgrade` Ansible roles automate the phases of large RHEL 9-to-10 upgrades.

