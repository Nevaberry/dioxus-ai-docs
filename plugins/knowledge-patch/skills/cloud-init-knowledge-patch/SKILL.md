---
name: cloud-init-knowledge-patch
description: cloud-init
version: "26.1"
license: MIT
metadata:
  author: Nevaberry
---

# cloud-init Knowledge Patch

Use this skill when changing cloud-init networking, datasource detection,
packaging, service integration, distribution support, platform detection, or
reporting consumers. Start with the compatibility checks below, then load the
topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [networking-and-datasources.md](references/networking-and-datasources.md) | Network v1 devices, router advertisements, OpenStack bond names and datasource identity, Scaleway metadata |
| [packaging-runtime-and-services.md](references/packaging-runtime-and-services.md) | Installation layout, Meson migration, systemd unit overrides, Python and distribution support |
| [platforms-and-reporting.md](references/platforms-and-reporting.md) | Tilaa, s390x LXD, Raspberry Pi behavior, finish-event duration |

## How to apply this patch

- Check datasource identity before diagnosing a metadata-networking failure on
  non-x86 systems.
- Audit downstream packaging and custom systemd units when moving an older
  cloud-init integration forward.
- Treat network renderer capabilities separately from datasource detection;
  support for a device type does not identify the cloud platform.
- Check platform-specific defaults before adding generic fallback networking or
  APT mirror configuration to Raspberry Pi images.
- Update event consumers to read the reported finish-event duration when direct
  stage timing is useful.

## Breaking changes and migration checks

### Non-x86 datasource identity is strict

Since 25.1.4, Ec2, OpenStack, and AltCloud systems without DMI no longer fall
back to probing link-local metadata after networking. If the datasource is not
identified explicitly, cloud-init remains disabled.

Identification can come from one of these sources:

- DMI data
- A kernel `ds=` override
- `datasource_list` configuration

For OpenStack, a config drive can supply the needed identification. An image can
also force the datasource in `/etc/cloud/cloud.cfg.d/91_openstack.cfg`:

```yaml
datasource_list: [ OpenStack ]
```

Use that override only when the image is intentionally tied to OpenStack. Do not
expect successful network setup by itself to trigger the removed link-local
probe.

### Installed-file paths moved

Since 25.1, packaged files install under `/usr/lib` rather than `/lib`.

Review downstream assumptions in:

- package manifests
- file lists
- patches that use absolute installation paths
- service or image assembly logic that copies installed files

Do not retain `/lib` merely because an older package placed cloud-init files
there.

### The build backend is Meson

Since 25.3, cloud-init builds with Meson instead of setuptools/distutils.
Downstream packages need to be checked for build invocation and installed-layout
differences. Meson also supports BSD builds in the current patch.

When adapting packaging:

1. Remove assumptions that the setuptools/distutils entry point performs the
   build.
2. Recheck the generated installation paths instead of translating commands
   mechanically.
3. Verify downstream file manifests against the Meson result.
4. Include the BSD Meson support when maintaining BSD packaging.

### Custom systemd unit commands need review

The socket protocol used by cloud-init's systemd units changed in 25.3 so that
alternatives such as `ncat -U` can be used. A downstream unit that overrides
`ExecStart=` must update its command for the changed protocol.

Audit the effective unit, not only the vendor file:

```sh
systemctl cat cloud-init.service
```

If a drop-in or replacement unit supplies `ExecStart=`, compare that command
with the current packaged unit before deployment.

### Runtime and distribution support changed

Python 3.8 is no longer supported. Do not select it as the interpreter for a
current cloud-init build or package.

Distribution-specific behavior also changed:

| Area | Current behavior |
| --- | --- |
| Rocky Linux | The `ca_certs` module is supported. |
| openEuler | `cc_rh_subscription` no longer handles this distribution. |
| RHEL | cloud-init no longer overwrites local changes in `disable-sshd-keygen-if-cloud-init-active.conf`. |

Preserve an administrator's RHEL changes to that file; do not add packaging
logic that restores the older overwrite behavior.

## Networking quick reference

### Network v1 device support

Network v1 can render all of these device types:

- bonds
- bridges
- VLANs

`network-config` can also express `allow_accept_ra` for those device types.
Keep that setting when translating or generating network v1 data; do not discard
it on the assumption that it is limited to another network schema or device
class.

### OpenStack bond names are supplied by metadata

OpenStack bond names now come directly from `network_data.json`. Do not replace
them with synthetic sequential names such as `bond0`, `bond1`, and so on.

This affects any downstream logic that:

- predicts bond names before reading metadata
- rewrites rendered bond names
- hard-codes sequential bond identifiers in tests
- maps other device configuration to a presumed `bondN` name

Use the name supplied in the OpenStack network data as the stable input to later
rendering steps.

## Datasource metadata quick reference

### Scaleway

The Scaleway datasource exposes:

- region
- availability zone

It no longer handles private-IP metadata. Consumers should use the exposed
location fields and must not depend on this datasource to populate the removed
private-IP metadata.

### OpenStack identity triage

When an affected non-x86 OpenStack instance stays disabled, check in this
order:

1. Whether usable DMI identity exists.
2. Whether the kernel command line supplies a `ds=` override.
3. Whether `datasource_list` selects OpenStack.
4. Whether an OpenStack config drive is available.

Do not use a later link-local metadata response as proof that cloud-init should
have selected the datasource; that fallback is no longer performed in this
case.

## Platform quick reference

### Newly detected environments

Cloud-init detects the Tilaa cloud platform and s390x LXD environments. Avoid
carrying local detection workarounds forward without first checking whether the
built-in detection now covers the target.

### Raspberry Pi behavior

Raspberry Pi support includes:

- keymap handling
- USB-gadget handling
- a systemd network service template

For this platform, cloud-init also disables fallback network configuration and
removes APT mirror configuration. Account for those defaults when building an
image or investigating why generic fallback networking or mirror configuration
was not emitted.

## Reporting quick reference

Reporting finish events include their duration. Event consumers can obtain
stage timing directly from the finish event instead of reconstructing it from
separate timestamps.

When changing a reporting integration, retain the duration field through
parsing, storage, and export so downstream observers can use it.

## Review checklist

- Is a non-x86 Ec2, OpenStack, or AltCloud datasource explicitly identifiable?
- Does OpenStack configuration preserve bond names from `network_data.json`?
- Does network v1 generation retain bonds, bridges, VLANs, and
  `allow_accept_ra` where configured?
- Do package manifests use `/usr/lib` and the Meson-produced layout?
- Do custom systemd `ExecStart=` commands follow the changed socket protocol?
- Does the runtime avoid Python 3.8?
- Do distribution conditionals match Rocky Linux, openEuler, and RHEL behavior?
- Do Raspberry Pi images respect the platform's networking and APT defaults?
- Do Scaleway consumers avoid the removed private-IP metadata?
- Do reporting consumers preserve finish-event duration?
