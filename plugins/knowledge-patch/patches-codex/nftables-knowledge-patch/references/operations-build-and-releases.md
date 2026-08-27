# Operations, builds, and releases

Use this reference for lifecycle commands, listings, diagnostics, source builds,
packaging, bindings, and release verification.

## Idempotent removal (1.1.6-guide)

`destroy` commands exist for tables, chains, rules, sets, maps, elements,
flowtables, and named stateful objects. They do not fail when the target is
absent:

```nft
destroy table inet stale
destroy element inet filter blocked { 192.0.2.1 }
```

Prefer `destroy` for convergent cleanup. Use `delete` when a missing object
should remain an error.

## Table ownership and dormancy (1.1.6-guide)

The `owner` flag prevents processes other than the owner from modifying a table.
The table normally disappears when the owner exits; `persist` keeps the
orphaned table available for a later owner.

The `dormant` flag unregisters the table's base chains. Add the existing table
again without `dormant` to reactivate it:

```nft
add table inet managed { flags owner, persist; }
add table inet maintenance { flags dormant; }
add table inet maintenance
```

## Rule placement under concurrency (1.1.6-guide)

Rule indexes are zero-based and resolved to handles in userspace before the
request reaches the kernel. Concurrent insertion or deletion can change what an
index identifies.

At a resolved location, `add` places the new rule after it, while `insert`
places the new rule before it. Prefer handles when stable concurrent placement
matters.

## Listing syntax and normalized output (1.1.2, 1.1.4)

The table-scoped short form is accepted:

```console
nft list sets inet foo
```

Older installations may require `list sets table inet foo`.

Listings preserve dependencies such as `meta nfproto` and order
`meta l4proto` before raw transport payload access. Complex set elements with
mappings, timeouts, comments, counters, quotas, or limits appear on one line.
Set listings show an element count beside the configured size, and hook device
names are quoted.

Treat these as normalization changes, not semantic ruleset differences.

## Diagnostics and operational context (1.1.2, 1.1.5)

Extended netlink errors for large set elements retain their correct source
locations. Both text and JSON commands fail when the requested table does not
exist. Include paths are canonicalized to avoid duplicate inclusion through
equivalent names.

Netlink batches continue after `ENOBUFS`. Retain the error context even when
processing continues.

The `route_localnet` sysctl is an explicit operational dependency. Inspect the
host value when rules depend on local-route behavior.

## Source dependencies and archives (1.1.2, 1.1.4)

Release archives use `.tar.xz`.

Build requirements:

- nftables 1.1.2 requires libnftnl 1.2.9 or newer and libmnl 1.0.4 or newer;
- nftables 1.1.4 requires libnftnl 1.3.0 or newer and libmnl 1.0.4 or newer.

## Build and systemd behavior (1.1.5, 1.1.6)

Installation of the upstream static-ruleset systemd unit is disabled by default.
Enable a unit directory explicitly:

```console
./configure --with-unitdir
```

Ancillary systemd files are not installed when the service file is not
installed. The source build supports `make check` and honors command-line
`CFLAGS`.

## Python bindings (1.0.6.1)

The Python bindings use a `src` layout, setuptools configuration, and
`pyproject.toml`. Distutils and the old autotools-integrated `setup.py` path are
removed. Install with a PEP 517-capable frontend instead of invoking `setup.py`
through autotools.

## Removed protocol support (1.0.6.1)

DECnet support is removed. Rulesets using DECnet-specific constructs must be
redesigned before migration.

## Release ordering and support claims (release-lifecycle)

The release index labels 1.0.6.1 as `stable`. Its publication after 1.1.5 and
before 1.1.6 means numerical version sorting does not reproduce publication
order. The index does not state a broader support lifetime or end-of-life
policy; do not infer one from the stable label.

## Artifact verification (release-lifecycle)

The release index pairs every tarball with a GPG signature and SHA-256 digest.
The listed digests for the newest and separately stable-labelled artifacts are:

```text
nftables-1.1.6.tar.xz    372931bda8556b310636a2f9020adc710f9bab66f47efe0ce90bff800ac2530c
nftables-1.0.6.1.tar.xz  bef0c9cfdca5f8b988957046c2cb33ef9869730593da0eacae4748201acf1116
```

Verify both the release-specific signature and digest before using a published
archive.
