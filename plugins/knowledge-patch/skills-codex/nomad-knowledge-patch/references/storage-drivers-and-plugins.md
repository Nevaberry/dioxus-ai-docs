# Storage, Drivers, and Plugins

## Dynamic host volumes

Nomad can create host volumes through the CLI or API without restarting clients
(batch 1.10.0), and stateful deployments can consume them through `volume` and
`volume_mount` blocks.

```shell
nomad volume create ./internal-plugin.volume.hcl
```

The scheduler tracks volume availability, but Nomad does not interpret the
underlying storage. A volume may therefore be local or backed by highly available
network storage; design placement and failure handling accordingly.

`nomad volume status` shows volume capabilities. `nomad volume delete` accepts a
volume ID prefix and a wildcard namespace. CSI volume and plugin events are also
available in the event stream.

## Storage scheduling capacity

Nomad calculates storage available for scheduling as
`totalBytes - client.reserved.disk`, rather than using free disk space (batch
1.11-upgrade). The `unique.storage.bytesfree` attribute is removed. Reserve at
least the disk capacity consumed by the host operating system.

## External plugin registration

Executables discovered in `plugin_dir` run only when a matching `plugin`
configuration block exists (since 1.10.0). Unconfigured executables are skipped.

## Removed remote driver interface

Task drivers no longer support remote tasks (batch 1.10.0). Custom drivers using
that interface must be redesigned before upgrading.

## Driver configuration

The Docker driver plugin accepts `image_pull_timeout`. The `raw_exec` driver
accepts `denied_envvars` in driver and task configuration and can select the task
user on Windows (since 1.10.0).

The secrets plugin execution timeout is 60 seconds (since 2.0.0), changing when a
slow provider operation fails.

## QEMU behavior and paths

Nomad 1.11.1 adds the QEMU task fields `emulator` and `machine_type`, defaulting to
`qemu-system-x86_64` and `pc`. The `kvm` accelerator no longer forces machine type
`host`. A `resources.cores` value supplies `-smp` only when the user has not
provided a custom `-smp` flag.

In Nomad 1.11.2, filesystem environment variables from the QEMU driver contain
host paths instead of relative container-style paths such as `/alloc` and
`/local`. Update jobs that consume those variables.

## Custom driver API compatibility

`DriverNetwork.Hash` is removed from the `plugin/drivers` package in 2.0.5.
Custom driver plugins referencing it must be updated before they can build.

## Architecture support

Nomad Enterprise 2.0.0 supports Linux on the `ppc64le` CPU architecture.
