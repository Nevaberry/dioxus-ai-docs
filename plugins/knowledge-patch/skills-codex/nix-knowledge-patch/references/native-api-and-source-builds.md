# Native APIs and Source Builds

## Building Nix from source

### Meson and Ninja (since 2.26.0)

Nix uses Meson and Ninja; the Make-based build system was removed. Update
source-build automation and packaging to invoke the current build system.

## C++ consumers

### Namespaced headers and macros (since 2.28.0)

Include installed headers as `nix/<component>/...`. Pkg-config now supplies
`-I${includedir}` rather than a path ending in `/nix`. Configuration headers
need not be force-included, and remaining public configuration macros have the
`NIX_` prefix.

```cpp
#include <nix/store/derived-path.hh>
#include <nix/util/configuration.hh>

#if NIX_SUPPORT_ACL
// ...
#endif
```

## Evaluator and flake C APIs

### Builder-scoped flake settings (since 2.28.0)

`nix_flake_init_global` was removed. Add flake settings to each evaluator
state builder with `nix_flake_settings_add_to_eval_state_builder`.

```c
nix_eval_state_builder *builder = nix_eval_state_builder_new(ctx, store);
nix_flake_settings_add_to_eval_state_builder(ctx, settings, builder);
```

### Native flake loading and locking (since 2.29.0)

C consumers can load flakes and perform basic locking directly. Select lock
modes with `nix_flake_lock_flags_set_mode_check`, `_virtual`, or
`_write_as_needed`; `nix_flake_lock_flags_add_input_override` also enables
virtual mode. The `nix-fetchers-c` library manages `nix.conf` settings for
built-in fetchers.

### Mutable indexed access (since 2.32.0)

`nix_get_attr_name_byidx` and `nix_get_attr_byidx` accept mutable
`nix_value *`, because lookup may modify the value. The ABI remains compatible,
but const-correct source may need adjustment.

### Lazy collection access (since 2.32.0)

Use `nix_get_list_byidx_lazy`, `nix_get_attr_byname_lazy`, and
`nix_get_attr_byidx_lazy` to retrieve list or attribute-set members without
forcing them. This is useful when forwarding an unevaluated value into a
collection or function call.

### Sticky primop errors (since 2.34.0)

An error returned by a C primop is retained in its thunk, so forcing again
does not retry and later succeed. Mark intentionally retryable errors with
`NIX_ERR_RECOVERABLE`.

```c
nix_set_err_msg(context, NIX_ERR_RECOVERABLE, msg);
```

## Store C API and plugins

### Lookup and copy store paths (since 2.34.0)

`nix_store_query_path_from_hash_part()` resolves a hash part to a full store
path. `nix_store_copy_path()` copies a path between stores with repair and
signature-check controls.

### Dynamically resolved plugin symbols (since 2.35.2)

The `nix` executable exports its C-binding symbols. C API plugins may resolve
them dynamically instead of linking the corresponding `libnix*c.so`
libraries.
