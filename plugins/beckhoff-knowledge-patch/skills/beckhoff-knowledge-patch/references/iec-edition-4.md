# IEC 61131-3 Edition 4

Edition 4 (published May 2025) adds concurrency primitives, UTF-8 strings, standardized properties, and CLASS. TwinCAT does not implement Ed4 directly — it has its own syntax for many of the same concepts.

## TwinCAT Build 4026 vs Ed4 Implementation Status

| Ed4 Feature | TwinCAT 4026 Status |
|---|---|
| MUTEX / SEMAPHORE | **Not implemented.** Use `FB_IecCriticalSection` from `Tc2_System` |
| USTRING / UCHAR (UTF-8) | **Not native.** Use `UTF8#` prefix with `{attribute 'TcEncoding' := 'UTF-8'}` |
| PROPERTY_GET / PROPERTY_SET | **Own syntax.** TwinCAT uses `PROPERTY` with Get/Set accessors |
| ASSERT | **Not standard.** TwinCAT uses own pragma / `ADSLOGSTR` |
| CLASS (non-FB OOP) | **Not supported.** Use FUNCTION_BLOCK |
| Access modifiers (PUBLIC/PRIVATE/PROTECTED/INTERNAL) | **Supported** on methods, properties, and FBs |
| ABSTRACT / FINAL | **Supported** on FBs, methods, and properties |
| Namespaces | **Supported** — each library defines a namespace |
| Octal literals removed | **Aligned** — TwinCAT never widely used octal |
| IL language removed | **Not enforced** — TwinCAT still offers IL |

## Concurrency: MUTEX and SEMAPHORE (Chapter 6.9)

New standardized primitives for multi-task synchronization. Both have OOP and function-based APIs.

```iecst
// MUTEX — mutual exclusion
VAR mtx : MUTEX; END_VAR
mtx.LOCK();          // Block until acquired
mtx.UNLOCK();
mtx.TRYLOCK();       // Non-blocking: returns immediately if locked
// Properties: mtx.LOCK_COUNT, mtx.OWNER
// Function-based: MUTEX_LOCK(), MUTEX_UNLOCK(), MUTEX_TRYLOCK()

// SEMAPHORE — counting semaphore for resource pools
VAR sem : SEMA; END_VAR
sem.ACQUIRE();       // Decrement count, block if zero
sem.RELEASE();       // Increment count
sem.TRY_ACQUIRE();   // Non-blocking acquire
// Function-based: SEMA_ACQUIRE(), SEMA_RELEASE(), SEMA_TRY_ACQUIRE()
```

**TwinCAT equivalent:** `FB_IecCriticalSection` from `Tc2_System` provides `Enter()` / `Leave()` for task synchronization.

## USTRING and UCHAR (UTF-8 Strings)

New types for UTF-8 encoded strings. Unlike WSTRING (UTF-16, 2 bytes/char), UTF-8 uses 1-4 bytes per character and is ASCII-compatible.

```iecst
VAR
    sUtf8   : USTRING[100] := USTRING#'Hello';  // or U#'Hello'
    cUtf8   : UCHAR := UCHAR#'A';               // or U#'A'
END_VAR
```

**TwinCAT equivalent:** Build 4026 supports `UTF8#` prefix for string literals and `{attribute 'TcEncoding' := 'UTF-8'}` on STRING variables. No native USTRING type.

## New String Functions: LEN_MAX and LEN_CODE_UNIT

```iecst
VAR
    s : STRING[100] := 'Hello';
    u : USTRING[100] := U#'Hello';
END_VAR
a := LEN_MAX(s);        // 100 — declared max capacity
b := LEN_CODE_UNIT(u);  // Number of code units (>= LEN for multi-byte chars)
```

## Character Code in Curly Brackets

Any character specified by hex code in `${...}` syntax:

```iecst
x : STRING  := '${9}';              // Tab character
y : WSTRING := WSTRING#'${2211}';   // Sigma
z : USTRING := USTRING#'${1F579}'; // Joystick emoji
```

## String to ARRAY OF BYTE Conversions

- `STRING_TO_ARRAY_OF_BYTE`, `WSTRING_TO_ARRAY_OF_BYTE`, `USTRING_TO_ARRAY_OF_BYTE`
- `ARRAY_OF_BYTE_TO_STRING`, `ARRAY_OF_BYTE_TO_WSTRING`, `ARRAY_OF_BYTE_TO_USTRING`

## Access Modifiers: Ed4 Standard vs TwinCAT

Ed4 puts access modifiers on VAR blocks. TwinCAT applies them to methods, properties, and FB declarations instead.

```iecst
// IEC Ed4 standard — access modifiers on VAR blocks:
FUNCTION_BLOCK FB_Example
    VAR PUBLIC
        nPublicVar : INT;
    END_VAR
    VAR PRIVATE
        _nInternalVar : INT;
    END_VAR
END_FUNCTION_BLOCK

// TwinCAT — access modifiers on members, not VAR blocks:
FUNCTION_BLOCK FB_Example
    VAR
        _nInternalVar : INT;   // convention: underscore = private
    END_VAR
    PROPERTY PUBLIC nPublicVar : INT   // Get/Set accessors
    METHOD PRIVATE _DoInternal : BOOL  // restricted method
    METHOD PROTECTED DoForDerived      // available to subclasses
END_FUNCTION_BLOCK
```

TwinCAT keywords: **PUBLIC** (default, unrestricted), **PRIVATE** (declaring FB only), **PROTECTED** (FB + derivatives), **INTERNAL** (namespace/library), **FINAL** (prevents override), **ABSTRACT** (must override in derived FB).

## CLASS vs FUNCTION_BLOCK

Ed4 introduces `CLASS` as distinct from `FUNCTION_BLOCK`. A CLASS has no cyclic body, no I/O mapping (`AT %I*`), and no task assignment — it is pure OOP. Both support methods, properties, inheritance, and interfaces.

**TwinCAT does not support CLASS.** Use FUNCTION_BLOCK for all OOP. To approximate a pure CLASS, leave the FB body empty and use only methods and properties.

## Namespaces

Ed4 formalizes namespace support. TwinCAT already supports namespaces — each PLC library defines a namespace matching the library name:

```iecst
// Qualified access when two libraries export the same name:
VAR
    fb1 : MyLibrary.FB_Sensor;
    fb2 : OtherLib.FB_Sensor;
END_VAR
```

Build 4026 adds the `Force Qualified_only for library access` project property, requiring all library symbols to be namespace-qualified.

## IEC Standard Properties (PROPERTY_GET / PROPERTY_SET)

Ed4 standardizes properties with syntax different from TwinCAT's `PROPERTY` keyword:

```iecst
// IEC Ed4 standard (NOT TwinCAT syntax):
PROPERTY_GET PUBLIC nFoo : INT
    nFoo := _nFoo;
END_PROPERTY
PROPERTY_SET PUBLIC nFoo : INT
    _nFoo := nFoo;
END_PROPERTY
// Usage identical: fbFoo.nFoo := 10; x := fbFoo.nFoo;
```

Default access is PROTECTED (not PUBLIC). Supports ABSTRACT, FINAL modifiers. TwinCAT uses its own `PROPERTY` keyword with separate Get/Set accessor objects.

## ASSERT Function

Debug-time assertion. No effect when IN is TRUE; implementation-defined notification when FALSE. Disabled in production.

```iecst
ASSERT(IN := nIndex >= 0 AND nIndex < 100);
```

**TwinCAT equivalent:** No standard ASSERT. Use `ADSLOGSTR` for runtime diagnostics or conditional checks.
