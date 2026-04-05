# Package Management Changes (Rocky Linux 10.0+)

## DNF Modularity Removed

DNF 5 removes the modularity system entirely. All `dnf module` commands are gone. Use direct package management instead.

### Migration Reference

| Task | Old (RL 9.x `dnf module`) | New (RL 10+) |
|------|---------------------------|--------------|
| List available versions | `dnf module list nginx` | `dnf repoquery nginx` |
| Install specific version | `dnf module enable nginx:1.14 && dnf module install nginx:1.14` | `dnf install nginx-1.26.3` |
| Remove | `dnf -y module remove --all nginx:1.14` | `dnf remove nginx-1.26.3` |

### Key Differences

- No module streams — install packages by exact version directly
- No `dnf module enable/disable/reset` — these commands do not exist
- No module profiles — install individual packages or groups directly
- `dnf repoquery <package>` replaces `dnf module list <package>` for version discovery

### Common Patterns

```bash
# Discover available versions of a package
dnf repoquery --available nginx

# Install a specific version
dnf install nginx-1.26.3

# List installed version
dnf list installed nginx
```

## rpmsort — RPM Version Sorting Utility

`rpmsort` is a new utility that correctly sorts RPM version strings using RPM's version comparison algorithm. Standard `sort` produces incorrect results for RPM versioning.

### Usage

```bash
# Correct version ordering
rpm -q kernel | rpmsort
# Output: kernel-6.12.0-13, kernel-6.12.0-130 (correct order)

# Standard sort gets it wrong
rpm -q kernel | sort
# Output: kernel-6.12.0-130, kernel-6.12.0-13 (wrong — lexicographic)
```

### When to Use

- Sorting RPM package lists by version
- Scripts that compare or order package versions
- Any context where RPM epoch:version-release ordering matters

`rpmsort` reads from stdin and writes sorted output to stdout, making it a drop-in replacement for `sort` in RPM version pipelines.
