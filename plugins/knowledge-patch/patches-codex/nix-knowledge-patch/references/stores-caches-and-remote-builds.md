# Stores, Caches, and Remote Builds

## Local and chroot stores

### Explicit build-hook discovery (since 2.25.0)

Separately packaged `libnixstore` no longer provides a useful default path to
the Nix binary directory. Applications linking it and using remote builds must
put Nix executables on `PATH` or set `build-hook` explicitly. The Perl
bindings no longer expose `getBinDir`.

### Durable path registration (since 2.25.0)

`fsync-store-paths = true` durably writes new store paths before registering
them as valid, reducing corruption after power loss or a crash. It defaults to
`false`.

### Host paths visible in chroot stores (since 2.27.0)

An evaluator using a chroot store sees the union of host and chroot
`/nix/store` contents. Host-store inputs remain accessible, and
`builtins.path` plus `builtins.filterSource` work in chroot stores.

### Runtime roots daemon (since 2.34.0)

`nix store roots-daemon` serves runtime GC roots over a Unix socket, avoiding
`/proc` scanning when the main daemon lacks `CAP_SYS_PTRACE`. Select it with
`use-roots-daemon`; this and tolerant GC require the experimental
`local-overlay-store` feature.

### Tolerant garbage collection (since 2.34.0)

The experimental local-store setting `ignore-gc-delete-failure = true` warns
and continues when an unprivileged process cannot delete a path.

### Unprivileged namespace wrapper (since 2.34.0)

On Linux, `libexec/nix-nswrapper` can run the daemon with full sandboxing in
an unprivileged user namespace. Allocate its build-user IDs in `/etc/subuid`
and `/etc/subgid`; Nixpkgs exposes `nix.daemonUser` and `nix.daemonGroup` for
the setup.

### Chroot-store daemon sockets (since 2.35.2)

A local chroot store derives its default daemon socket from the store's
`state` directory. For `nix-daemon --store /foo/bar`, the socket is
`/foo/bar/nix/var/nix/daemon-socket/socket`. Preserve another location with
`nix daemon --socket-path ...` and connect with the matching `unix://` URL.

### Sandbox xattr behavior (since 2.35.2)

The Linux sandbox returns `ENOTSUP` for `listxattr`, `llistxattr`, and
`flistxattr`, matching other xattr calls. Builds cannot enumerate host
extended attributes such as `security.selinux`.

### Selective recursive deletion (since 2.35.2)

`nix store delete --recursive --skip-alive` deletes only dead paths in an
argument's closure; `--skip-live` is an alias. Add `--also-referrers` to make
referrers eligible too.

## Roots, copies, signing, and closures

### Root paths during copy (since 2.26.0)

`nix copy` accepts `--profile` for one top-level copied path and `--out-link`
for links to top-level copied paths. Creating roots during the copy closes the
window in which concurrent GC could delete a result.

### Multiple signing keys (since 2.29.0)

The `secret-keys` store-URI parameter accepts a comma-separated file list, so
a copy can sign paths with multiple keys during rotation.

```text
file:///tmp/store?secret-keys=/tmp/key1,/tmp/key2
```

### Incomplete substituted closures (since 2.30.0)

Nix does not combine a partially available substituted closure with local
builds for its missing references. Configure an overlay cache together with
the underlying cache or clients may build more paths locally.

## SSH stores

### Shell-style `NIX_SSHOPTS` (since 2.26.0)

`NIX_SSHOPTS` parses spaces and quotes with shell-like rules, so quoted proxy
commands work consistently across SSH-backed Nix commands.

### Ports in store URIs (since 2.31.0)

SSH and SSH-ng store references accept ports with hostnames, IPv4, and
bracketed IPv6 addresses.

```text
ssh://user@example.com:2222
ssh-ng://[b573:6a48:e224:840b:6007:6275:f8f7:ebf3]:22
```

### Scoped IPv6 URI syntax (since 2.31.0)

Encode a scoped IPv6 zone separator `%` as `%25`, for example
`[fe80::1%2518]`. Literal-percent forms are invalid.

## HTTP caches and transfers

### Builtin fetcher TLS verification (since 2.25.0)

The `<nix/fetchurl.nix>` `builtin:fetchurl` derivation builder verifies TLS
certificates, so invalid HTTPS certificates fail. This is distinct from the
evaluation-time `builtins.fetchurl` behavior.

### Connection timeout default (since 2.29.0)

`connect-timeout` defaults to five seconds rather than unlimited. Override it
for caches that legitimately establish connections more slowly.

### Compressed cache metadata and logs (since 2.32.0)

HTTP stores can compress `.narinfo`, `.ls`, and build-log uploads with
`narinfo-compression`, `ls-compression`, and `log-compression`. The HTTP
`Content-Encoding` header advertises the codec for transparent decompression.

### Cache metadata lifetime (since 2.34.0)

`narinfo-cache-meta-ttl` controls how long `/nix-cache-info` is cached, in
seconds; the default is seven days. `nix store info --refresh` forces a new
cache-validity check.

### HTTPS client certificates (since 2.34.0)

HTTPS substituter URLs accept `tls-certificate` and `tls-private-key` for
mutual TLS.

### Supported content encodings (since 2.34.0)

HTTP decompression follows linked libcurl capabilities. `deflate` and the
deprecated `x-gzip` alias join `br`, `zstd`, and `gzip`; nonstandard `xz` and
`bzip2` encodings are rejected. Distribution builds must link libcurl with
the desired codec libraries.

### Optional HTTP/3 (since 2.35.2)

Set `http3 = true` or pass `--http3` to request HTTP/3 with fallback to
HTTP/2 or HTTP/1.1. Nix silently ignores it when libcurl lacks HTTP/3 support.

### Retry policy (since 2.35.2)

Transfers honor `Retry-After`, treat HTTP 429 and 503 as rate-limited, and
support full-jitter backoff through `filetransfer-retry-delay`,
`filetransfer-retry-delay-rate-limited`, `filetransfer-retry-max-delay`, and
`filetransfer-retry-jitter`. `download-attempts` aliases
`filetransfer-retry-attempts`; HTTP and S3 URIs accept per-store `retry-*`
overrides.

### Authentication status codes (since 2.35.2)

HTTP 401 and 407 from binary caches are authentication errors, not missing
objects. Only 403 retains the missing-object behavior required for unlistable
S3 buckets.

## S3 binary caches

### Credential providers (since 2.29.0, 2.34.0)

S3 caches support STS profile credentials, including credentials produced by
`aws sso login`. Nix 2.34.2 restores STS WebIdentity for EKS IRSA and OIDC
`AssumeRoleWithWebIdentity` workflows plus ECS metadata credentials for ECS
tasks and EKS Pod Identity. Use `AWS_WEB_IDENTITY_TOKEN_FILE` and role variables, or
`AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` /
`AWS_CONTAINER_CREDENTIALS_FULL_URI`.

### Multipart uploads (since 2.33.0)

S3 traffic uses curl SigV4. Authenticated use requires curl 7.75.0 or later
and `aws-crt-cpp`; builds without it can read only public buckets. The store
parameters are `multipart-upload` (default `false`), `multipart-threshold`
(default 100 MiB), and `multipart-chunk-size` (default/minimum 5 MiB).
`buffer-size` aliases `multipart-chunk-size`.

### Pinned objects and storage classes (since 2.33.0)

Use `versionId` to pin an object in a versioned bucket. `storage-class`
selects the class for regular and multipart uploads; when omitted, the bucket
default applies.

### Addressing style (since 2.34.0)

`addressing-style=auto` uses virtual-hosted URLs for standard AWS endpoints
and path-style URLs for custom endpoints or dotted bucket names. `path`
forces the deprecated path form. `virtual` cannot be used with dotted bucket
names.

## Hooks and content-addressed traces

### Graceful build-hook termination (since 2.35.2)

Nix terminates `build-hook` with `SIGTERM`, not `SIGKILL`. Hooks can trap the
signal and clean up.

### Concurrent post-build hooks (since 2.35.2)

`post-build-hook` runs asynchronously with up to `max-jobs` instances.
Dependent builds wait for their instance, but hook implementations must be
safe when instances overlap.

### Build traces replace realisations (since 2.35.2)

The experimental content-addressed derivation feature keys build traces by
derivation path and output name and records only resolved derivations. `nix
realisation` is renamed to `nix store build-trace`; cache entries move from
`realisations/<hash>!<output>.doi` to
`build-trace-v2/<drvName>/<outputName>.doi`. JSON is split into `key` and
`value`, `dependentRealisations` is removed, and signatures use structured
objects.
