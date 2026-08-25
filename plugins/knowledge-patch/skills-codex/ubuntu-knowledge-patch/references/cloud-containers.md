# Cloud Images, Provisioning, and Containers

## cloud-init provisioning

### NoCloud, WSL, and configuration validation

Cloud-init 24.3.1 in Ubuntu 24.10 adds FTP and FTPS NoCloud seeds, NoCloud
`network-config` seed support, network-v2 schema validation, NVMe disk setup, and
remote URI sources for `write_files`. WSL gains multipart MIME configuration and
Landscape tags.

`DEPRECATION_INFO_BOUNDARY` lets a stable downstream image pin its original
cloud-init major/minor boundary so later cloud-init upgrades do not turn newer
deprecation classifications into status failures.

### Boot-stage process model

The four cloud-init systemd boot stages in Ubuntu 24.10 share one Python process
through `cloud-init-main.service`. Cloud-init warns if a stage is invoked by a
PID other than that root process. Automation must invoke the systemd units rather
than call boot stages from post-production scripts.

### Platform package split

Ubuntu 25.04 divides cloud-init dependencies between `cloud-init-base` for
common dependencies and `cloud-init-<cloudname>` metapackages for platform
dependencies. The `cloud-init` metapackage preserves the previous install-all
behavior.

Cloud-init 25.1.1 also adds:

- networkd `RequiredForOnline` support;
- single-stack IPv6 on Oracle and IPv6 address configuration on SmartOS;
- a CloudCIX datasource;
- VMware network-v2 conversion and datasource priority; and
- recognition of Samsung Cloud Platform as OpenStack.

### Mandatory non-x86 datasource declaration

Cloud-init 25.3 in Ubuntu 25.10 disables itself on non-x86 machines unless a
known datasource is declared during early boot through DMI, kernel parameters,
filesystem configuration, or environment files. Image builders and cloud
administrators must declare one or newly launched instances may be unreachable
over SSH.

### New datasource behavior

Cloud-init 25.3 adds Raspberry Pi OS support, early ephemeral networking on
CloudStack, EC2 metadata crawling across multiple NICs, GCE instance-data
templating, Hetzner private-network metadata, and VMware per-boot and hotplug
network updates. `cloud-init clean` gains a generalized datasource-clean
operation. WSL can provision a Landscape installation request ID.

## Cloud-image publication and behavior

### Per-image package changes

Ubuntu 24.10 cloud images publish a companion `.image_changelog.json`. It lists
package additions, removals, and changes; relevant package changelog entries;
and addressed CVEs relative to both the previous daily image and the previous
release image.

### Azure images

Azure publishes all Ubuntu 24.10 variants under the `ubuntu-24_10` offer and
uses plans for derivatives. New images set both `net.core.rmem_max` and
`net.core.rmem_default` to `1048576`.

Ubuntu 25.10 Azure images include `azure-vm-utils`, providing consistent disk
names across SCSI and NVMe and improved handling of MANA and Mellanox accelerated
networking. Do not retain custom udev or Netplan rules that merely reproduce
those functions without first checking for conflicts.

### Google Cloud images

Ubuntu 24.10 Google images support Intel TDX confidential VMs and advertise the
capability with the `TDX_CAPABLE` guest-OS metadata flag.

Google Cloud's console SSH-in-browser button is incompatible with Ubuntu 25.10
because it depends on the deprecated `diffie-hellman-group-exchange-sha256` and
`diffie-hellman-group14-sha1` algorithms. Use a compatible SSH client or access
path instead of weakening server algorithms without review.

### WSL image location

From Ubuntu 25.04, Ubuntu WSL images are published at
`cdimage.ubuntu.com/ubuntu-wsl/`, not `cloud-images.ubuntu.com`.

## LXD host and profile compatibility

Ubuntu 24.10 containers require cgroup v2 and an LXD build with
systemd-credential support. The documented compatible channels are
`latest/stable`, `5.21/stable`, and `5.0/edge`. A Focal host also requires its
HWE kernel. With an affected LXD 5.0 installation,
`-c security.nesting=true` can permit launch. Ubuntu 18.04 and older containers
cannot run on an Ubuntu 24.10 cgroup-v2 host.

In Ubuntu 25.10 Questing containers, an AppArmor profile can be applied to the
wrong process and unexpectedly block shell redirection such as
`<tool> > output.log`.

## Container runtimes

### Containerd 2 and runc 1.2

Containerd 2.0.2 in Ubuntu 25.04 removes functionality deprecated during the
1.x series. Review configuration and integration APIs for 2.0 compatibility.

Runc 1.2.5:

- permits an unlimited cgroup-v2 memory limit with a finite swap limit;
- applies bind-mount options that clear flags;
- rejects bind mounts containing superblock flags;
- ignores `--criu` with a warning;
- makes `kill -a` unnecessary for shared PID namespaces; and
- supports per-mount ID mappings and `cgroup.kill`.

The mount changes can turn previously tolerated container specifications into
hard failures; validate generated OCI configurations.

### Docker networking and inspection

Docker in Ubuntu 25.04 no longer places the container short ID in the
`Aliases` field returned by `docker inspect`. Consumers must use `DNSNames`,
which contains the name, hostname, network aliases, and short ID.

IPv6 iptables support is no longer experimental and is enabled by default for
Linux bridge networks.

### Docker build and Compose commands

Docker adds `docker image ls --tree` and `docker image push --platform`.
Buildx replaces experimental `--print` with `--call` and adds
`buildx history`. Compose adds `config --environment`, `watch --prune`, and Bake
support.
