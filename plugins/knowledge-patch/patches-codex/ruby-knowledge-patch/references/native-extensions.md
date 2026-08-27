# Native Extensions and Platform Builds

## Replace removed allocation and GC APIs

Native extensions must replace these removed interfaces (since 3.4.0):

- `rb_newobj`
- `rb_newobj_of`
- their allocation macros
- `rb_gc_force_recycle`

Use supported allocation and lifetime APIs appropriate to the extension's
object type rather than retaining compatibility shims for the removed calls.

## Close descriptors through IO

`rb_thread_fd_close` is deprecated and is now a no-op (since 4.0.0).
Extensions that expose a descriptor should create an `IO` with
`RUBY_IO_MODE_EXTERNAL`, then close it with `rb_io_close`. Closing this way
interrupts and waits for pending operations.

`rb_thread_call_with_gvl` can be called whether or not its caller already holds
the GVL.

## Use the Set C API

The Set C API provides these functions (since 4.0.0):

- `rb_set_foreach`
- `rb_set_new`
- `rb_set_new_capa`
- `rb_set_lookup`
- `rb_set_add`
- `rb_set_clear`
- `rb_set_delete`
- `rb_set_size`

The obsolete `$SAFE` path-checking function `rb_path_check` is removed.

## Update Windows build tooling

Windows builds require Visual Studio 2015 or newer (since 4.0.0). MSVC
versions older than 14.0 are unsupported.

