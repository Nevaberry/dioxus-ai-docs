# Hosted runner images

Use this reference when selecting Windows or macOS hosted-runner labels and
validating architecture-sensitive builds.

## Windows Server 2025 with Visual Studio 2026

The dedicated `windows-2025-vs2026` hosted-runner image provides a
public-preview validation path alongside `windows-2025`.

```yaml
jobs:
  validate:
    runs-on: windows-2025-vs2026
    steps:
      - run: echo test
```

Migration of this image into `windows-2025` was scheduled to begin June 8,
2026. Keep an explicit label while isolating Visual Studio 2026 validation,
and reassess image assumptions as that migration proceeds.

## macOS 26 Intel larger runners

The public-preview macOS 26 Intel image is available to larger runners under
the `macos-26-large` label.

```yaml
jobs:
  intel-test:
    runs-on: macos-26-large
    steps:
      - run: uname -a
```

Use the explicit Intel label when architecture affects native dependencies,
build products, or test behavior.

## M2 macOS larger runners

M2-powered macOS larger runners are generally available under:

- `macos-latest-xlarge`
- `macos-15-xlarge`
- `macos-14-xlarge`
- `macos-13-xlarge`

```yaml
jobs:
  build:
    runs-on: macos-15-xlarge
    steps:
      - run: uname -m
```

Choose a versioned label when image drift matters. Use
`macos-latest-xlarge` only when following the moving latest image is
intentional.
