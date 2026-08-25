# Build, Packaging, and Releases

## Native build dependencies

Release archives use `.tar.xz` beginning with 1.1.2.

The native-library minimums are release-specific:

| nftables release | libnftnl | libmnl |
| --- | --- | --- |
| 1.1.2 | 1.2.9 or newer | 1.0.4 or newer |
| 1.1.4 | 1.3.0 or newer | 1.0.4 or newer |

The 1.1.6 build supports `make check` and honors command-line `CFLAGS`.

## systemd installation

The upstream static-ruleset systemd unit is available in 1.1.5, but its
installation is opt-in. Supply a unit directory when the build should install
it:

```console
./configure --with-unitdir
```

In 1.1.6, ancillary systemd files are not installed when the service file
itself is not installed.

## Python bindings

The Python bindings use a `src` layout, setuptools configuration, and
`pyproject.toml` as of 1.0.6.1. Distutils and the old autotools-integrated
`setup.py` route were removed. Install with a PEP 517-capable frontend rather
than invoking `setup.py` through autotools.

## Release selection and support claims

The release-lifecycle index labels 1.0.6.1 as `stable`, even though it was
published on 2025-09-02 between 1.1.5 and 1.1.6. Do not infer publication order
from version-number sorting alone. The index makes no broader support-lifetime
or end-of-life commitment.

## Artifact verification

The release-lifecycle index pairs each tarball with a GPG signature and a
SHA-256 digest. Its verification values for the newest listed release and the
separately stable-labelled release are:

```text
nftables-1.1.6.tar.xz    372931bda8556b310636a2f9020adc710f9bab66f47efe0ce90bff800ac2530c
nftables-1.0.6.1.tar.xz  bef0c9cfdca5f8b988957046c2cb33ef9869730593da0eacae4748201acf1116
```

Verify both the signature and the release-specific digest; do not substitute a
digest from a differently labelled archive.

