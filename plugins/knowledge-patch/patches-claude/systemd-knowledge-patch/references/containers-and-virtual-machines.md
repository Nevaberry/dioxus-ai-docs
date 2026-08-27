# Containers and Virtual Machines

## Per-user managers and host integration

### Capsules (256)

A capsule is an extra per-user manager using a transient `DynamicUser=` and a
home below `/var/lib/capsules/<name>`. Start `capsule@<name>.service`, then use
`systemctl --capsule=`/`-C` or the matching `systemd-run` option.

### Nspawn host integration (256)

Payloads export UNIX sockets below `/run/systemd/nspawn/unix-export/`.
`--bind=` accepts `owneridmap` to map the host owner to the container-side
owner, and Wi-Fi interfaces can be moved into a container.

### Host lifecycle notifications (256)

PID 1 reports hostname, machine ID, reached targets, installed signal-handler
level, shutdown type, and reboot argument through `X_SYSTEMD_HOSTNAME=`,
`X_SYSTEMD_MACHINE_ID=`, `X_SYSTEMD_UNIT_ACTIVE=`,
`X_SYSTEMD_SIGNALS_LEVEL=2`, `X_SYSTEMD_SHUTDOWN=`, and
`X_SYSTEMD_REBOOT_PARAMETER=`. Supervisors can gate access on notifications
such as `ssh-access.target`.

### Per-user machine and image daemons (259)

Machined and importd have user instances selected by `machinectl --user` and
`importctl --user`; images live below `~/.local/state/machines/`. Nspawn and
vmspawn register with caller and system instances where permitted.
`RegisterMachineEx()` and `CreateMachineEx()` accept pidfds.

## Nspawn behavior

### Cgroups for non-systemd payloads (257)

Nspawn mounts unified cgroup hierarchy into roots without systemd. Set
`SYSTEMD_NSPAWN_UNIFIED_HIERARCHY=0` only to retain the older behavior.

### Unprivileged directory containers (258)

Foreign-ID ranges plus mountfsd/nsresourced permit directory-tree containers
stored below a caller-owned parent, not only DDI containers. Managed UID/GID
ranges are available through `--private-users=managed` even to privileged
nspawn.

### Delegation to nested containers (260)

Nsresourced can allocate multiple extra 64K ranges, combine a client-UID-only
mapping with them, and optionally identity-map the foreign range. Its BPF-LSM
policy does not reject inode access solely for ownership outside the transient
range. Expose nsresourced and mountfsd Varlink sockets to a child with
`--private-users-delegate=`.

### OCI swappiness spelling (258.10-261.2)

Nspawn reads the spec-correct `swappiness` key from OCI memory resources.

```json
{"linux":{"resources":{"memory":{"swappiness":0}}}}
```

## Vmspawn workflows

### Managed VM runner (256)

Vmspawn boots a directory or direct kernel/initrd, selects firmware and
software TPM, configures namespaces and networking, attaches binds or drives,
registers with machined, and passes transient SSH keys.
`systemd-vmspawn@.service` runs images as units; use
`machinectl --runner=vmspawn` or `machinectl -V`.

### Unprivileged and host-integrated VMs (258, 259)

Vmspawn supports unprivileged routed TAP networking, `--grow-image=`,
`--tpm-state=`, and `--notify-ready=`. It accepts `--bind-user=`,
`--bind-user-shell=`, and, like nspawn, `--bind-user-group=`. File-backed VM
disks expose their backing filename as the guest-visible serial. An `.nspawn`
file may join `[Network] NamespacePath=`.

### Ephemeral and qcow2 machines (260)

Use `systemd-vmspawn --ephemeral` for a disposable VM and `--image-format=`
for raw or qcow2 input. `--extra-drive=` accepts its format as a colon
parameter.

## Access and transports

### Socket-activated SSH (256, 257)

`systemd-ssh-generator` activates `sshd@.service` on VM VSOCK port 22,
container-exported UNIX sockets, and `/run/ssh-unix-local/socket`.
`systemd.ssh_listen=` or the `ssh.listen` credential adds endpoints.
`systemd-ssh-proxy` connects OpenSSH to `vsock/`, `unix/`, or registered
`machine/` targets, for example `ssh vsock/4711`,
`ssh unix/run/ssh-unix-local/socket`, or `ssh machine/foobar`. Homed may unlock
homes through userdb authorized keys.

### Varlink over SSH (257)

`ssh-exec:` starts a remote executable and speaks Varlink over SSH;
`ssh-unix:` tunnels to a remote UNIX socket. The old `ssh:` spelling remains
accepted.

## Images, services, and machine APIs

### Boot-time image workflow (257)

Nspawn supports unprivileged FUSE and `--bind-user=` can carry the bound
record's SSH key. `systemd-import-generator` schedules sysext, confext,
portable-service, nspawn, or vmspawn downloads from kernel arguments or
credentials.

### MStacks (260)

An `.mstack/` directory describes a self-contained OverlayFS and bind-mount
layout. `importctl pull-oci` downloads OCI content into this form;
`systemd-mstack` inspects it, `RootMStack=` uses it in a service, and
`systemd-nspawn --mstack=` runs it.

### Per-user portable services (260)

Portabled has a user instance selected with `portablectl --user` or
`--system`. On attachment it creates policy and pins the image against silent
replacement.

### Machined request contract (258.10-261.2)

Machine registration no longer accepts the redundant `supervisor` Varlink
input. The D-Bus shell operation accepts numeric user IDs as well as names.
