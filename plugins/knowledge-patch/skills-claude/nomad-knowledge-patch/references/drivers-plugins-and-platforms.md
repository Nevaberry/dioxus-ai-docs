# Drivers, Plugins, and Platforms

## Plugin loading and compatibility

### External plugin configuration

Since 1.10.0, executables in `plugin_dir` run only when a matching `plugin`
configuration block exists. Unconfigured plugins are skipped.

### Remote task-driver removal

Since 1.10.0, task drivers no longer support remote tasks. This breaks custom
drivers that used that interface.

### Driver network hash removal

Since 2.0.5, `DriverNetwork.Hash` has been removed from the `plugin/drivers`
package. Update custom driver plugins that reference the method before building
against Nomad 2.0.5.

### Secrets plugin timeout

Since 2.0.0, the secrets plugin execution timeout is 60 seconds, changing when
slow plugin operations time out.

## Driver configuration and execution

### Docker and raw_exec additions

Since 1.10.0, the Docker driver plugin accepts `image_pull_timeout`.

The `raw_exec` driver accepts `denied_envvars` in both driver and task
configuration and supports selecting the task user on Windows.

### Executor failure exit code

Since 1.10.0, executor failures in the `exec`, `raw_exec`, `java`, and `qemu`
task drivers report exit code `-1`.

## QEMU behavior

### Machine configuration

Nomad 1.11.1 adds QEMU task fields `emulator` and `machine_type`, defaulting to
`qemu-system-x86_64` and `pc`.

The `kvm` accelerator no longer forces machine type `host`. A `resources.cores`
value supplies `-smp` only when the user has not provided a custom `-smp` flag.

### Filesystem environment paths

In Nomad 1.11.2, filesystem environment variables exposed by the QEMU driver
contain host file paths instead of relative container paths such as `/alloc`
and `/local`. Update jobspecs that use those variables.

## Platform support

Nomad Enterprise 2.0 adds Linux support for the `ppc64le` CPU architecture.
