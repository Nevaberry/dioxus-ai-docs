# DNF5 Replaces DNF4 (Fedora 41+)

`dnf` is now DNF5, a C++ rewrite. This is a breaking change for scripts and automation targeting Fedora 41+.

## Mandatory Subcommands

Optional subcommands from DNF4 are now required:

```bash
# Old (DNF4)              → New (DNF5)
dnf history <id>          → dnf history info <id>
dnf updateinfo            → dnf advisory summary
dnf repolist              → dnf repo list        # alias still works
dnf groupinstall <grp>    → dnf group install <grp>
```

## Renamed/Restructured Commands

### config-manager

Uses subcommands instead of flags:

```bash
# Add a repo
dnf config-manager --add-repo URL     → dnf config-manager addrepo --from-repofile=URL

# Set options
dnf config-manager --save --setopt=.. → dnf config-manager setopt key=value

# Enable/disable repos
dnf config-manager setopt fedora.enabled=0
```

### shell → do

The interactive `dnf shell` is replaced by a non-interactive `dnf do`:

```bash
dnf shell                 → dnf do install pkg1 remove pkg2
```

### mark subcommands

```bash
dnf mark install pkg      → dnf mark user pkg
dnf mark remove pkg       → dnf mark dependency pkg
```

### repoquery

```bash
dnf rq --resolve --requires pkg → dnf rq --providers-of=requires pkg
```

### download

```bash
dnf download --source pkg → dnf download --srpm pkg
```

## Dropped Options

| Old Option | Replacement |
|-----------|-------------|
| `-4` / `-6` | `ip_resolve` config option |
| `--verbose` | Removed (no replacement) |
| `--downloaddir` | `--destdir` |
| `--skip-broken` (on upgrade) | `--no-best` |

## Config Changes

| Setting | DNF4 | DNF5 |
|---------|------|------|
| Cache dir (root) | `/var/cache/dnf` | `/var/cache/libdnf5` |
| Cache dir (user) | `~/.cache/dnf` | `~/.cache/libdnf5` |
| Makecache timer | `dnf-makecache.timer` | `dnf5-makecache.timer` |
| Auto-updates timer | `dnf-automatic.timer` | `dnf5-automatic.timer` |
| `best` default | `false` | `true` |
| `strict` option | Single option | Split into `skip_broken` and `skip_unavailable` |
