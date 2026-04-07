# Kernel Policy Extensions

Recent Linux kernel and SELinux userspace releases have added new policy capabilities for finer-grained access control.

## allowxperm Netlink Message Filtering (kernel >= 6.13)

Extended permission rules (`allowxperm`) now support filtering on individual netlink message types via the `nlmsg` permission class. This allows policies to permit specific netlink operations instead of granting blanket access to entire netlink socket classes.

### Prerequisite: Enable the policycap

The `netlink_xperm` policy capability must be enabled in the policy for nlmsg extended permissions to take effect:

```cil
(policycap netlink_xperm)
```

### Syntax

First, grant the base `nlmsg` permission on the socket class, then use `allowxperm` to specify permitted message types by their hex value:

```
allow src_t tgt_t : netlink_route_socket nlmsg;
allowxperm src_t tgt_t : netlink_route_socket nlmsg { 0x12 };
```

The hex values correspond to netlink message type constants (e.g., `RTM_GETLINK` = `0x12` for route sockets).

### Supported Socket Classes

Extended nlmsg permissions are supported on these netlink socket classes:

| Socket Class | Common Message Types |
|---|---|
| `netlink_route_socket` | Route, link, address management |
| `netlink_tcpdiag_socket` | TCP diagnostic queries |
| `netlink_xfrm_socket` | IPsec/XFRM policy and state |
| `netlink_audit_socket` | Audit subsystem control |

## Default Object Rules (policy version 27+)

Default object rules control which security context field — from the **source** (creating process) or **target** (parent directory/object) — is used to populate each field of a newly created object's context.

### Syntax

```
default_user <object_class> source|target;
default_role <object_class> source|target;
default_type <object_class> source|target;
default_range <object_class> source|target [low|high|low_high];
```

### Example

```
default_user file target;
default_role file source;
default_type file source;
default_range file target low;
```

This configuration means when creating a new file:
- **User field**: taken from the target (parent directory)
- **Role field**: taken from the source (creating process)
- **Type field**: taken from the source (creating process)
- **Range field**: taken from the target's low range value

### Range Qualifiers

The `default_range` rule accepts an optional qualifier for MLS (Multi-Level Security) range handling:

| Qualifier | Meaning |
|---|---|
| `low` | Use only the low sensitivity level from source/target |
| `high` | Use only the high sensitivity level from source/target |
| `low_high` | Use the full range (low-high) from source/target |

If no qualifier is specified, the full range is used (equivalent to `low_high`).

### Applicable Object Classes

Default rules apply to object classes that support creation with inherited contexts, including:
- `file`, `dir`, `lnk_file`, `chr_file`, `blk_file`, `sock_file`, `fifo_file`
- Other object classes that undergo labeling transitions
