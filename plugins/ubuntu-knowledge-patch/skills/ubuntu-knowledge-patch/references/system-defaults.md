# System Default Changes — Ubuntu 25.10

## sudo-rs Replaces GNU sudo

`sudo-rs` (a memory-safe Rust rewrite) is now the default sudo provider.

### Binary Renaming

Original GNU sudo binaries are renamed with a `.ws` suffix:

| Command | Now provided by |
|---------|----------------|
| `sudo` | sudo-rs |
| `sudo.ws` | Original GNU sudo |
| `visudo` | sudo-rs |
| `visudo.ws` | Original GNU visudo |

### LDAP Authentication

The `sudo-ldap` package is **removed**. LDAP-based sudo authentication must now be configured through PAM modules instead of the dedicated sudo-ldap integration.

## rust-coreutils Replaces GNU coreutils

Core utilities are now provided by `rust-coreutils` v0.2.2. GNU coreutils remain installed as a fallback.

### Compatibility

rust-coreutils is not yet 100% compatible with GNU coreutils. Edge cases in flag handling or output formatting may differ. If a script breaks:

```bash
# Check which commands have diversions (fallback to GNU)
dpkg-divert --list | grep coreutils

# Explicitly call GNU version if needed
/usr/bin/gnu-<command>
```

## APT 3.1

### New Solver (Default)

The new dependency solver is now the default. It provides better conflict resolution and clearer error messages.

### Diagnostic Commands

```bash
apt why <pkg>           # explain why a package is installed or required
apt why-not <pkg>       # explain why a package cannot be installed
                        # (unresolvable dependencies, conflicts, etc.)
```

### History Commands (Preview)

```bash
apt history-list        # list past apt transactions
apt history-info <id>   # show details of a specific transaction
```

These are preview features — the interface may change in future releases.

### Repository Restriction Directives

Control which packages come from which repositories using `Include` and `Exclude` in sources configuration:

```
# Only allow security packages from this repo
Types: deb
URIs: http://security.ubuntu.com/ubuntu
Suites: questing-security
Components: main
Include: linux-image-*, openssl, openssh-*

# Never install these packages from this repo
Types: deb
URIs: http://ppa.launchpad.net/...
Suites: questing
Components: main
Exclude: python3-core, libc6
```

## wget Removed from Server Seed

`wget` is no longer pre-installed on Ubuntu Server images.

### Replacement

`wcurl` ships with the `curl` package and serves as a drop-in for simple download use cases:

```bash
# Old
wget https://example.com/file.tar.gz

# New
wcurl https://example.com/file.tar.gz
```

For scripts that depend on `wget`, either install it explicitly (`apt install wget`) or migrate to `wcurl`/`curl`.

## Wayland-Only Desktop

The X.org session is removed entirely from the default Ubuntu desktop. GNOME Shell runs exclusively under Wayland.

### Impact

- No X11 session option in the display manager
- Applications relying on X11-specific features need XWayland (installed by default)
- Screen sharing, remote desktop, and accessibility tools should be tested for Wayland compatibility

### Terminal Multiplexers

- `byobu` demoted from main to universe — still installable but not part of the default server package set
- `screen` removed from the server seed entirely — use `tmux` instead
