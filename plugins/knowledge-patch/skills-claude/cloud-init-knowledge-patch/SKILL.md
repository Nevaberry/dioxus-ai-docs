---
name: cloud-init-knowledge-patch
description: cloud-init
version: 26.1
license: MIT
metadata:
  author: Nevaberry
---


# cloud-init Knowledge Patch

Use this skill when changing cloud-init networking, datasource detection,
packaging, service integration, distribution support, templating, platform
detection, or reporting consumers. Start with the compatibility checks below,
then load the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [networking-and-datasources.md](references/networking-and-datasources.md) | Network v1 devices, route metrics, OpenStack bond names and identity, Azure controls, OpenNebula, Scaleway |
| [packaging-runtime-and-services.md](references/packaging-runtime-and-services.md) | Installation layout, Meson migration, systemd overrides, Python support, Jinja, mounts, boot analysis |
| [platforms-and-reporting.md](references/platforms-and-reporting.md) | Distribution modules and defaults, platform detection, Raspberry Pi, CloudStack, Oracle, finish-event duration |

## How to apply this patch

- Establish the datasource identity before debugging metadata networking on a
  non-x86 system.
- Audit package manifests, custom systemd units, and runtime selection when
  moving an older downstream integration forward.
- Treat renderer features separately from datasource detection: support for a
  device or route setting does not establish the cloud platform.
- Test custom Jinja templates against the sandbox before shipping an image.
- Check platform-specific defaults before adding generic fallback networking,
  mirror configuration, or separate module bootstrapping.
- Keep reporting duration and conventional exit status intact for callers that
  consume cloud-init results programmatically.

## Breaking changes and migration checks

### Non-x86 datasource identity is strict

Since 25.1.4, Ec2, OpenStack, and AltCloud systems without DMI do not fall back
to probing link-local metadata after networking. Cloud-init remains disabled
unless one of these identifies the datasource:

- DMI data
- a kernel `ds=` override
- `datasource_list` configuration

For OpenStack, a config drive can provide identification. An image intentionally
tied to OpenStack can force it in
`/etc/cloud/cloud.cfg.d/91_openstack.cfg`:

```yaml
datasource_list: [ OpenStack ]
```

Do not interpret successful networking or a later metadata response as proof
that the removed fallback should select the datasource.

### Custom Jinja templates run in a sandbox

Cloud-init renders Jinja templates in a sandbox. Revise custom templates that
depend on operations the sandbox forbids, and exercise them during image tests
rather than assuming an unrestricted rendering environment.

### Missing Azure custom data is a failure

The Azure datasource reports missing custom data as a provisioning failure
instead of silently continuing. Automation must handle that result as a failed
provisioning path.

### Installed paths and the build backend changed

Packaged files install under `/usr/lib`, not `/lib`, and cloud-init builds with
Meson rather than setuptools or distutils. Recheck build invocation, generated
paths, downstream manifests, patches with absolute paths, and image assembly
logic. Meson also supports BSD builds.

### Custom systemd commands need review

The systemd-unit socket protocol changed for compatibility with alternatives
such as `ncat -U`. Inspect the effective unit:

```sh
systemctl cat cloud-init.service
```

If a drop-in or replacement supplies `ExecStart=`, compare its command with the
current packaged unit and update it before deployment.

### Python 3.8 is unsupported

Do not select Python 3.8 for a current cloud-init build or package. Check both
the package build environment and the interpreter used by installed services.

## Networking quick reference

### Preserve Network v1 device capabilities

Network v1 renders bonds, bridges, and VLANs. `network-config` can express
`allow_accept_ra` for each of those device types. Keep the setting when
translating or generating Network v1 data.

### Use OpenStack bond names from metadata

OpenStack bond names come directly from `network_data.json`. Do not replace
them with sequential names such as `bond0` or `bond1`, predict names before
reading metadata, or hard-code `bondN` expectations in tests.

### Keep route metrics in NetworkManager output

The NetworkManager renderer carries route-metric settings into generated
connection profiles. Express competing-route preference in the network
configuration; a renderer-specific workaround is no longer needed.

### Apply Azure controls deliberately

Azure provides `apply_network_config_set_name` to disable application of
network-config `set-name` directives. Its experimental `skip_ready_report`
option suppresses the ready report. Treat these as separate controls and make
the experimental status visible in image policy.

### Preserve OpenNebula route metadata

OpenNebula accepts global `SEARCH_DOMAIN` data for all interfaces and
per-interface static routes through `ETHx_ROUTES`. Keep the global and
interface scopes distinct when translating metadata.

## Datasource metadata quick reference

### Scaleway

The Scaleway datasource exposes region and availability-zone fields. It no
longer handles private-IP metadata, so consumers must not depend on it to
populate that value.

### OpenStack identity triage

When an affected non-x86 OpenStack instance stays disabled, check in this
order:

1. Whether usable DMI identity exists.
2. Whether the kernel command line supplies a `ds=` override.
3. Whether `datasource_list` selects OpenStack.
4. Whether an OpenStack config drive is available.

Do not use a later link-local metadata response as evidence that selection
should have happened.

## Runtime and module quick reference

### Amazon Linux modules

Amazon Linux supports `yum_add_repo` and `ca_certs`. Images can configure Yum
repositories and trusted CA certificates through cloud-init without separate
bootstrap logic.

### Mount paths with special characters

The `mounts` module escapes special characters in mount paths written to
`fstab`. Preserve the escaped result rather than post-processing it back into
an invalid entry.

### Analyze boot exit status

`analyze_boot` returns an integer exit code. Callers can consume it as a
conventional process status and should not assume the result is non-numeric.

## Platform quick reference

### Raspberry Pi defaults

Raspberry Pi support includes keymap handling, USB-gadget handling, and a
systemd network service template. On this platform cloud-init also disables
fallback network configuration and removes APT mirror configuration. Account
for those defaults before diagnosing absent generic output.

### Distribution behavior

Current distribution behavior includes:

| Area | Behavior |
| --- | --- |
| Rocky Linux | `ca_certs` is supported. |
| openEuler | `cc_rh_subscription` does not handle the distribution. |
| RHEL | Local changes to `disable-sshd-keygen-if-cloud-init-active.conf` are preserved. |
| Azure Linux 4.0 | The distribution is supported. |
| Alpine | The CDN is the default APK mirror. |
| Debian Bullseye | Backports suite selection uses the updated behavior. |

Do not add package logic that restores the older RHEL overwrite behavior or
generic mirror defaults that conflict with the platform behavior.

### Detection updates

Cloud-init detects Tilaa and s390x LXD environments. CloudStack can discover
virtual-router information from NetworkManager leases, and Oracle dracut images
can detect an iSCSI root through iBFT. Recheck built-in detection before
carrying local workarounds forward.

## Reporting quick reference

Reporting finish events include duration. Keep the field through parsing,
storage, and export so consumers can obtain stage timing directly rather than
reconstructing it from separate timestamps.

## Review checklist

- Is a non-x86 Ec2, OpenStack, or AltCloud datasource explicitly identified?
- Does OpenStack preserve bond names from `network_data.json`?
- Does Network v1 retain bonds, bridges, VLANs, and `allow_accept_ra`?
- Do NetworkManager profiles retain configured route metrics?
- Are Azure rename, ready-report, and custom-data behaviors handled separately?
- Are OpenNebula search-domain and per-interface route scopes preserved?
- Do package manifests use `/usr/lib` and the Meson-produced layout?
- Do effective custom systemd commands follow the current socket protocol?
- Does the runtime avoid Python 3.8?
- Do sandboxed templates and escaped mount paths pass image tests?
- Do distribution conditionals match current module support and defaults?
- Do Raspberry Pi images respect networking and APT behavior?
- Do Scaleway consumers avoid removed private-IP metadata?
- Do detection paths account for CloudStack leases and Oracle iBFT?
- Do reporting consumers preserve finish-event duration and integer exit codes?
