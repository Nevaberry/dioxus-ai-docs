---
name: cloud-init-knowledge-patch
description: cloud-init
version: 26.1
license: MIT
metadata:
  author: Nevaberry
---


# cloud-init Knowledge Patch

Use this skill when changing cloud-init networking, datasource selection,
packaging, service integration, templating, distribution support, platform
detection, mounts, or reporting consumers. Start with the compatibility checks
below, then load the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [networking-and-datasources.md](references/networking-and-datasources.md) | Network v1 devices, route metrics, OpenStack bond names and identity, Azure controls, OpenNebula metadata, and cloud discovery |
| [packaging-runtime-and-services.md](references/packaging-runtime-and-services.md) | Installation layout, Meson, systemd overrides, Python support, Jinja sandboxing, mounts, modules, and distribution defaults |
| [platforms-and-reporting.md](references/platforms-and-reporting.md) | Tilaa, s390x LXD, Raspberry Pi behavior, finish-event duration, and boot-analysis status |

## How to apply this patch

- Check datasource identity before diagnosing metadata networking on non-x86
  Ec2, OpenStack, or AltCloud systems.
- Keep renderer capabilities separate from datasource detection. Successful
  network setup does not identify a cloud platform.
- Preserve metadata-supplied names, route metrics, domains, and routes while
  translating network configuration.
- Audit packaging, installed paths, and effective systemd units when moving an
  older downstream integration forward.
- Review custom Jinja templates under sandbox rules rather than assuming every
  previously accepted operation remains available.
- Check platform and distribution defaults before adding generic networking,
  mirror, module, or discovery workarounds.
- Preserve duration and integer exit status through reporting integrations so
  callers can consume direct results.

## Breaking changes and migration checks

### Non-x86 datasource identity is strict

Since 25.1.4, Ec2, OpenStack, and AltCloud systems without DMI do not fall back
to probing link-local metadata after networking. Cloud-init remains disabled
unless the datasource is identified through one of these mechanisms:

- DMI data
- A kernel `ds=` override
- `datasource_list` configuration

For OpenStack, a config drive can provide the needed identification. An image
that is intentionally tied to OpenStack can instead force the datasource in
`/etc/cloud/cloud.cfg.d/91_openstack.cfg`:

```yaml
datasource_list: [ OpenStack ]
```

Do not treat a reachable link-local metadata service as proof that cloud-init
will select the datasource on an affected system.

### Installed paths and the build backend changed

Packaged files install below `/usr/lib` rather than `/lib` since 25.1. Review
package manifests, absolute-path patches, service assembly, and image-copy
logic for assumptions about the old location.

Cloud-init uses Meson rather than setuptools or distutils since 25.3. When
updating downstream packaging:

1. Replace the old build invocation.
2. Inspect the Meson-produced installation layout.
3. Reconcile package file lists with the actual output.
4. Account for Meson support when maintaining a BSD build.

### Custom systemd commands need review

The socket protocol used by cloud-init's systemd units changed in 25.3 to work
with alternatives such as `ncat -U`. Any downstream unit that overrides
`ExecStart=` must update its command for that protocol. Compare every
downstream override with the current packaged command before deployment.

### Jinja rendering is sandboxed

Cloud-init renders Jinja templates in a sandbox. Audit custom templates and
replace operations rejected by the sandbox; a template working under the old
renderer is not sufficient compatibility evidence.

### Azure missing custom data is a failure

The Azure datasource reports missing custom data as a provisioning failure
instead of silently continuing. Provisioning automation must surface and
handle this failure path.

## Networking quick reference

### Network v1 devices and router advertisements

Network v1 renders bonds, bridges, and VLANs. `network-config` can also express
`allow_accept_ra` for those device types. Preserve the setting when translating
or generating Network v1 data.

### NetworkManager route metrics

The NetworkManager renderer carries route-metric settings into generated
connection profiles. Keep configured metrics intact when competing routes rely
on them for preference; renderer-specific metric workarounds are no longer
needed.

### OpenStack bond names

OpenStack bond names come directly from `network_data.json`. Do not replace
them with synthetic sequential names such as `bond0` or `bond1`, and do not
write tests that assume a `bondN` sequence.

### OpenNebula metadata

OpenNebula accepts a global `SEARCH_DOMAIN` for all interfaces and
`ETHx_ROUTES` values for per-interface static routes. Carry both forms through
metadata parsing and network rendering.

## Datasource controls and discovery

### Azure controls

Azure provides `apply_network_config_set_name` to disable application of
network-config `set-name` directives. It also provides the experimental
`skip_ready_report` option to suppress the ready report. Treat renaming and
ready reporting as separate controls.

### Scaleway location metadata

The Scaleway datasource exposes region and availability zone. It no longer
handles private-IP metadata, so consumers must not depend on that datasource
for the removed field.

### CloudStack and Oracle discovery

CloudStack can obtain virtual-router information from NetworkManager leases.
Oracle dracut images can detect an iSCSI root through iBFT. Check these built-in
paths before retaining local discovery workarounds.

## Runtime and distribution quick reference

### Python and module support

Python 3.8 is unsupported for current builds. Amazon Linux supports the
`yum_add_repo` and `ca_certs` cloud-config modules, and Rocky Linux supports
`ca_certs`. The `cc_rh_subscription` module no longer handles openEuler.

### Distribution behavior and defaults

- RHEL preserves local changes in
  `disable-sshd-keygen-if-cloud-init-active.conf`; packaging must not restore
  the older overwrite behavior.
- Azure Linux 4.0 is supported.
- Alpine uses its CDN as the default APK mirror.
- Debian uses updated backports suite selection for Bullseye.

### Mount paths

The `mounts` module escapes special characters in mount paths when writing
`fstab`. Preserve the escaped output rather than reintroducing raw paths in a
downstream rewrite.

## Platforms and reporting quick reference

### Platform detection and Raspberry Pi defaults

Cloud-init detects Tilaa and s390x LXD environments. Raspberry Pi support
includes keymap handling, USB-gadget handling, and a systemd network service
template. On Raspberry Pi it also disables fallback network configuration and
removes APT mirror configuration.

Check those built-in behaviors before adding generic detection, fallback
networking, or mirror configuration.

### Reporting consumers

Reporting finish events include their duration, so consumers can obtain stage
timing directly from the event. Retain the duration during parsing, storage,
and export.

`analyze_boot` returns an integer exit code. Callers should handle it as a
conventional process status instead of treating the result as an untyped or
non-status value.

## Review checklist

- Is a non-x86 Ec2, OpenStack, or AltCloud datasource explicitly identifiable?
- Does OpenStack preserve bond names from `network_data.json`?
- Does Network v1 retain bonds, bridges, VLANs, and `allow_accept_ra`?
- Do NetworkManager profiles retain configured route metrics?
- Are Azure renaming, ready reporting, and missing-custom-data failure handled?
- Are OpenNebula `SEARCH_DOMAIN` and `ETHx_ROUTES` values preserved?
- Do packages use `/usr/lib`, Meson, and a supported Python runtime?
- Do effective systemd `ExecStart=` commands use the changed socket protocol?
- Have custom Jinja templates been checked under sandbox restrictions?
- Do distribution module gates and defaults match the target system?
- Are special characters in `fstab` mount paths left escaped?
- Do Raspberry Pi images respect platform networking and APT defaults?
- Do reporting consumers retain finish-event duration and boot-analysis status?
