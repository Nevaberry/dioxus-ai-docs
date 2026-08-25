# Containers and Virtual Machines

## Managers and transports

### Capsules (256)

A capsule is a per-user service manager using a transient `DynamicUser=` and
`/var/lib/capsules/<name>` home. Start `capsule@<name>.service`; address it
with `systemctl --capsule=`/`-C` or `systemd-run --capsule=`.

### Host lifecycle notifications (256)

PID 1 reports hostname, machine ID, reached targets, installed signal
handlers, shutdown type, and reboot argument with `X_SYSTEMD_HOSTNAME=`,
`X_SYSTEMD_MACHINE_ID=`, `X_SYSTEMD_UNIT_ACTIVE=`,
`X_SYSTEMD_SIGNALS_LEVEL=2`, `X_SYSTEMD_SHUTDOWN=`, and
`X_SYSTEMD_REBOOT_PARAMETER=`. Supervisors can gate access on target
notifications such as `ssh-access.target` instead of polling.

### Socket-activated SSH (256, 257)

`systemd-ssh-generator` activates `sshd@.service` on VSOCK port 22, exported
container UNIX sockets, or `/run/ssh-unix-local/socket`. Add listeners with
`systemd.ssh_listen=` or `ssh.listen`; connect using systemd-ssh-proxy, for
example `ssh vsock/4711`, `ssh unix/run/ssh-unix-local/socket`, or a registered
VM name such as `ssh machine/foobar`. Userdb authorized keys allow SSH to
unlock homed homes.

### Per-user machine and image daemons (259)

Machined and importd have user instances selected by `machinectl --user` and
`importctl --user`; images live under `~/.local/state/machines/`. Nspawn and
vmspawn register with caller and system instances when permitted.
`RegisterMachineEx()` and `CreateMachineEx()` accept pidfds.

### Machined request contract (258.10-261.2)

The machine registration Varlink method no longer accepts `supervisor` in any
covered point release. The D-Bus shell operation accepts numeric user IDs.

## Nspawn containers

### Host integration and bind ownership (256)

Guests export UNIX sockets below `/run/systemd/nspawn/unix-export/`.
`--bind=` option `owneridmap` maps the host owner to the container owner, and
Wi-Fi interfaces can be moved into containers.

### Non-systemd and unprivileged payloads (257, 258)

Nspawn mounts unified cgroup hierarchy into roots without systemd by default;
`SYSTEMD_NSPAWN_UNIFIED_HIERARCHY=0` retains prior behavior where supported.
It supports unprivileged FUSE and `--bind-user=` can propagate a bound user's
stored SSH key.

Foreign-ID allocation and mountfsd/nsresourced allow unprivileged directory
containers below caller-owned parents as well as DDIs, and routed TAP devices
for unprivileged VMMs. `--private-users=managed` requests nsresourced even for
privileged nspawn.

### Existing namespaces and user binding (259)

An `.nspawn` file can join `[Network] NamespacePath=`. Vmspawn supports
`--bind-user=` and `--bind-user-shell=`; both runners accept
`--bind-user-group=`. File-backed VM disks expose their filename as serial for
stable guest `/dev/disk/by-id/` paths.

### Delegation to nested containers (260)

Nsresourced can allocate multiple extra 64K ID ranges, combine a client-UID
mapping with them, and optionally identity-map foreign IDs. Its BPF-LSM policy
does not reject inode access solely for foreign ownership. Expose nsresourced
and mountfsd Varlink sockets to a nested container with nspawn
`--private-users-delegate=`.

### OCI swappiness spelling (258.10-261.2)

All covered point releases read `linux.resources.memory.swappiness`. Use the
spec-correct `swappiness` key in OCI input.

## Vmspawn and image-backed machines

### Managed VM runner (256)

Vmspawn boots directories or kernel/initrd pairs, selects firmware and
software TPM, configures user namespaces/networking, adds binds or drives,
registers with machined, and passes transient SSH keys. Run it as
`systemd-vmspawn@.service`; select it with `machinectl --runner=vmspawn` or
`machinectl -V`.

### Unprivileged networking and readiness (258)

Vmspawn supports unprivileged networking plus `--grow-image=`, `--tpm-state=`,
and `--notify-ready=`.

### Ephemeral and qcow2 machines (260)

Use `systemd-vmspawn --ephemeral` for a disposable machine and
`--image-format=raw|qcow2` for input. `--extra-drive=` accepts its format as a
colon-separated parameter.

## Image-backed workloads

### Unprivileged DDIs (256)

Nsresourced allocates transient 64K UID/GID ranges and delegates mounts,
cgroups, and interfaces; mountfsd mounts Verity-backed DDIs and returns mount
file descriptors. This enables unprivileged dissect, user-manager
`RootImage=`, and `nspawn --image=`; untrusted images require Polkit.

### MStacks (260)

An `.mstack/` directory describes an OverlayFS/bind arrangement. Create one
with `importctl pull-oci`, inspect with `systemd-mstack`, use it as
`RootMStack=` for a service, or run it via nspawn `--mstack=`.

### Per-user portable services (260)

Portabled has a user instance selected with `portablectl --user` or
`--system`. On supported kernels it lets unprivileged users run portable
services. Attachment generates policy and pins the image against silent
replacement.

### Portable-image pool limits (258.10-261.2)

Portabled applies configured pool limits to portable images in v260.4 and
v261.2; portable-service images count against those limits.
