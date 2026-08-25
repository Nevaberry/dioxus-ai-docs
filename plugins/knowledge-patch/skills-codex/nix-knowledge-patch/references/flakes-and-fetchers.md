# Flakes and Fetchers

## Input declarations and lock files

### Relative repository inputs (since 2.26.0)

A flake can reference another flake in its repository with
`inputs.foo.url = "path:./foo";`. This changes the lock-file format; older Nix
versions cannot read locks containing relative-path inputs.

### Reproducible registry resolution (since 2.26.0, 2.33.0)

Lock generation for indirect references ignores system and user registries.
It uses the global registry and command-line `--override-flake` values, so set
input URLs explicitly when reproducibility matters. `nix registry resolve
nixpkgs` prints the resolved flake reference without fetching or evaluation.

### Channel tarballs as flake inputs (since nixos-25.05)

The channel server implements the Lockable HTTP Tarball Protocol. A URL such
as `https://channels.nixos.org/nixos-25.05/nixexprs.tar.xz` can be used
directly as a lockable flake input.

### Source information for non-flake inputs (since 2.30.0)

Inputs with `flake = false` expose their parent source's `sourceInfo`, keeping
the containing source distinct from an input below it. Select a subdirectory
with `?dir=subdir`.

### Nested lock preservation (since 2.31.0)

When an input reference changes during lock update, Nix consults that input's
own lock file for nested inputs instead of fetching their latest versions.

## Git-backed inputs

### Self-declared submodules (since 2.27.0)

A Git flake can set `inputs.self.submodules = true`; callers no longer need to
add `submodules = true` themselves.

### Git LFS materialization (since 2.27.0, 2.31.0)

Set `inputs.self.lfs = true` or add `lfs=1` to a Git URL to materialize LFS
objects. LFS-over-SSH honors `NIX_SSHOPTS`, uses the URL port, and follows the
`git-lfs-authenticate` response when the API endpoint is not on port 443.

### SHA-256 Git hashing (since 2.31.0)

Experimental Git-hashed store objects support SHA-256 as well as SHA-1.

### SCP-like Git URLs (since 2.35.2)

`builtins.fetchGit` and Git `builtins.fetchTree` inputs accept SCP-like URLs,
including verbatim `~` paths and bracketed IPv6 hosts.

```nix
builtins.fetchGit "host:~/relative/to/home"
builtins.fetchTree { type = "git"; url = "user@[::1]:~/repo"; }
```

### GitHub parameter validation (since 2.35.2)

The `github:` fetcher rejects unknown URL parameters instead of ignoring them;
for example, `tag` is invalid.

## Prefetch, show, check, archive, and clone

### Prefetch output links (since 2.27.0)

`nix flake prefetch --out-link ./result REF` creates an output link for the
prefetched result.

### Partial `flake show` around IFD (since 2.29.0)

`nix flake show` skips outputs requiring import-from-derivation and continues
showing the rest instead of failing the whole command.

### Archive without signature checks (since 2.30.0)

`nix flake archive --no-check-sigs` permits a direct copy to a remote store
that would otherwise reject the operation during signature verification.

### Parallel input prefetch (since 2.31.0)

`nix flake prefetch-inputs .` fetches all flake inputs in parallel. It avoids
serialized evaluation-time fetches but may fetch inputs evaluation would not
use.

### Check realization behavior (since 2.32.0)

If a derivation is substitutable, `nix flake check` may leave it unrealized
locally. A successful check does not imply every checked output is in the
local store.

### Clone non-Git inputs (since 2.33.0)

`nix flake clone` supports arbitrary input types, including tarball-backed
flakes and tarball flakes hosted on FlakeHub.

### Check output paths and links (since 2.35.2)

`nix flake check` accepts `--print-out-paths` and `--out-link`. Without
`--out-link`, it creates no output links.

## URL compatibility

### Built-in channel hostname (since 2.33.0)

Persisted channel URLs and allowlists should use
`https://channels.nixos.org/`; the old `https://nixos.org/channels/` location
redirects but that compatibility redirect may be retired.

### Absolute `file:` tarball paths (since 2.34.0)

Tarball references using the `file:` scheme must contain absolute paths.
Relative forms are rejected as ambiguous.
