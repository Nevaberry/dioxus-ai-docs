---
name: selinux-knowledge-patch
description: "SELinux changes since training cutoff (latest: 0.1.0) — CIL policy language, udica container policies, allowxperm netlink filtering, default object rules. Load before working with SELinux."
version: "0.1.0"
license: MIT
metadata:
  author: Nevaberry
---

# SELinux Knowledge Patch

Covers SELinux policy development features added after Claude's training cutoff.

**Baseline knowledge**: SELinux modes (enforcing/permissive/disabled), security contexts (user:role:type:level), booleans (`setsebool`/`getsebool`), basic policy management (`semanage`, `semodule`, `restorecon`), and `audit2allow`.

## Quick Reference: CIL vs Kernel Policy Language

CIL (Common Intermediate Language) replaces M4-based `.te`/`.if`/`.fc` policy modules with S-expression syntax:

| Kernel Policy | CIL Equivalent | Notes |
|---|---|---|
| `attribute` | `typeattribute` | Declares a type attribute |
| `typeattribute` | `typeattributeset` | Assigns types to an attribute |
| `attribute_role` | `roleattribute` | Declares a role attribute |
| `allow` | `allow` | Same syntax, S-expression form |
| `module` / `require` | `block` / `blockinherit` | Namespacing replaces module system |

CIL eliminates M4 macro dependency and module load-ordering requirements.

## CIL Policy Basics

CIL uses `(block ...)` for namespacing — all declarations inside a block are scoped:

```cil
(block myapp
    (type process)
    (type data)
    (role app_r)
    (roletype app_r process)
    (allow process data (file (read write open getattr)))
)
```

Types are referenced across blocks as `blockname.typename` (e.g., `myapp.process`).

### Block Inheritance

Blocks can inherit from other blocks, replacing the M4 template/interface pattern:

```cil
(block base_app
    (type process)
    (type data)
)

(block webapp
    (blockinherit base_app)
    ;; webapp.process and webapp.data now exist
    (allow process data (file (read write)))
)
```

### Access Rule Syntax

CIL access rules group permissions by object class in S-expressions:

```cil
;; Single class, multiple permissions
(allow src_t tgt_t (file (read write open getattr)))

;; Multiple classes in one rule
(allow src_t tgt_t (file (read write)) (dir (search getattr)))
```

### Loading CIL Modules

Compile and load CIL policies directly with `semodule` — no `.pp` compilation step:

```bash
semodule -i myapp.cil
semodule -r myapp        # remove
```

See [references/cil-policy.md](references/cil-policy.md) for full CIL syntax details and examples.

## udica: Container Policy Generator

Generate tailored SELinux policies for containers from their runtime inspection data:

```bash
# Inspect running container → generate CIL policy
podman inspect <container_id> | udica my_policy

# Install policy with required template modules
semodule -i my_policy.cil \
    /usr/share/udica/templates/{base_container.cil,net_container.cil,home_container.cil}

# Run container with the custom policy
podman run --security-opt label=type:my_policy.process ...
```

udica parses container JSON for capabilities, mount points, and ports, then combines appropriate CIL template blocks. Works with Podman and Docker.

See [references/container-policy.md](references/container-policy.md) for template selection and advanced usage.

## Kernel Policy Extensions

### allowxperm Netlink Message Filtering (kernel >= 6.13)

Extended permissions now support netlink message type filtering. Requires enabling the `netlink_xperm` policycap:

```cil
(policycap netlink_xperm)
```

Grant base `nlmsg` permission, then filter by message type hex value:

```
allow src_t tgt_t : netlink_route_socket nlmsg;
allowxperm src_t tgt_t : netlink_route_socket nlmsg { 0x12 };
```

Supported socket classes:

| Socket Class | Use Case |
|---|---|
| `netlink_route_socket` | Route, link, address management |
| `netlink_tcpdiag_socket` | TCP diagnostic queries |
| `netlink_xfrm_socket` | IPsec/XFRM policy and state |
| `netlink_audit_socket` | Audit subsystem control |

### Default Object Rules (policy version 27+)

Control which context field (source or target) provides user/role/type/range for newly created objects:

```
default_user file target;
default_role file source;
default_type file source;
default_range file target low;
```

The `low`, `high`, or `low_high` qualifier on `default_range` controls which part of the MLS range is used. Applies to `file`, `dir`, `lnk_file`, `chr_file`, `blk_file`, `sock_file`, `fifo_file` and other object classes that undergo labeling transitions.

See [references/kernel-policy-extensions.md](references/kernel-policy-extensions.md) for detailed semantics and range qualifier reference.

## Reference Files

| File | Contents |
|---|---|
| [cil-policy.md](references/cil-policy.md) | CIL syntax, blocks, inheritance, type/role declarations, access rules |
| [container-policy.md](references/container-policy.md) | udica container policy generation, templates, Podman/Docker workflow |
| [kernel-policy-extensions.md](references/kernel-policy-extensions.md) | allowxperm nlmsg rules, default object rules, policycap requirements |
