# CLI Enhancements

## `podman run`/`create --creds` and `--cert-dir` (5.7+)

New options to manage registry authentication inline when pulling images:
```bash
podman run --creds user:pass --cert-dir /path/to/certs docker.io/myimage
```

## `podman kube play` multiple files (5.7+)

Accepts multiple YAML files in a single command. New `--no-pod-prefix` option disables prefixing container names with pod names:
```bash
podman kube play app.yaml db.yaml
podman kube down app.yaml db.yaml
podman kube play --no-pod-prefix app.yaml
```

## `podman wait --return-on-first` (5.7+)

Returns after *any* container matches the condition instead of waiting for all:
```bash
podman wait --return-on-first --condition=exited ctr1 ctr2
```

## `podman exec --no-session` (5.8+)

Skip exec session tracking for faster startup:
```bash
podman exec --no-session mycontainer ls /app
```

## `podman update --ulimit` (5.8+)

Update ulimits on a running container:
```bash
podman update --ulimit nofile=65536:65536 mycontainer
```

## `podman volume create --uid/--gid` (5.6+)

Set ownership when creating volumes:
```bash
podman volume create --uid 1000 --gid 1000 myvolume
```

## `podman machine init --swap` (5.6+)

Enable swap in the VM (size in megabytes):
```bash
podman machine init --swap 2048
```
