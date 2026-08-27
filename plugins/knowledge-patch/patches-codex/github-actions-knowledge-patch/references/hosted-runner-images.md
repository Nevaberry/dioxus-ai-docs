# Hosted Runner Images

## Windows Server 2025 with Visual Studio 2026

The dedicated `windows-2025-vs2026` label provides a public-preview validation
path alongside `windows-2025`. Its migration into `windows-2025` was scheduled
to start June 8, 2026. Use the dedicated label when validating Visual Studio
2026 explicitly, and verify image status before treating the toolchain as
stable.

```yaml
jobs:
  validate:
    runs-on: windows-2025-vs2026
    steps:
      - run: echo test
```

## macOS 26 on Intel

The public-preview macOS 26 Intel image is available to larger runners under
`macos-26-large`. Select it when Intel architecture is part of the test target;
do not infer architecture from the macOS release alone.

```yaml
jobs:
  intel-test:
    runs-on: macos-26-large
    steps:
      - run: uname -a
```

## M2 macOS larger runners

M2-powered macOS runners are generally available under these labels:

- `macos-latest-xlarge`
- `macos-15-xlarge`
- `macos-14-xlarge`
- `macos-13-xlarge`

Use a release-specific label when image movement would harm reproducibility;
use `macos-latest-xlarge` only when following the latest M2 image is intended.

```yaml
jobs:
  build:
    runs-on: macos-15-xlarge
    steps:
      - run: uname -m
```
