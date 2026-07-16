# Containers and virtualization

## Build and transfer container images

Podman 4.9 on Rocky Linux 9.4 adds the Technology Preview `podman build farm`
command for multi-architecture builds. Its REST API reports transfer progress,
and `Containerfile` supports multi-line HereDoc instructions.

Podman 5.0 on Rocky Linux 9.5 makes multi-architecture image builds fully
supported, adds manifest management, and expands Quadlet-based automatic
systemd service generation. Rocky Linux 10.0 also lets image pushes and pulls
configure retry counts and delays.

## Configure Podman storage and behavior

Rocky Linux 9.4 adds configuration modules in `containers.conf` and fully
supports SQLite as a default database backend. Migrate away from the deprecated
BoltDB backend and `container-tools:4.0` module.

Rocky Linux 10.0 Podman 5 uses `crun` rather than `runc` as the default runtime
and makes cgroup v2 the default cgroup version.

## Migrate container networking

On Rocky Linux 9.4, the `pasta` network name and CNI network stack are
deprecated; CNI is planned for removal in a future release. On Rocky Linux
10.0, the `slirp4netns` network mode is deprecated.

## Modernize virtualization management

Rocky Linux 10.0 deprecates the monolithic `libvirtd` daemon in favor of modular
daemons and sockets. It also deprecates the i440fx machine type and Virtual
Machine Manager, with Cockpit intended to replace Virtual Machine Manager.

