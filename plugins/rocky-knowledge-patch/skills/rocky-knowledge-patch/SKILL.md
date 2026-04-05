---
name: rocky-knowledge-patch
description: Rocky Linux changes since training cutoff (latest: 10.0) — DNF 5 (modularity removed), Valkey replaces Redis, rpmsort, rh_waived kernel arg. Load before working with Rocky Linux.
license: MIT
metadata:
  author: Nevaberry
  version: "10.0"
---

# Rocky Linux 10+ Knowledge Patch

Claude's baseline knowledge covers Rocky Linux through 9.3. This skill provides changes from 9.5 (2024) onwards.

## Quick Reference

### Breaking Changes in Rocky Linux 10.0

| What Changed | Old (RL 9.x) | New (RL 10+) |
|--------------|---------------|--------------|
| Package streams | `dnf module enable/install` | Direct `dnf install pkg-version` |
| Version discovery | `dnf module list <pkg>` | `dnf repoquery <pkg>` |
| Redis | `dnf install redis` | `dnf install valkey` |
| Redis CLI compat | Built-in | `dnf install valkey-compat-redis` (Plus repo) |
| Deprecated kernel features | Enabled by default | Disabled; add `rh_waived` to re-enable |
| RPM version sorting | `sort` (incorrect) | `rpmsort` (RPM-aware) |

### DNF Modularity Removed

DNF 5 removes modularity entirely. All `dnf module` commands are gone:

```bash
# RL 9.x (no longer works in 10)
dnf module enable nginx:1.14
dnf module install nginx:1.14

# RL 10+ (direct install)
dnf repoquery --available nginx # discover versions
dnf install nginx-1.26.3        # install specific version
```

See `references/package-management.md` for full migration table and patterns.

### Valkey Replaces Redis

Redis is removed. Valkey 8.0 (API-compatible fork) is the replacement:

```bash
dnf install valkey
systemctl enable --now valkey
```

For `redis-cli`/`redis-server` command compatibility:

```bash
dnf install valkey-compat-redis # from Plus repo
redis-cli ping                  # works as alias to valkey-cli
```

See `references/service-changes.md` for configuration paths and migration details.

### rpmsort — RPM Version Sorting

```bash
rpm -q kernel | rpmsort # correct: 6.12.0-13 before 6.12.0-130
rpm -q kernel | sort    # wrong: 6.12.0-130 before 6.12.0-13
```

### rh_waived Kernel Argument

Deprecated/insecure kernel features are disabled by default. Re-enable for legacy workloads:

```bash
sudo grubby --update-kernel=ALL --args="rh_waived"
```

See `references/service-changes.md` for details on when this is needed.

## Reference Files

| File | Contents |
|------|----------|
| `package-management.md` | DNF modularity removal migration, rpmsort usage |
| `service-changes.md` | Valkey/Redis replacement, rh_waived kernel argument |
