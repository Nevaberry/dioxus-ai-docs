# Containers and Virtual Machines

## Run managed VMs

- Vmspawn can boot a directory or a direct kernel/initrd, choose firmware and software TPM use, configure user namespaces and networking, add bind mounts or drives, register with machined, and pass transient SSH keys (since 256).
- `systemd-vmspawn@.service` runs images as units. `machinectl --runner=vmspawn` or `machinectl -V` chooses vmspawn instead of nspawn (since 256).
- Vmspawn supports unprivileged networking, `--grow-image=`, `--tpm-state=`, and `--notify-ready=` (since 258).
- `systemd-vmspawn --ephemeral` runs a disposable VM. `--image-format=` selects raw or qcow2, and an extra drive's format can be supplied in the colon-separated `--extra-drive=` argument (since 260).
- Vmspawn accepts `--bind-user=` and `--bind-user-shell=`; both vmspawn and nspawn accept `--bind-user-group=`. A file-backed VM disk exposes its backing filename as its serial, enabling stable guest `/dev/disk/by-id/` selection (since 259).

## Integrate containers with the host

- Container payloads export AF_UNIX sockets to the host through `/run/systemd/nspawn/unix-export/`. The `owneridmap` option on `--bind=` maps the host owner to the container-side owner, and Wi-Fi interfaces can be moved into a container (since 256).
- PID 1 sends its supervisor `X_SYSTEMD_HOSTNAME=`, `X_SYSTEMD_MACHINE_ID=`, `X_SYSTEMD_UNIT_ACTIVE=`, `X_SYSTEMD_SIGNALS_LEVEL=2`, `X_SYSTEMD_SHUTDOWN=`, and `X_SYSTEMD_REBOOT_PARAMETER=` notifications. A supervisor can use target notifications such as `ssh-access.target` rather than polling (since 256).
- When a container payload has no systemd installation, nspawn mounts unified cgroup2 into it by default. `SYSTEMD_NSPAWN_UNIFIED_HIERARCHY=0` retains the earlier behavior where still supported (since 257; cgroup v1 itself is gone in 258).
- An `.nspawn` file can join an existing network namespace with `[Network] NamespacePath=` (since 259).

```ini
[Network]
NamespacePath=/run/netns/build
```

## Run unprivileged containers

- `systemd-nsresourced` allocates transient 65,536-entry UID/GID ranges and delegates mounts, cgroups, and network interfaces. `systemd-mountfsd` mounts verity-backed DDIs and returns mount file descriptors (since 256).
- This allows unprivileged `systemd-dissect`, user-manager `RootImage=`, and `systemd-nspawn --image=`. Untrusted images still require Polkit approval (since 256).
- Directory-tree containers can use a foreign UID/GID range beneath a caller-owned parent, and unprivileged VMMs can receive automatically routed TAP devices. `--private-users=managed` requests nsresourced allocation even for privileged nspawn (since 258).
- Nsresourced can allocate multiple additional 65,536-ID ranges, combine a caller-UID-only map with them, and optionally identity-map the foreign range. Its BPF-LSM policy no longer rejects inode access solely because ownership lies outside a transient range (since 260).
- Expose the mountfsd and nsresourced Varlink sockets inside nested containers when delegation is intended; nspawn automates this with `--private-users-delegate=` (since 260).

## Use capsules and per-user daemons

- A capsule is an extra per-user service manager using a transient `DynamicUser=` identity and `/var/lib/capsules/<name>` as its home. Start `capsule@<name>.service`, then address it with `systemctl -C <name>` or `--capsule=` (since 256).
- Machined and importd have per-user instances. Select them with `machinectl --user` and `importctl --user`; user images live below `~/.local/state/machines/` (since 259).
- Nspawn and vmspawn register with the caller's and system machined instances when authorized. `RegisterMachineEx()` and `CreateMachineEx()` accept pidfds (since 259).
- Portabled has a user instance selected with `portablectl --user` or `--system`. On attachment it generates a policy and pins the image so it cannot be silently replaced (since 260).

## Connect without guest networking

- `systemd-ssh-generator` socket-activates `sshd@.service` on VSOCK port 22 in VMs, on exported AF_UNIX sockets in containers, and on `/run/ssh-unix-local/socket` locally. Add listeners with `systemd.ssh_listen=` or the `ssh.listen` credential (since 256).
- `systemd-ssh-proxy` connects OpenSSH to these transports, such as `ssh vsock/4711`, `ssh unix/run/ssh-unix-local/socket`, or a registered VM via `ssh machine/foobar` (since 256 and 257).
- Vmspawn can forward the guest journal to the host over VSOCK with `--forward-journal=` (since 256).

## Compose OCI-backed roots

- An MStack is a self-contained `.mstack/` directory describing OverlayFS layers and bind mounts. `importctl pull-oci` downloads OCI content into this form (since 260).
- Inspect it with `systemd-mstack`, use it as a service root with `RootMStack=`, or run it with nspawn's `--mstack=` (since 260).
- Nspawn supports unprivileged FUSE, and `--bind-user=` propagates an SSH key from the bound user record (since 257).
