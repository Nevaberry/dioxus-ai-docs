# Runtime and Desktop Transitions

Covered batches: `2.41`, `2025-h1-platform`, and `2025-q4-interventions`.

## Application and runtime compatibility

### Upgrade Discord after glibc 2.41

After upgrading to glibc 2.41, Discord versions older than `0.0.84-1` report a corrupt installation and may lose audio connectivity, although written chat continues to work.

Upgrade Discord to `0.0.84-1` or newer. Until then, use Discord Canary, the browser client, or the Flatpak package when audio is required.

### Preserve required .NET 9 packages during the .NET 10 transition

The 9.0-to-10.0 upgrade can fail with unsatisfied dependencies for these unversioned packages:

- `aspnet-runtime`
- `aspnet-targeting-pack`
- `dotnet-runtime`
- `dotnet-sdk`
- `dotnet-source-built-artifacts`
- `dotnet-targeting-pack`

When version 9 is still required, install the corresponding `-9.0` package during the full system upgrade, then remove the unversioned package. For example:

```sh
pacman -Syu aspnet-runtime-9.0
pacman -Rs aspnet-runtime
```

Apply the same versioned-package pattern to each listed component still needed at version 9.

## Wine

### Recreate 32-bit prefixes for pure WoW64

Under batch `2025-h1-platform`, `wine` and `wine-staging` switch to pure WoW64 and no longer depend on `[multilib]`.

Recreate all existing 32-bit prefixes and reinstall their applications. Expect 32-bit applications that use OpenGL directly to potentially run more slowly.

## Plasma

### Install the split X11 session before Plasma 6.4

Plasma 6.4 installs only its Wayland session by default after `kwin` splits into `kwin-wayland` and `kwin-x11`.

Install `plasma-x11-session` before upgrading any workstation that must log into Plasma on X11. Without it, the X11 login session is unavailable after the upgrade.

## Waydroid

### Overwrite unowned bytecode left by old packages

Waydroid versions before `1.5.4-3` can leave unowned Python bytecode that conflicts with newly packaged files. If the full upgrade reports conflicting `.pyc` files below `/usr/lib/waydroid/tools/`, overwrite only the known cache-file pattern:

```sh
pacman -Syu --overwrite /usr/lib/waydroid/tools/\*__pycache__/\*
```

These stale cache files are safe to overwrite.

## NVIDIA graphics

### Move Pascal and older GPUs to the legacy driver

NVIDIA 590 drops support for Pascal (GTX 10xx), Maxwell, and older GPUs. At the same time, Arch replaces:

| Previous package | Open-module replacement |
|---|---|
| `nvidia` | `nvidia-open` |
| `nvidia-dkms` | `nvidia-open-dkms` |
| `nvidia-lts` | `nvidia-lts-open` |

For an affected Pascal, Maxwell, or older GPU, remove the official NVIDIA package and install `nvidia-580xx-dkms` from the AUR before the transition to avoid a broken graphical environment.

Allow Turing GPUs (20xx and GTX 1650) and newer to transition automatically; they do not need the legacy package.
