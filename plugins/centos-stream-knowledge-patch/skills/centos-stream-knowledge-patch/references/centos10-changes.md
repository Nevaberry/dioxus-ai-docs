# CentOS Stream 10 "Coughlan" (December 2024)

## Architecture: x86_64_v3 Requirement

The AMD/Intel 64-bit build now targets the x86_64_v3 microarchitecture level. This requires:
- AVX, AVX2
- BMI1, BMI2
- FMA
- LZCNT, MOVBE
- XSAVE

Minimum hardware: Intel Haswell (2013) or AMD Excavator (2015) and newer.

Check support: `ld.so --help`

Other architectures:
- ARM 64-bit (ARMv8.0-A)
- IBM Power (POWER9)
- IBM Z (z14)

## Display: Xorg Removed, Wayland Only

`xorg-x11-server-Xorg` is no longer packaged. Wayland is the sole display server.

For legacy X11 applications, `xorg-x11-server-Xwayland` provides a compatibility layer running X11 apps within a Wayland session.

## Desktop Applications: Flatpak Model

GIMP, LibreOffice, and Inkscape are no longer in the base repositories. RHEL/CentOS is transitioning to providing desktop apps via Flatpak.

Options for users:
1. Install from [Flathub](https://flathub.org/)
2. Request packages in [EPEL](https://docs.fedoraproject.org/en-US/epel/epel-package-request/)

## Redis -> Valkey

Redis was removed due to its license change from BSD-3-Clause to RSALv2/SSPLv1. Valkey 7.2, a BSD-licensed fork, is the replacement. It is API-compatible and a drop-in replacement.

## Modularity Removed

CentOS Stream 9 used "modularity" to provide optional alternative versions of software (e.g., multiple Python or Node.js versions). CentOS Stream 10 drops this entirely in favor of traditional non-modular RPM packages. Alternative versions will be added as standard AppStream packages over time.

## Repositories

- **BaseOS**: Core OS packages, full lifecycle
- **AppStream**: Additional applications, runtimes, databases (some with shorter lifecycles per RHEL Application Stream policy)
- **CRB** (CodeReady Builder): Development packages, disabled by default

Package management: DNF 4.20, RPM 4.19.

## Lifecycle

Maintained until ~2030, contingent on end of RHEL 10 Full Support phase.

## Secureboot

At launch, secureboot was broken. Resolved in the 2025-07-07 update.
