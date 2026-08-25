# Atomic, Cloud, and Container Workflows

## Contents

- Image-mode package and deployment management
- Atomic Desktop behavior
- CoreOS and IoT images
- Cloud and container metadata
- Podman and Netavark migration

## Image-mode package and deployment management

### DNF and bootc on image-mode systems (41)

Atomic Desktops, CoreOS, and IoT include DNF5 and `bootc`. DNF works while
building their container images. On a booted image-mode system it redirects
package changes to deployment-aware tools instead of modifying the deployment.
`rpm-ostree` remains available; `bootc` can switch and update deployments:

```console
sudo bootc switch quay.io/fedora/fedora-iot
```

### Atomic Desktop update authorization (41)

rpm-ostree policy lets ordinary users refresh metadata and update without
authentication. Passwordless administrator operations include package
layering, rollback, transaction cancellation, and cleanup. Changing kernel
arguments or rebasing to another image requires authorization.

## Atomic Desktop behavior

### composefs roots on CoreOS and IoT (41)

CoreOS and IoT mount `/` through composefs, making the deployed root genuinely
read-only. This initial default did not yet apply to Fedora 41 Atomic Desktops.

### Atomic Desktops use composefs roots (42)

Atomic Desktop variants now also mount `/` through composefs, extending the
CoreOS and IoT behavior and making their deployed roots genuinely read-only.

### Atomic image renames (41)

Move unofficial Sericea and Onyx image references to `sway-atomic` and
`budgie-atomic`; publication under the old names is being removed.

### Kinoite enables automatic updates by default (43)

Plasma Discover stages Kinoite system updates through rpm-ostree automatically
by default. Users can disable automatic updates or change their frequency in
system settings.

### Atomic Desktops drop FUSE 2 (44)

Atomic Desktop images omit FUSE 2 binaries and libraries. Layered workloads
must not assume the deprecated FUSE 2 runtime is present.

## CoreOS and IoT images

### CoreOS updates move to OCI transport (42)

New Fedora 42 CoreOS installations fetch updates from
`quay.io/fedora/fedora-coreos` rather than the Fedora OSTree repository. They
still use Zincati and rpm-ostree, not bootc. Existing nodes migrate through a
barrier release; the old repository remained active until Fedora 43.

### CoreOS updates are OCI-only (43)

The transition is complete: new CoreOS updates are no longer published to the
canonical OSTree repository and arrive only as OCI images from Fedora's
`quay.io` registry.

### Fedora CoreOS is defined by a Containerfile (43)

Build Fedora CoreOS locally or in CI with `podman build` from a Containerfile
based on the Fedora bootc image. The previous custom compose path is no longer
required for these builds.

### Fedora IoT replaces Zezere (42)

Fedora IoT initial configuration uses `systemd-firstboot` instead of the Zezere
provisioning server, including where Zezere's IPv6 behavior previously blocked
setup.

## Cloud and container metadata

### Fedora container-image OCI labels are renamed (44)

Fedora images replace `org.opencontainers.image.name` with
`org.opencontainers.image.title` and `org.opencontainers.image.license` with
`org.opencontainers.image.licenses`. Update inspection, admission, and policy
tooling to query the new labels.

## Podman and Netavark migration

The following requirements are from the included `future-podman-6` readiness
batch and must be applied before the major upgrade.

### Podman 6 removes slirp4netns and cgroups v1 (future-podman-6)

Podman 6 removes slirp4netns, cgroups v1 support, and the slirp-specific
`--network-cmd-path` option. Move rootless networking to Pasta with Netavark
and make sure hosts use cgroups v2 before upgrading.

### BoltDB must be migrated before Podman 6 (future-podman-6)

Podman 6 removes the BoltDB backend. Unmigrated BoltDB state makes existing
container state unusable after the upgrade. First upgrade to Podman 5.8 and
reboot so state migrates to SQLite; only then install Podman 6.

### Netavark drops iptables support (future-podman-6)

Netavark no longer supports iptables, rather than merely preferring nftables.
Migrate manually configured iptables-based Podman networking to nftables.

### Remote-client configuration is refactored (future-podman-6)

Podman 6 substantially refactors remote-client configuration and unifies
parsing behavior for `containers.conf` and `storage.conf`. Existing
`containers.conf` files may need migration or separation into client and
server settings, especially for Windows and macOS remote clients.
