# Container SELinux Policies with udica

udica is a tool that generates custom SELinux CIL policies for containers based on their runtime inspection data. It analyzes a container's capabilities, mount points, and exposed ports to produce a tailored policy that is more permissive than the default `container_t` only where needed.

## Basic Workflow

### 1. Inspect the Container

udica reads JSON inspection output from Podman or Docker:

```bash
# Podman
podman inspect <container_id> | udica my_policy

# Docker
docker inspect <container_id> | udica my_policy
```

udica parses the inspection JSON for:
- **Capabilities** (e.g., `NET_ADMIN`, `SYS_PTRACE`)
- **Mount points** (bind mounts, volumes, and their paths)
- **Exposed ports** (TCP/UDP port bindings)

### 2. Install the Generated Policy

The generated `.cil` file must be installed alongside the udica CIL template modules it depends on:

```bash
semodule -i my_policy.cil \
    /usr/share/udica/templates/{base_container.cil,net_container.cil,home_container.cil}
```

### 3. Run with the Custom Policy

Apply the policy type to the container at launch:

```bash
# Podman
podman run --security-opt label=type:my_policy.process ...

# Docker
docker run --security-opt label=type:my_policy.process ...
```

## Template Modules

udica selects templates based on detected container properties. Templates are CIL files installed in `/usr/share/udica/templates/`:

| Template | Selected When |
|---|---|
| `base_container.cil` | Always included (base permissions) |
| `net_container.cil` | Container exposes network ports |
| `home_container.cil` | Container mounts paths under `/home` |

The generated policy uses CIL `blockinherit` to compose the selected templates into a single coherent policy.

## How udica Differs from audit2allow

| | `audit2allow` | `udica` |
|---|---|---|
| **Input** | AVC denial logs (reactive) | Container spec (proactive) |
| **Timing** | After denials occur | Before running the container |
| **Scope** | Permits exactly what was denied | Permits what the container spec declares |
| **Format** | M4 `.te` module | CIL `.cil` module |

udica generates policies proactively from the container specification, while `audit2allow` reacts to logged denials after the fact.
