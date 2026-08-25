# Extensions, Builds, and Packaging

## Removed and deprecated Ruby interfaces

### Refinements, DidYouMean, and Net::HTTP

The following interfaces are removed since 3.4.0:

- `Refinement#refined_class`
- Mutation through `DidYouMean::SPELL_CHECKERS`
- Deprecated Net::HTTP proxy, response-code, and receiver constants

### ObjectSpace and process status

Since 4.0.0, `ObjectSpace._id2ref` is deprecated, while
`Process::Status#&` and `Process::Status#>>` are removed.

## Native-extension compatibility

### Allocation and recycling APIs

Since 3.4.0, native extensions must replace:

- `rb_newobj`
- `rb_newobj_of`
- their allocation macros
- `rb_gc_force_recycle`

### Descriptor close and GVL contracts

Since 4.0.0, `rb_thread_fd_close` is deprecated and is a no-op. An extension
that exposes a file descriptor should:

1. Create an `IO` with `RUBY_IO_MODE_EXTERNAL`.
2. Close it with `rb_io_close`.

`rb_io_close` interrupts and waits for pending operations.

`rb_thread_call_with_gvl` can be called whether or not the caller already holds
the GVL.

### Set C API and path checking

The Set C API is available since 4.0.0:

- `rb_set_foreach`
- `rb_set_new`
- `rb_set_new_capa`
- `rb_set_lookup`
- `rb_set_add`
- `rb_set_clear`
- `rb_set_delete`
- `rb_set_size`

The obsolete `$SAFE` path-checking function `rb_path_check` is removed.

## Platform build requirements

Since 4.0.0, Windows builds require Visual Studio 2015 or newer. MSVC versions
older than 14.0 are unsupported.

Building the experimental ZJIT requires Rust 1.85.0 or newer. Building the
experimental MMTk garbage collector also requires Rust.

## Package integrity

Since 3.4.0, `gem push` accepts `--attestation` to store a build-artifact
signature with Sigstore.

Bundler can add checksums when creating lockfiles by enabling
`lockfile_checksums`, or add them to an existing lockfile:

```sh
bundle config set lockfile_checksums true
bundle lock --add-checksums
```
