# C API and extensions

## Extension structure, layout, and ownership

### ctypes metaclasses and alignment

Projects subclassing ctypes internal metaclasses must move setup performed after
`super().__new__()` into `__init__` and create classes by calling the metaclass
rather than its `__new__` directly. `ctypes.Structure` adds `_align_` for
explicit packed-memory alignment.

Python 3.14 adds `Structure._layout_` to choose a nondefault ABI, and platform
bit-field layouts no longer overlap. Depending on `_pack_` alone for MSVC
layout outside Windows is deprecated. `memoryview_at()` exposes pointer-backed
memory without copying, and public `CField` metadata supports layout inspection.

### Reference ownership (`whatsnew-3.13`)

`PyModule_Add()` always steals its value reference, including on failure.
`PyDict_GetItemRef()`, `PyList_GetItemRef()`, `PyImport_AddModuleRef()`, and
`PyWeakref_GetRef()` return strong rather than borrowed references; callers own
and must release them.

### Lookups that preserve errors

`PyObject_HasAttrWithError()` and `PyMapping_HasKeyWithError()`, including their
string variants, return `-1` on error rather than clearing it. The older
error-suppressing lookup helpers report suppressed failures through
`sys.unraisablehook()`.

### Direct source migrations

`Python.h` no longer supplies `<ieeefp.h>`, `<time.h>`, `<sys/select.h>`,
`<sys/time.h>`, or, on Windows, `<stddef.h>` transitively. Include each owning
header directly. Replace removed `Py_TRASHCAN_SAFE_BEGIN` and `END` with
`Py_TRASHCAN_BEGIN(object, deallocator)` and `Py_TRASHCAN_END`.

Python 3.14 `Py_DECREF()` protects against deallocation stack overflow, so
third-party extension objects no longer need the trashcan mechanism. The `k`
and `K` `PyArg_Parse()` formats accept `__index__()`, and `Py_BuildValue()` adds
`p` to convert a C integer to `bool`.

## Free-threading and synchronization

### Declaring no-GIL support

Multi-phase extensions declare support with `Py_mod_gil`; single-phase
extensions use `PyUnstable_Module_SetGIL()`. Importing an undeclared extension
normally re-enables the GIL unless it was explicitly forced off. Installing
extension packages into a free-threaded build requires pip 24.1 or newer.

Windows build backends targeting free-threaded extensions must define
`Py_GIL_DISABLED` themselves.

### Dictionary iteration

`PyDict_Next()` does not lock a dictionary in free-threaded builds. Hold one
critical section around the entire iteration rather than locking each step.

### Safe uniqueness checks

In Limited API 3.14, `Py_TYPE()` and `Py_REFCNT()` become opaque calls and the
broken `PySequence_Fast_GET_*` macros disappear. Borrowed operand-stack
references make `Py_REFCNT(obj) == 1` unsafe for uniqueness. Use the applicable
`PyUnstable_Object_Is*Referenced()` helper.

## Public construction and iteration APIs

### Unambiguous iteration and integer interchange

`PyIter_NextItem()` replaces the ambiguous end/error result of `PyIter_Next()`.
Fixed-width `PyLong_As*` and `PyLong_From*` functions, plus `PyLong_Export()`
and `PyLongWriter_*()`, provide native integer interchange without private
representation access.

### Unicode and type construction

`PyUnicodeWriter` is a public incremental string builder. `PyType_Freeze()`
makes a type immutable, and `Py_tp_token` with `PyType_GetBaseByToken()`
identifies extension-defined bases without brittle pointer comparisons.

### Public bytes construction

Python 3.15 `PyBytesWriter` creates, grows, resizes, writes, formats, finishes,
or discards incremental `bytes`. `PyBytes_FromStringAndSize(NULL, len)` and
`_PyBytes_Resize()` are soft-deprecated in its favor.

### Unified definition slots and exports

`PySlot` and `PyType_FromSlots()` unify type and module definitions, including
nested slots, explicit name, size, flags, metaclass, and module slots, and typed
convenience macros. `PyModule_FromSlotsAndSpec()` and `PyModExport_*` consume the
same structure. Older `PyType_FromSpec*()` and `PyModule_FromDefAndSpec*()`
constructors are soft-deprecated.

### Additional public APIs

Python 3.15 adds APIs to parse `METH_FASTCALL` arrays, create and recognize
`frozendict`, access `sys` attributes without `PySys_GetObject()`, declare and
check module ABI compatibility, and use `PyCriticalSection` through the Stable
ABI. Dedicated `*_DuringGC()` accessors are safe from `tp_traverse` handlers.

In 3.15.0b3, `PyDict_SetDefaultRef()` joins the Stable ABI and
`PyObject_CallFinalizerFromDealloc()` joins the Limited API.
`PyMutex_IsLocked()` is public, and Windows
`PyThread_acquire_lock_timed()` honors its interrupt flag.

## Embedding and interpreter lifecycle

### ABI-flexible configuration

Opaque `PyInitConfig` configures initialization without coupling embedders to C
structure layouts, including adding built-in modules with
`PyInitConfig_AddModule()`. `PyConfig_Get()`, `PyConfig_Set()`, and related APIs
inspect or change the active runtime configuration.

### Interned strings across reinitialization

`Py_Finalize()` deletes all interned strings in Python 3.14. An embedder that
later calls `Py_Initialize()` must release extension-held interned references
during shutdown or risk use-after-free.

### Finalization-safe interpreter access

Python 3.15 interpreter guards, interpreter views, and attach/detach APIs let
native threads use interpreters that can be finalizing or concurrently deleted.
The `PyGILState` family is soft-deprecated without a removal plan and should not
be expanded in new code.

### Embedding lifecycle semantics

In Python 3.15.0b3, `Py_IsInitialized()` stays false until initialization,
including `site` import, is complete. `Py_RunMain()` returns an exit code rather
than calling `Py_Exit()`. `PyConfig_Set()` synchronizes legacy global flags and
replaces `sys.flags` rather than mutating the existing object.

## Stable ABI and module compatibility

### Free-threaded Stable ABI

Python 3.15 extensions can target `abi3t`, normally through a build backend or
directly with `Py_TARGET_ABI3T`. Unsupported surfaces still require separate
`abi3` and `cp315t` builds. `abi3t` code uses opaque type data and the
`PyModExport_*` hook instead of a traditional `PyInit_*` entry point.

### Module ABI enforcement

In Python 3.15.0b3, `Py_mod_abi` is mandatory for modules built from slot arrays
or `PyModExport_*`. Importing a non-free-threaded extension into a free-threaded
interpreter raises an exception. On non-Windows free-threaded builds,
`Py_LIMITED_API` no longer also requires `Py_GIL_DISABLED`.

## Invariants, hooks, and events

### Allocation and monitoring hooks

`PyRefTracer_SetTracer()` and `PyRefTracer_GetTracer()` let native tools observe
object creation and destruction. Extensions can fire `sys.monitoring` events
through a C API.

### Managed state and datetime

Python 3.15 types using managed dictionaries or weak references must also set
`Py_TPFLAGS_HAVE_GC`. `PyDateTime_IMPORT` is thread-safe; call it rather than
testing `PyDateTimeAPI` directly.

### Watchers and signals

In Python 3.15.0b3, type watchers are notified when watched heap types are
deallocated, and function watchers add
`PyFunction_PYFUNC_EVENT_MODIFY_QUALNAME`. `PyErr_CheckSignals()` raises an
exception scheduled through `PyThreadState_SetAsyncExc()`.

## Removed and deprecated C APIs

### Replacements for removed APIs

Removed Unicode encode/decode helpers migrate to `PyCodec_Encode()` and
`PyCodec_Decode()`. Removed weak-reference accessors migrate to
`PyWeakref_GetRef()`, and `PyImport_ImportModuleNoBlock()` becomes
`PyImport_ImportModule()`. Removed `Py_Get*()` initialization queries become
the corresponding `PyConfig_Get()` keys.

### Argument, representation, and portability migrations

Out-of-range unsigned values accepted by `PyArg_ParseTuple()` formats are
deprecated. Replace direct `PyComplexObject.cval` access with conversion
functions, and private identifier-caching helpers with an interned string in
module state. Legacy portability macros for alignment, integer types and
limits, varargs, infinity, and long-double constants are deprecated in favor of
C99 or C11 facilities.

### Additional 3.15.0b3 migrations

`PyConfig.bytes_warning` is deprecated for removal in 3.17,
`PySys_ResetWarnOptions()` is removed, and nullable `PyArg_Parse()` arguments
are unsupported.
