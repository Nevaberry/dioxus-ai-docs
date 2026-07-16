# C API and extensions

Use this reference for extension compatibility, references and errors, types and modules, free-threading, the Stable and Limited APIs, and embedding.

## Compatibility and removed APIs

### Reduced transitive includes from `Python.h` (Python 3.13)
`Python.h` no longer supplies `<ieeefp.h>`, `<time.h>`, `<sys/select.h>`, or `<sys/time.h>`, and on Windows it no longer supplies `<stddef.h>`; extensions using their declarations must include them directly. Defining `Py_LIMITED_API` also causes `Python.h` to undefine `Py_BUILD_CORE`, `Py_BUILD_CORE_BUILTIN`, and `Py_BUILD_CORE_MODULE`.

### `PY_SSIZE_T_CLEAN` is obsolete (Python 3.13)
C extensions no longer need to define `PY_SSIZE_T_CLEAN` before `Python.h`; `#` argument-format units now always use `Py_ssize_t`.

### Trashcan macro migration (Python 3.13)
`Py_TRASHCAN_SAFE_BEGIN` and `Py_TRASHCAN_SAFE_END` were removed; use `Py_TRASHCAN_BEGIN(object, deallocator)` and `Py_TRASHCAN_END` in `tp_dealloc` implementations.

### Removed legacy C entry points (Python 3.13)
The old `PyObject_As*Buffer()` APIs were removed in favor of `PyObject_GetBuffer()` plus `PyBuffer_Release()`, and the `PyEval_Call*()`/`PyCFunction_Call()` family was replaced by the corresponding `PyObject_Call*()` APIs. Legacy initialization setters such as `PySys_SetPath()`, `Py_SetPath()`, and `Py_SetStandardStreamEncoding()` were also removed in favor of configuring `PyConfig` before `Py_InitializeFromConfig()`.

### Stricter C buffer flags (3.13.0)
Passing `PyBUF_READ` or `PyBUF_WRITE` to `PyBuffer_FillInfo()` or `PyObject_GetBuffer()` now raises `SystemError`; those flags are reserved for the `PyMemoryView_*` APIs.

### Refcount-safe and opaque limited APIs (Python 3.14)
Borrowed operand-stack references can make `Py_REFCNT()` smaller than in older releases, so extensions testing uniqueness must use `PyUnstable_Object_IsUniquelyReferenced()` or `PyUnstable_Object_IsUniqueReferencedTemporary()` as appropriate. In the 3.14 limited API, `Py_TYPE()` and `Py_REFCNT()` are opaque calls and the broken `PySequence_Fast_GET_*` macros are removed.

### C API removals and reinitialization hazards (Python 3.14)
`PyDictObject.ma_version_tag` is removed in favor of dictionary watchers, immutable types with mutable bases now raise `TypeError`, and the undocumented C recursion-limit fields are gone in favor of `Py_EnterRecursiveCall()`. `Py_Finalize()` now deletes all interned strings, so embedders that reinitialize Python must release extension-held interned references during shutdown to avoid use-after-free crashes.

### Additional C API migrations (3.14.0)
`PySequence_In()` is soft-deprecated in favor of `PySequence_Contains()`, and `Py_MEMCPY`, `Py_IS_NAN`, `Py_IS_INFINITY`, `Py_IS_FINITE`, and `Py_HUGE_VAL` are also soft-deprecated. The undocumented `PyUnicode_AsEncodedObject()`/`AsDecodedObject()`/`AsEncodedUnicode()`/`AsDecodedUnicode()` functions are scheduled for removal in 3.15, while non-tuple sequences for nested `PyArg_Parse*()` units that expose borrowed data are deprecated.

### Stable ABI for free-threaded extensions (Python 3.15 preview)
Free-threaded builds now have the `abi3t` Stable ABI. Extensions normally select it through their build backend or by defining `Py_TARGET_ABI3T`; code must use opaque per-type storage and the new module export/slot machinery rather than embedding `PyObject`, while extensions needing APIs outside `abi3t` should publish separate `abi3` and `cp315t` builds. `sys.abi_info` exposes runtime ABI details, and `PyCriticalSection` is now part of the Stable ABI.

### C API compatibility migrations (Python 3.15 preview)
Extension modules can declare and check ABI requirements with `Py_mod_abi`, `PyABIInfo_Check()`, and `PyABIInfo_VAR`; new `*_DuringGC()` accessors are the safe way to reach type, item, or module data inside `tp_traverse`. Managed-dict or managed-weakref types must now also set `Py_TPFLAGS_HAVE_GC`, and thread-safe initialization requires calling `PyDateTime_IMPORT` rather than checking `PyDateTimeAPI` directly.

Legacy `Py_Get*()` runtime-configuration getters are removed in favor of keys passed to `PyConfig_Get()`, `PyWeakref_GetObject()` is replaced by strong-reference `PyWeakref_GetRef()`, and `PyImport_ImportModuleNoBlock()` is replaced by `PyImport_ImportModule()`. Direct `PyComplexObject.cval` access and out-of-range acceptance by unsigned `PyArg_Parse*()` formats are newly deprecated.

### Further C API migrations (3.15.0b3)
`PySys_ResetWarnOptions()` and the deprecated `PyUnicode_As*Object()`/`PyUnicode_As*Unicode()` codec helpers are removed; `_PyObject_CallMethodId()`, `_PyObject_GetAttrId()`, and `_PyUnicode_FromId()` are newly deprecated. `PyConfig.bytes_warning`, `Py_MATH_El`, and `Py_MATH_PIl` are deprecated, `Py_INFINITY` is soft-deprecated, and portability macros including `Py_ALIGNED`, `PY_FORMAT_SIZE_T`, the `Py_LL`/`Py_ULL` and integer-limit families, `PY_SIZE_MAX`, `Py_UNICODE_SIZE`, `Py_UNICODE_WIDE`, and `Py_VA_COPY` are now soft-deprecated.

## References, errors, and object lifecycle

### Ownership- and error-aware C accessors (Python 3.13)
New strong-reference APIs include `PyDict_GetItemRef()`, `PyDict_SetDefaultRef()`, `PyList_GetItemRef()`, `PyImport_AddModuleRef()`, and `PyWeakref_GetRef()`, avoiding borrowed-reference hazards. `PyMapping_GetOptionalItem*()` and `PyObject_GetOptionalAttr*()` suppress only missing-key or missing-attribute conditions, while the new `*Has*WithError()` functions return `-1` on error instead of silently discarding exceptions.

### Owned and borrowed constant access in C (3.13.0)
`Py_GetConstant()` returns a strong reference to a named singleton or small constant, while `Py_GetConstantBorrowed()` provides the borrowed-reference form; for example, `Py_GetConstant(Py_CONSTANT_ZERO)` retrieves zero.

### Finalization-safe C lifecycle inspection (3.13.0)
`PyThreadState_GetUnchecked()` returns `NULL` rather than terminating when there is no current thread state, leaving the check to its caller. `Py_IsFinalizing()` reports whether the main interpreter is shutting down.

### Reference ownership for `PyModule_Add()` (3.13.0)
The new `PyModule_Add()` resembles `PyModule_AddObject()` and `PyModule_AddObjectRef()` but always steals the supplied value reference, including on failure.

### Reporting suppressed C API errors (3.13.0)
Legacy C helpers that suppress errors, including `PyDict_GetItem()`, `PyMapping_HasKey()`, `PyObject_HasAttr()`, and `PySys_GetObject()`, now send those errors to `sys.unraisablehook()`. `PyErr_FormatUnraisable()` lets extensions add formatted context when reporting an unraisable exception.

### Object-lifetime tracing from C (3.13.0)
`PyRefTracer_SetTracer()` and `PyRefTracer_GetTracer()` let native tooling observe object creation and destruction in a manner analogous to allocation tracing with `tracemalloc`.

### Public C hash helpers (3.13.0)
`Py_HashPointer()` hashes a pointer, `PyObject_GenericHash()` exposes the default object hash, and `PyHASH_MODULUS`, `PyHASH_BITS`, `PyHASH_INF`, and `PyHASH_IMAG` expose interpreter hash parameters.

### Active-exception thread-state cleanup (3.14.0)
`PyThreadState_Clear()` now warns and calls `sys.excepthook` if the thread state still owns an active exception, exposing lifecycle mistakes that were previously silent.

## Types, modules, and argument parsing

### `ctypes` metaclass initialization moved (Python 3.13)
Internal `ctypes` metaclasses now perform initialization in `__init__` rather than `__new__`. Subclasses must move logic that ran after `super().__new__()` into `__init__`, and class creation must call the metaclass rather than invoking only its `__new__` method.

### C-level monitoring events (Python 3.13)
The new PyMonitoring C API lets extensions generate PEP 669 events with `PyMonitoring_Fire*()` functions and delimit monitored scopes with `PyMonitoring_EnterScope()` and `PyMonitoring_ExitScope()`.

### Public C clock API (Python 3.13)
The new `PyTime_t` API exposes wall-clock, monotonic, and performance-counter readings through `PyTime_Time*()`, `PyTime_Monotonic*()`, and `PyTime_PerfCounter*()`, with raw variants and conversion to `double` seconds.

### Forced `ctypes.Structure` alignment (3.13.0)
`ctypes.Structure` subclasses can force their alignment with the new `_align_` class attribute.

### Native-byte integer conversion in C (3.13.0)
`PyLong_AsNativeBytes()`, `PyLong_FromNativeBytes()`, and `PyLong_FromUnsignedNativeBytes()` convert between Python integers and native byte buffers, with flags controlling edge cases when values fill the buffer.

### Type-name formatting in C (3.13.0)
`PyType_GetModuleName()` and `PyType_GetFullyQualifiedName()` expose type naming without manual attribute access. `PyUnicode_FromFormat()` adds `%T`, `%T#`, `%N`, and `%N#` for formatting qualified names of object types and type objects.

### Correct access to static-type dictionaries (3.13.0)
`PyType_GetDict()` retrieves the dictionary exposed as `cls.__dict__`; extension code must use it for static built-in types, whose `tp_dict` is now always `NULL`.

### Managed-dictionary GC hooks (3.13.0)
Types using `Py_TPFLAGS_MANAGED_DICT` must call `PyObject_VisitManagedDict()` and `PyObject_ClearManagedDict()` from their traverse and clear functions.

### Non-raising dictionary pops in C (3.13.0)
`PyDict_Pop()` and `PyDict_PopString()` optionally return a removed value but, unlike Python's `dict.pop()` without a default, do not raise `KeyError` for a missing key.

### Non-ASCII C keyword parsing (3.13.0)
`PyArg_ParseTupleAndKeywords()` now accepts non-ASCII keyword names, so extension-call signatures no longer need to restrict named parameters to ASCII.

### Explicit `ctypes` structure layouts (Python 3.14)
`Structure` and `Union` bit fields now follow platform GCC/Clang or MSVC layouts more closely and no longer overlap; set `_layout_` to request a non-default ABI. On non-Windows systems, using `_pack_` to imply MSVC layout is deprecated in favor of `_layout_ = 'ms'`.

### Complex C data support (Python 3.14)
`struct` adds `F` and `D` formats for C float-complex and double-complex values. When compiler and `libffi` support is present, `ctypes` also exposes `c_float_complex`, `c_double_complex`, and `c_longdouble_complex`.

### Unambiguous C iteration and integer interop (Python 3.14)
`PyIter_NextItem()` replaces the ambiguous result convention of `PyIter_Next()`, and fixed-width `PyLong_AsInt32/64`, `AsUInt32/64`, and matching constructors map directly to `<stdint.h>`. PEP 757's `PyLong_Export()`/`FreeExport()` and `PyLongWriter_*` APIs expose arbitrary-size integers through an explicit native layout.

### Public C Unicode and type-building APIs (Python 3.14)
The new `PyUnicodeWriter` family incrementally constructs strings from characters, substrings, UTF-8, wide characters, reprs, and formatted data before `Finish()` or `Discard()`, and `PyUnicode_Equal()` provides direct equality. `PyType_Freeze()` makes a type immutable, while `Py_tp_token` and `PyType_GetBaseByToken()` identify extension-defined bases without fragile pointer checks.

### Public Windows COM helpers in `ctypes` (3.14.0)
`ctypes.COMError` and `ctypes.CopyComPointer()` are now public instead of being available only through the private `_ctypes` module.

### Caller-locked C dictionary iteration (3.14.0)
In a free-threaded build, `PyDict_Next()` no longer locks the dictionary itself; callers must hold a critical section around the entire iteration loop.

```c
Py_BEGIN_CRITICAL_SECTION(dict);
while (PyDict_Next(dict, &pos, &key, &value)) {
    /* use borrowed key and value */
}
Py_END_CRITICAL_SECTION();
```

### Vectorcall slots for spec-created types (3.14.0)
The new `Py_tp_vectorcall` slot lets the `PyType_FromSpec()` family set `tp_vectorcall`, including from limited-API extensions implementing efficient `__new__` or `__init__` calls.

### Context-object watchers in C (3.14.0)
`PyContext_AddWatcher()` and `PyContext_ClearWatcher()` register callbacks for entering and exiting context objects.

### Python-aware C file handling (3.14.0)
`Py_fopen()` accepts a Python path object and sets a Python exception on failure; pair it with `Py_fclose()`, which supplies the required portable close behavior on Windows.

### C version packing and Boolean construction (3.14.0)
`Py_PACK_VERSION()` and `Py_PACK_FULL_VERSION()` bit-pack Python version numbers. The new `p` format for `Py_BuildValue()` converts a C integer truth value directly to a Python `bool`.

```c
PyObject *enabled = Py_BuildValue("p", flag);
```

### Explicit index conversion for native-byte integers (3.14.0)
`PyLong_AsNativeBytes()` no longer invokes `__index__()` by default. Pass `Py_ASNATIVEBYTES_ALLOW_INDEX` when index-compatible non-`int` objects should be accepted.

### C byte construction and argument parsing (Python 3.15 preview)
The `PyBytesWriter` family creates, grows, writes, resizes, formats, finishes, or discards an incrementally built `bytes` value, replacing the soft-deprecated pattern of allocating with `PyBytes_FromStringAndSize(NULL, n)` and resizing privately. `PyArg_ParseArray()` and `PyArg_ParseArrayAndKeywords()` parse the vector argument layout used by `METH_FASTCALL` functions.

### Unified C definition slots and module exports (Python 3.15 preview)
`PySlot` and `PyType_FromSlots()` provide a single extensible slot representation for types and modules, including nested subslots, scalar data, type layout, metaclass, module, and flag entries. `PyModExport_<name>` replaces `PyInit_<name>` where the new export protocol is required, and the older `PyType_FromSpec*()` and `PyModule_FromDefAndSpec*()` construction families are soft-deprecated.

### C support for immutable mappings (3.15.0b3)
The C API adds `PyAnyDict_Check()`/`PyAnyDict_CheckExact()` for either mutable or frozen dictionaries, plus `PyFrozenDict_Check()`, `PyFrozenDict_CheckExact()`, and `PyFrozenDict_New()` for the new built-in type.

### C module creation and ABI declarations (3.15.0b3)
`PyImport_CreateModuleFromInitfunc()` creates a module from a spec and initialization function. Modules created from a slot array through `PyModule_FromSlotsAndSpec()` or `PyModExport_*` must include a `Py_mod_abi` slot rather than treating it as optional metadata.

### Stable, Limited, and watcher C APIs (3.15.0b3)
`Py_SIZE()`, `Py_IS_TYPE()`, and `Py_SET_SIZE()` join the Stable ABI, while `PyObject_CallFinalizerFromDealloc()` joins the Limited API. Function watchers receive `PyFunction_PYFUNC_EVENT_MODIFY_QUALNAME` when a watched function's qualified name changes.

## Free-threading and synchronization

### Lightweight extension mutexes (Python 3.13)
`PyMutex` is a new one-byte mutex for extension code; `PyMutex_Lock()` releases the GIL when it must block, and `PyMutex_Unlock()` releases the mutex.

### Free-threaded C critical sections (3.13.0)
PEP 703 critical-section macros provide per-object locking for free-threaded builds and compile as no-ops in the default GIL build, allowing one extension code path to support both runtimes.

### C signaling and synchronization updates (3.15.0b3)
`PyErr_CheckSignals()` now raises an exception scheduled with `PyThreadState_SetAsyncExc()`, and public non-limited critical-section variants accept one or two `PyMutex*` values directly. `PyUnstable_Object_EnableDeferredRefcount()` returns `0` for an object not tracked by the garbage collector.

## Embedding and interpreter lifecycle

### ABI-flexible embedding configuration (Python 3.14)
The opaque `PyInitConfig` API configures and initializes an embedded interpreter without exposing CPython configuration structs, with create/set/get/error/free operations and `Py_InitializeFromInitConfig()`. `PyInitConfig_AddModule()` registers built-ins, while `PyConfig_Get()`, `PyConfig_Set()`, `PyConfig_GetInt()`, and `PyConfig_Names()` inspect or alter the running interpreter.

### Finalization-safe interpreter access from C (Python 3.15 preview)
PEP 788 adds interpreter guards that postpone finalization, thread-safe views of interpreters that may concurrently disappear, and attach/detach APIs with built-in finalization protection. These replace unsafe check-then-attach patterns; the `PyGILState` family is now soft-deprecated without a removal plan.

### Embedding lifecycle semantics (3.15.0b3)
`Py_RunMain()` returns an exit code instead of calling `Py_Exit()` after a script, command, or REPL, and `Py_IsInitialized()` becomes true only after initialization, including `site` import, is complete. Runtime `PyConfig_Set()` calls also update matching legacy globals such as `Py_InspectFlag`; it and `sys.set_int_max_str_digits()` replace the `sys.flags` object instead of mutating it in place.
