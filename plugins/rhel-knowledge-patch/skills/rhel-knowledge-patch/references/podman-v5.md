# Podman v5 — RHEL 10

## Default Changes

- **cgroups v2** is the default (not v1)
- **`pasta`** is the default rootless network backend (not `slirp4netns`)
- **`containers.conf`** is read-only for system connections and farm info — managed via `podman.connections.json`
- **sigstore signatures** used for image verification (replaces GPG/simple signing)

## Multi-Architecture Builds

`podman farm build` is fully supported for creating multi-arch images:

```bash
# Set up farm nodes
podman system connection add arm-node ssh://user@arm-host/run/podman/podman.sock
podman farm create my-farm arm-node local

# Build and push multi-arch manifest
podman farm build --tag registry.example.com/myapp:latest .
```

A farm is a group of machines with UNIX Podman sockets. The `farm build` command:
1. Builds on all nodes
2. Pushes images to registry
3. Creates and pushes manifest list

## Quadlet Enhancements

Quadlet supports `.pod` files (not just `.container`, `.volume`, `.network`, `.image`, `.build`, `.kube`):

### Pod Quadlet Keys
```ini
# myapp.pod
[Pod]
PodName=myapp
DNS=8.8.8.8
DNSOption=ndots:5
DNSSearch=example.com
IP=10.88.0.10
IP6=fd00::10
UserNS=keep-id
PublishPort=8080:80
AddHost=db:10.0.0.5
```

### Container Quadlet Keys (new)
```ini
[Container]
CgroupsMode=enabled
StartWithPod=true
# Mount image managed by .image file
Mount=type=image,source=mydata.image,dst=/data
# Share network with another container
Network=other.container
```

### General Quadlet Features
- `ServiceName` key to set systemd service name in all Quadlet types
- `DefaultDependencies=false` to disable `network-online.target` dependency
- Quadlets can be placed in `/run/containers/systemd`
- `PublishPort` values can contain variables

## Container Management

```bash
# Runtime resource changes are persistent
podman update --cpus 4 --memory 2g mycontainer

# Health check management on running containers
podman update --health-cmd "curl -f http://localhost/" mycontainer
podman update --no-healthcheck mycontainer

# Health check logging
podman run --health-log-destination /var/log/health.log \
  --health-max-log-count 10 \
  --health-max-log-size 500 myimage

# Disable health check events globally
# In containers.conf [engine] section:
# healthcheck_events = false
```

## Volume and Mount Options

```bash
# Mount subset of volume
podman run --mount type=volume,source=myvol,dst=/data,subpath=config ...

# Mount subset of image
podman run --mount type=image,source=myimage,dst=/data,subpath=etc ...

# Multiple hostnames in --add-host (semicolon-separated)
podman run --add-host "host1;host2:192.168.1.1" ...
```

## Networking

```bash
# Use existing bridge without modification
podman network create --driver bridge --opt mode=unmanaged mynet

# macvlan/ipvlan interface names configurable in containers.conf
# [network] section: interface_name = "eth0"

# Specify host-side interface name
podman run --network bridge:host_interface_name=veth-myapp ...

# Container hostname passed to DHCP
podman run --hostname myapp --network bridge ...
```

## Kubernetes Integration

```bash
# Generate and run Kubernetes Job YAML
podman kube generate --type job mycontainer >job.yaml
podman kube play job.yaml

# CDI devices in kube play
podman kube play --device "vendor.com/device=mydevice" pod.yaml

# Image-based volumes in Kubernetes YAML
# Use annotation: io.podman.annotations.kube.image.automount/$ctrname
```

## `--compat-volumes` Build Option

The `--compat-volumes` flag restores old VOLUME instruction behavior where RUN changes to VOLUME directories are discarded:

```bash
podman build --compat-volumes -t myimage .
```

This was previously the default but is now opt-in.
