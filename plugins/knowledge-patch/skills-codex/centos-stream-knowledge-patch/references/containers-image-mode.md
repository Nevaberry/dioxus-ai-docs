# Containers and image mode

## Podman configuration and state

### Podman configuration behavior

Per-user `containers.conf` can set `log-location` for `podman-kube systemd`. Rootless Podman gains an inheritable system-wide configuration layer without breaking existing user overrides. Aardvark-DNS reloads `resolv.conf` changes dynamically instead of requiring a restart. (9.8)

### Podman 5.8 database and Quadlet operations

Podman 5.8.2 automatically attempts to migrate BoltDB state to SQLite after reboot because Podman 6 removes BoltDB. Force a retry with `podman system migrate --migrate-db`. `podman quadlet install` accepts multiple documents separated by `---` when each begins with `# FileName=<name>`. New operations include `podman update --ulimit`, `podman exec --no-session`, and Quadlet file-management APIs. (9.8)

### Podman 5 networking and connection migration

Podman stores system connections and farms in managed `podman.connections.json`; their old `containers.conf` forms are read-only. Rootless `slirp4netns` is deprecated in favor of the default `pasta`. CNI is unsupported: leave `network_backend` unset or set it to `netavark`. During upgrade, remove CNI-backed images and containers with `podman rmi --all --force`. (10.2)

## Major-version runtime migration

### Container runtime and cgroup migration

`runc` is removed. Migrate existing Podman containers to `crun` with `podman system migrate --new-runtime=crun`. Release 10 boots only with cgroup v2, so convert hosts and containers that require cgroup v1.

### Container host and configuration compatibility

Running release 7 containers on a release 10 host is unsupported. The default `storage.conf` location moves from `/etc/containers` to `/usr/share/containers`; automation that edits the packaged configuration must use the new path.

## Images, signing, and disconnected operation

### Sequoia-PGP container signatures

Podman verifies OpenPGP image signatures with Sequoia-PGP while retaining GnuPG signing workflows. `--sign-by-sq-fingerprint` signs with Sequoia-managed keys and supports composite post-quantum algorithms. (10.2)

### Disconnected updates and RHEL 10 runtime images

Air-gapped and disconnected edge deployments can apply updates without internet access. New registry images include `rhel10/ruby-40`, `rhel10/postgresql-18`, `rhel10/python-314-minimal`, `rhel10/mariadb-118`, and `rhel10/php-84`. (10.2)

### Time-zone data in minimal UBI 10

`ubi10-minimal` no longer installs `tzdata`. When migrating container builds, run `microdnf install tzdata`, not `microdnf reinstall tzdata`. (10.2)

## Isolation preview

### MicroVM-isolated containers preview

The Technology Preview `krun` runtime lets a suitably configured `crun` launch container workloads inside lightweight microVMs for an extra isolation boundary. (10.2)
