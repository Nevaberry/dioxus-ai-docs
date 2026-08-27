# Stores, Builds, Transports, and Caches

## Store durability and garbage collection

### Durable registration

`fsync-store-paths = true` makes Nix durably write a new store path before
registering it as valid (2.25.0). It defaults to `false`; enable it when the
additional I/O is justified by crash and power-loss resilience.

### Runtime roots and tolerant collection

`nix store roots-daemon` serves runtime GC roots over a Unix socket (2.34.0),
allowing collection when the main daemon cannot scan `/proc` because it lacks
`CAP_SYS_PTRACE`. Select it with the store's `use-roots-daemon` setting. That
setting and `ignore-gc-delete-failure`, which warns and continues past paths an
unprivileged process cannot remove, require the experimental
`local-overlay-store` feature.

Since 2.35.2, use:

```sh
nix store delete --recursive --skip-alive PATH
```

This removes only dead paths in the argument closure. `--skip-live` is an
alias; add `--also-referrers` to make referrers eligible too.

### Chroot stores

The evaluator sees the union of host and chroot `/nix/store` contents since
2.27.0, so host inputs and `builtins.path`/`builtins.filterSource` remain usable
with a chroot store.

In 2.35.2, a local chroot store derives its default daemon socket from the
store's `state` directory. For `nix-daemon --store /foo/bar`, the default is
`/foo/bar/nix/var/nix/daemon-socket/socket`. Preserve another location with
`nix daemon --socket-path ...` and connect with a matching `unix://` store URL.

## Build execution and sandboxing

### Build directories and CPU allocation

Temporary build directories moved below the Nix state directory in 2.30.0.
`build-dir` defaults to `builds` under `$NIX_STATE_DIR`, normally
`/nix/var/nix/builds`, rather than following `$TMPDIR` or using `/tmp`.
Directory names became opaque in 2.32.0 and no longer contain derivation names;
monitoring must not infer build identity from a directory basename.

`build-cores = 0` performs automatic CPU detection from 2.31.0 and exports the
detected value as `NIX_BUILD_CORES`, matching an unset setting rather than
passing a literal zero.

### External and unprivileged builders

The experimental `external-builders` setting in 2.32.0 delegates selected
system types to helper programs, for example to build through QEMU.

On Linux, `libexec/nix-nswrapper` can run the daemon with full sandboxing in an
unprivileged user namespace (2.34.0). Allocate its build-user IDs in both
`/etc/subuid` and `/etc/subgid`; Nixpkgs exposes `nix.daemonUser` and
`nix.daemonGroup` to support this arrangement.

The Linux sandbox returns `ENOTSUP` for `listxattr`, `llistxattr`, and
`flistxattr` as of 2.35.2. Builds must not enumerate host extended attributes,
including `security.selinux`.

### Build and post-build hooks

Because separately packaged `libnixstore` cannot locate the Nix binary
directory (2.25.0), remote-build applications must put Nix executables on
`PATH` or set `build-hook` explicitly.

Nix sends `SIGTERM`, not `SIGKILL`, when ending a build hook in 2.35.2, so a
hook can trap termination and clean up. `post-build-hook` also runs
asynchronously with up to `max-jobs` concurrent instances. Dependent builds
wait for their own hook; hook implementations must still be overlap-safe.

### Import-from-derivation visibility

Set `trace-import-from-derivation = true` to warn for every IFD without
disabling it (2.30.0). This supports staged removal while
`allow-import-from-derivation` remains enabled.

## Copying, substitution, and signatures

### Roots created during copy

`nix copy` accepts `--profile` and `--out-link` since 2.26.0. The profile
points to the top-level copied path; output links point to top-level copied
paths. Creating the root during the copy closes the race with concurrent GC.

### No mixed incomplete closures

Since 2.30.0, Nix does not combine a partially available substituted closure
with local builds for missing references. Configure an overlay substituter
together with every underlying cache or expect additional local builds.

```ini
substituters = https://overlay.example https://cache.nixos.org
```

`nix flake check` may avoid realizing a checked derivation when a substituter
has it (2.32.0); success does not imply every output is in the local store.

### Multiple signing keys

The `secret-keys` store-URI parameter accepts a comma-separated list of key
files as of 2.29.0, allowing paths to receive old and new signatures during
key rotation.

## HTTP and HTTPS transport

### TLS verification and authentication

The `builtin:fetchurl` derivation builder (`<nix/fetchurl.nix>`) verifies TLS
certificates from 2.25.0 onward. Invalid-certificate servers fail; this is
separate from evaluation-time `builtins.fetchurl`.

HTTPS substituter URLs support client-certificate authentication in 2.34.0 via
`tls-certificate` and `tls-private-key`. Keep both paths outside the store.

HTTP 401 and 407 responses from binary caches are authentication failures as
of 2.35.2, not missing paths. HTTP 403 retains missing-object behavior for
unlistable S3 buckets.

### Timeouts, retries, and HTTP/3

`connect-timeout` defaults to five seconds starting in 2.29.0; override it for
slow or intermittently reachable substituters.

In 2.35.2, transfer logic honors `Retry-After`, treats 429 and 503 as
rate-limited, and supports full-jitter backoff through:

- `filetransfer-retry-delay`
- `filetransfer-retry-delay-rate-limited`
- `filetransfer-retry-max-delay`
- `filetransfer-retry-jitter`
- `filetransfer-retry-attempts` (`download-attempts` is its compatibility alias)

HTTP and S3 store URLs can override equivalent `retry-*` parameters per
substituter. `http3 = true` or `--http3` requests HTTP/3 with fallback to
HTTP/2 or HTTP/1.1; it is silently ignored if Nix's libcurl lacks HTTP/3.

### Content encoding

HTTP cache stores can compress `.narinfo`, `.ls`, and build-log uploads from
2.32.0 using `narinfo-compression`, `ls-compression`, and `log-compression`.
They advertise `Content-Encoding`, which compatible clients decode.

In 2.34.0, accepted encodings follow linked libcurl capabilities: `gzip`,
deprecated `x-gzip`, `deflate`, `br`, and `zstd` can be supported. Nonstandard
`xz` and `bzip2` encodings are rejected. Distribution builders must link
libcurl with every codec they intend to expose.

### Cache metadata lifetime and logs

`narinfo-cache-meta-ttl` controls how long `/nix-cache-info` remains cached
locally (2.34.0); the default is seven days. `nix store info --refresh` forces
a new validity check.

`json-log-path` mirrors every Nix log event as JSON to a file or Unix-domain
socket (2.30.0):

```ini
json-log-path = /var/log/nix.json
```

## SSH transports

`NIX_SSHOPTS` receives shell-style space and quote parsing since 2.26.0, so
quoted proxy commands work consistently. Git LFS over SSH also honors it in
2.31.0, together with URL ports and the API endpoint returned by
`git-lfs-authenticate`.

SSH store URIs accept explicit ports for hostnames, IPv4, and bracketed IPv6
in 2.31.0:

```text
ssh://user@example.com:2222
ssh-ng://[b573:6a48:e224:840b:6007:6275:f8f7:ebf3]:22
```

In scoped IPv6 URIs, encode the zone separator `%` as `%25`; literal `%` is no
longer accepted.

## S3 stores and caches

### Credentials

The S3 client supports STS profile credentials from 2.29.0, including sessions
created by `aws sso login`.

Nix 2.34.2 restores WebIdentity credentials used by EKS IRSA, GitHub Actions
OIDC, and other `AssumeRoleWithWebIdentity` flows, as well as ECS metadata
credentials used by ECS tasks and EKS Pod Identity. Configure
`AWS_WEB_IDENTITY_TOKEN_FILE` and its role variables, or
`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` / `_FULL_URI` respectively.

### Curl transport and multipart uploads

S3 cache traffic uses curl SigV4 in 2.33.0. Authenticated operation needs curl
7.75.0 or newer plus `aws-crt-cpp`; builds without `aws-crt-cpp` can access
only public buckets. Existing URLs remain valid, but multipart configuration is:

- `multipart-upload`, default `false`
- `multipart-threshold`, default 100 MiB
- `multipart-chunk-size`, default and minimum 5 MiB

`buffer-size` is an alias for `multipart-chunk-size`.

### Object identity and storage

S3 URLs can pin a versioned object with `versionId` (2.33.0). Binary-cache
stores accept `storage-class` for regular and multipart uploads; omitting it
uses the bucket default.

### Addressing styles

S3 stores default to `addressing-style=auto` in 2.34.0. Standard AWS endpoints
use virtual-hosted URLs; custom endpoints and dotted bucket names use path
style. `path` forces deprecated path style. `virtual` forces virtual-hosted
style and is invalid for dotted bucket names.

## Content-addressed build traces

The experimental content-addressed derivation feature in 2.35.2 replaces
realisations with build traces. `nix realisation` becomes
`nix store build-trace`. Trace identity is derivation store path plus output
name, and only resolved derivations are recorded.

Cache objects move from `realisations/<hash>!<output>.doi` to
`build-trace-v2/<drvName>/<outputName>.doi`. JSON splits into `key` and `value`
and drops `dependentRealisations`:

```json
{
  "key": { "drvPath": "abc...-foo.drv", "outputName": "out" },
  "value": { "outPath": "xyz...-foo", "signatures": [] }
}
```

Build traces use the same structured signature objects as
`nix path-info --json --json-format 3`.

## Protocol compatibility

Nix 2.32.0 drops daemon worker-protocol peers older than Nix 2.0 (protocol
version 18). Upgrade both sides before mixing a 2.32 client or daemon with a
pre-2.0 peer.
