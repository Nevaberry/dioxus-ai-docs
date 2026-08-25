# Hosted Runner Images

Use this reference when a workflow needs Windows Server 2025 with Visual
Studio 2026, an Intel macOS 26 larger runner, or an M2 macOS larger runner.
Preview labels and architecture choices should be explicit in workflow review.

## Windows Server 2025 with Visual Studio 2026

The dedicated `windows-2025-vs2026` image is a public-preview validation path
alongside `windows-2025`. Its migration into `windows-2025` was scheduled to
start June 8, 2026. Keep the dedicated label when validation must explicitly
target the preview image, and check migration status before assuming the two
labels select identical contents.

```yaml
jobs:
  validate:
    runs-on: windows-2025-vs2026
    steps:
      - run: echo test
```

## macOS 26 on Intel

The public-preview macOS 26 Intel image is available for larger runners under
the `macos-26-large` label. Use it when the Intel architecture is intentional;
do not infer M2 behavior from this label.

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

Choose a version-specific label when the operating-system version matters;
use `macos-latest-xlarge` only when following the moving latest image is
acceptable.

```yaml
jobs:
  build:
    runs-on: macos-15-xlarge
    steps:
      - run: uname -m
```
