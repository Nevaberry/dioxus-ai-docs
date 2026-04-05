# Debian 13 (Trixie) Architecture Changes

## i386: Legacy-Only

From trixie, i386 is no longer a regular architecture:
- No official kernel
- No Debian installer
- Fewer packages available
- Requires SSE2 (amd64 CPU) -- most 32-bit CPUs not supported

**Intended use**: running legacy code via multiarch or chroot on 64-bit (amd64) systems.

**Do NOT upgrade i386 systems to trixie.** Options:
- Reinstall as amd64
- Retire hardware
- [Cross-grading](https://wiki.debian.org/CrossGrading) (risky)

## riscv64: First Official Support

Debian 13 is the first release officially supporting 64-bit RISC-V hardware. Full Debian 13 features available.

## armel: Last Release

From trixie, armel is no longer a regular architecture:
- No Debian installer
- Only Raspberry Pi 1, Zero, and Zero W supported by kernel packages

Users can upgrade if hardware is kernel-supported or using third-party kernel.

**Trixie is the last release for armel.** Migrate to armhf or arm64.

## mipsel/mips64el: Removed

These architectures are no longer supported by Debian. Users should switch to different hardware.

## /boot Size Requirements

Kernel and firmware packages have grown significantly.

**Before upgrading:**
- `/boot` partition: at least 768 MB, ~300 MB free
- No separate `/boot`? Nothing to do.

If `/boot` is too small and in LVM:
```bash
lvextend ...  # increase size
```

If `/boot` is a regular partition: likely easier to reinstall.

## Supported Architectures

| Architecture | Status |
|-------------|--------|
| amd64 | Full support |
| arm64 | Full support |
| armel | Last release, limited kernel |
| armhf | Full support |
| ppc64el | Full support |
| riscv64 | New, full support |
| s390x | Full support |
| i386 | Legacy only (multiarch/chroot) |

## Hardening on arm64

PAC (Pointer Authentication) for ROP protection and BTI (Branch Target Identification) for COP/JOP protection are enabled automatically on supporting hardware.
