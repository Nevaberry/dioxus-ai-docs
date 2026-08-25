# C API and extensions

## ctypes and native layouts

### ctypes metaclass and alignment (`whatsnew-3.13`)

Subclasses of ctypes internal metaclasses must move setup performed after
`super().__new__()` into `__init__`, and create classes by calling the metaclass
rather than its `__new__` directly. `ctypes.Structure._align_` sets explicit
packed-memory alignment.

### Explicit layouts and views (`whatsnew-3.14`)

`Structure._layout_` selects a non-default ABI. Platform bit-field layouts no
longer overlap, and relying only on `_pack_` for MSVC layout outside Windows is
deprecated. `memoryview_at()` exposes pointer-backed memory without copying;
public `CField` metadata supports layout inspection.

## Free-threading and subinterpreters

### Declaring GIL support (`whatsnew-3.13`)

Multi-phase modules declare no-GIL support with `Py_mod_gil`; single-phase
modules call `PyUnstable_Module_SetGIL()`. Importing an undeclared extension
normally re-enables the GIL unless it was explicitly forced off. Installing
extension packages in a free-threaded build requires pip 24.1 or newer.

### Windows build contracts (`whatsnew-3.14`)

Windows build backends targeting free-threaded extensions must define
`Py_GIL_DISABLED` themselves.

### Stable ABI for free-threaded extensions (`whatsnew-3.15`)

Target the free-threaded Stable ABI, `abi3t`, through a backend or
`Py_TARGET_ABI3T`. Unsupported APIs require separate `abi3` and `cp315t`
artifacts. `abi3t` uses opaque type data and `PyModExport_*` export hooks rather
than a traditional `PyInit_*` entry point.

### Finalization-safe interpreter access (`whatsnew-3.15`)

Interpreter guards, views, and attach/detach APIs let native threads use
interpreters that may be finalizing or concurrently deleted. The `PyGILState`
family is soft-deprecated without a removal plan; do not extend its use in new
code.

### C module ABI enforcement (`3.15.0b3`)

`Py_mod_abi` is mandatory for modules built from slot arrays or
`PyModExport_*`. Importing a non-free-threaded extension into a free-threaded
interpreter raises. On non-Windows free-threaded builds, defining
`Py_LIMITED_API` no longer also requires `Py_GIL_DISABLED`.

## References, errors, and iteration

### Reference ownership (`whatsnew-3.13`)

`PyModule_Add()` always steals its value reference.
`PyDict_GetItemRef()`, `PyList_GetItemRef()`, `PyImport_AddModuleRef()`, and
`PyWeakref_GetRef()` return strong references that callers own and release.

### Lookup APIs that preserve errors (`whatsnew-3.13`)

`PyObject_HasAttrWithError()` and `PyMapping_HasKeyWithError()`, including
string variants, return `-1` on error rather than clearing it. Older
error-suppressing lookup helpers report suppressed failures through
`sys.unraisablehook()`.

### Unambiguous iteration and integer interchange (`whatsnew-3.14`)

`PyIter_NextItem()` replaces the ambiguous `PyIter_Next()` end/error result. Fixed-width
`PyLong_As*` and `PyLong_From*`, `PyLong_Export()`, and `PyLongWriter_*()`
exchange native integers without private representation access.

### Deallocation and argument formats (`3.14.0`)

`Py_DECREF()` protects against deallocation stack overflow, so extension types
do not need trashcan machinery solely for this purpose. `k` and `K`
`PyArg_Parse()` formats accept `__index__()`. `Py_BuildValue()` adds `p` to
convert a C integer to `bool`.

## Types, modules, and public builders

### Allocation and monitoring hooks (`3.13.0`)

`PyRefTracer_SetTracer()` and `PyRefTracer_GetTracer()` let native tools observe
object creation and destruction. Extensions can fire `sys.monitoring` events
through the C API.

### Unicode and type construction (`whatsnew-3.14`)

`PyUnicodeWriter` is a public incremental string builder. `PyType_Freeze()`
makes a type immutable. `Py_tp_token` and `PyType_GetBaseByToken()` identify
extension-defined bases without brittle pointer comparisons.

### Public bytes construction (`whatsnew-3.15`)

`PyBytesWriter` creates, grows, resizes, writes, formats, finishes, and discards
incrementally built `bytes`. `PyBytes_FromStringAndSize(NULL, len)` and
`_PyBytes_Resize()` are soft-deprecated in its favor.

### Unified slots and exports (`whatsnew-3.15`)

`PySlot` and `PyType_FromSlots()` unify type and module definitions with nested
slots, explicit name/size/flags/metaclass/module slots, and typed convenience
macros. `PyModule_FromSlotsAndSpec()` and `PyModExport_*` consume the same
structure. `PyType_FromSpec*()` and `PyModule_FromDefAndSpec*()` are
soft-deprecated.

### Additional public APIs (`whatsnew-3.15`)

New APIs parse `METH_FASTCALL` arrays, create and recognize `frozendict`, access
`sys` attributes without `PySys_GetObject()`, and declare/check module ABI
compatibility. `PyCriticalSection` joins the Stable ABI. Dedicated
`*_DuringGC()` accessors are safe from `tp_traverse` handlers.

### Watcher and signal events (`3.15.0b3`)

Type watchers receive deallocation events for watched heap types. Function
watchers add `PyFunction_PYFUNC_EVENT_MODIFY_QUALNAME`. `PyErr_CheckSignals()`
raises an exception scheduled through `PyThreadState_SetAsyncExc()`.

### More Stable and Limited APIs (`3.15.0b3`)

`PyDict_SetDefaultRef()` joins the Stable ABI;
`PyObject_CallFinalizerFromDealloc()` joins the Limited API.
`PyMutex_IsLocked()` is public, and Windows
`PyThread_acquire_lock_timed()` honors its interrupt flag.

## Limited API and invariants

### Opaque reference and sequence APIs (`whatsnew-3.14`)

In Limited API 3.14, `Py_TYPE()` and `Py_REFCNT()` are opaque calls, and broken
`PySequence_Fast_GET_*` macros are removed. Borrowed stack references make
`Py_REFCNT(obj) == 1` unsafe for uniqueness; use the appropriate
`PyUnstable_Object_Is*Referenced()` API.

### Changed type invariants (`whatsnew-3.15`)

Types using managed dictionaries or weak references must also set
`Py_TPFLAGS_HAVE_GC`. `PyDateTime_IMPORT` is thread-safe; call it instead of
checking `PyDateTimeAPI` directly.

## Embedding and lifecycle

### ABI-flexible configuration (`whatsnew-3.14`)

Opaque `PyInitConfig` configures initialization without exposing C structure
layouts, including built-in modules through `PyInitConfig_AddModule()`.
`PyConfig_Get()`, `PyConfig_Set()`, and related APIs inspect or change current
runtime configuration.

### Interned strings across reinitialization (`whatsnew-3.14`)

`Py_Finalize()` deletes all interned strings. An embedder that later calls
`Py_Initialize()` must release extension-held interned references during
shutdown to prevent use-after-free.

### Embedding lifecycle semantics (`3.15.0b3`)

`Py_IsInitialized()` stays false until initialization, including `site` import,
is complete. `Py_RunMain()` returns an exit code instead of calling
`Py_Exit()`. `PyConfig_Set()` synchronizes legacy global flags and replaces
`sys.flags` instead of mutating the existing object.

## Source migration checklist

### Header and trashcan migrations (`whatsnew-3.13`)

`Python.h` no longer transitively supplies `<ieeefp.h>`, `<time.h>`,
`<sys/select.h>`, `<sys/time.h>`, or Windows `<stddef.h>`; include each header
used. Replace removed `Py_TRASHCAN_SAFE_BEGIN` / `END` with
`Py_TRASHCAN_BEGIN(object, deallocator)` / `Py_TRASHCAN_END`.

### Removed APIs and replacements (`whatsnew-3.15`)

Use `PyCodec_Encode()` / `PyCodec_Decode()` for removed Unicode codec helpers,
`PyWeakref_GetRef()` for removed weak-reference accessors,
`PyImport_ImportModule()` for `PyImport_ImportModuleNoBlock()`, and
`PyConfig_Get()` keys for removed `Py_Get*()` initialization queries.

Out-of-range unsigned values accepted by `PyArg_ParseTuple()` formats are
deprecated. Replace `PyComplexObject.cval` access with conversion functions and
private identifier caches with interned strings in module state. Replace
legacy portability macros for alignment, integer limits/types, varargs,
infinity, and long-double constants with C99/C11 facilities.

### Additional C migrations (`3.15.0b3`)

`PyConfig.bytes_warning` is deprecated for removal in 3.17,
`PySys_ResetWarnOptions()` is removed, and nullable `PyArg_Parse()` arguments
are unsupported.
