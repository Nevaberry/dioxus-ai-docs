---
name: centos-stream-knowledge-patch
description: CentOS Stream changes since training cutoff (latest: 10) — x86_64_v3 minimum, Wayland-only (Xorg removed), Valkey replaces Redis, modularity removed, desktop apps to Flatpak. Load before working with CentOS Stream.
license: MIT
metadata:
  author: Nevaberry
  version: "10"
---

# CentOS Stream Knowledge Patch

Claude's baseline knowledge covers CentOS Stream 9. This skill provides changes in CentOS Stream 10 "Coughlan" (December 2024).

## Breaking Changes Quick Reference

| Change | Impact | Details |
|--------|--------|---------|
| x86_64_v3 minimum | Pre-Haswell/Excavator CPUs unsupported | [centos10-changes](references/centos10-changes.md) |
| Xorg server removed | Wayland-only; Xwayland for legacy X11 apps | [centos10-changes](references/centos10-changes.md) |
| Redis -> Valkey | Package and CLI renames | [centos10-changes](references/centos10-changes.md) |
| Desktop apps removed | GIMP, LibreOffice, Inkscape via Flatpak/EPEL | [centos10-changes](references/centos10-changes.md) |
| Modularity removed | Traditional RPMs only | [centos10-changes](references/centos10-changes.md) |

## CentOS Stream 10 Overview

Released December 2024. Lifecycle until ~2030 (RHEL 10 Full Support). Codename "Coughlan".

### Architectures

- AMD/Intel 64-bit: now **x86_64_v3** (requires AVX2, BMI2, FMA — Haswell/Excavator or newer)
- ARM 64-bit (ARMv8.0-A)
- IBM Power (POWER9)
- IBM Z (z14)

Check CPU support: `ld.so --help`

### Xorg Server Removed

`xorg-x11-server-Xorg` no longer included. Wayland is the only display server. `xorg-x11-server-Xwayland` available for legacy X11 application compatibility.

### Desktop Applications Removed

GIMP, LibreOffice, and Inkscape removed from repositories. Install via Flatpak from [Flathub](https://flathub.org/) or request in EPEL.

### Redis Replaced by Valkey

Redis removed due to license change (BSD-3 -> RSALv2/SSPLv1). **Valkey 7.2** is the API-compatible, BSD-licensed replacement.

### Modularity Removed

No longer uses modularity system for alternative package versions. Traditional non-modular RPM packages used instead. Alternative versions expected to be added over time as standard AppStream packages.

### Repositories

Same structure: BaseOS, AppStream, CRB (disabled by default). DNF 4.20, RPM 4.19.

### Key Package Versions

| Category | Package | Version |
|----------|---------|---------|
| Kernel | Linux | 6.12 |
| Languages | Python | 3.12 |
| | GCC | 14 |
| | Go | 1.23 |
| | Rust | 1.82 |
| | LLVM | 19 |
| | Node.js | 22 |
| | PHP | 8.3 |
| | Ruby | 3.3 |
| | OpenJDK | 21 |
| Databases | PostgreSQL | 16 |
| | MariaDB | 10.11 |
| | MySQL | 8.4 |
| | Valkey | 7.2 |
| Web | Apache | 2.4.62 |
| | nginx | 1.26 |
| Desktop | GNOME | 47 |
| | Qt | 6.7 |

## Reference Files

| File | Contents |
|------|----------|
| [centos10-changes.md](references/centos10-changes.md) | Full details on CentOS Stream 10 changes |
