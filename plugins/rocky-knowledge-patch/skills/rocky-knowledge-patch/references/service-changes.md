# Service and Kernel Changes (Rocky Linux 10.0+)

## Valkey Replaces Redis

Redis has been removed from Rocky Linux 10. Valkey 8.0 is the replacement — an open-source fork with compatible APIs.

### Installation

```bash
# Install Valkey server
dnf install valkey

# Start and enable
systemctl enable --now valkey
```

### Redis Compatibility

For scripts and applications that expect `redis-cli` and `redis-server` commands, install the compatibility package from the Plus repository:

```bash
# Enable Plus repo and install compatibility shim
dnf install valkey-compat-redis

# After install, redis-cli and redis-server commands work as aliases
redis-cli ping # Works — routes to valkey-cli
redis-server   # Works — routes to valkey-server
```

### Key Points

- Valkey is API-compatible with Redis — application code using Redis protocol requires no changes
- Configuration files move from `/etc/redis/` to `/etc/valkey/`
- Default port remains 6379
- The `valkey-compat-redis` package is in the Plus repository, not the base repository

## rh_waived Kernel Argument

Rocky Linux 10 disables deprecated and insecure kernel features by default. To re-enable them for legacy workloads, add `rh_waived` to the kernel command line.

### Usage

```bash
# Temporary (current boot only)
sudo grubby --update-kernel=ALL --args="rh_waived"

# Verify
cat /proc/cmdline | grep rh_waived
```

### When Needed

- Running legacy workloads that depend on deprecated kernel interfaces
- Hardware requiring drivers that use removed kernel APIs
- Migration period while updating applications to use current interfaces

This is a transitional mechanism — plan to update workloads to avoid depending on waived features.
