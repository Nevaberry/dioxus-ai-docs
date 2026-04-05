# Build 4026 Features & Generics

## Build 4026 PLC Feature Summary

Key PLC additions in TwinCAT 3.1 Build 4026:

- **Generics** (`VAR_GENERIC CONSTANT`) -- parameterized FBs with compile-time constants
- **Mandatory method inputs** -- inputs without defaults must be assigned at call site
- **New operators** -- `__POUNAME`, `__POSITION`, `XSIZEOF`
- **64-bit date types** -- `LDATE`, `LDATE_AND_TIME` (LDT), `LTIME_OF_DAY` (LTOD)
- **UTF8# literal prefix** -- interpret string literals as UTF-8
- **`__TRY`/`__CATCH` on 64-bit** -- exception handling now on x64 runtimes
- **Referenced libraries** -- use a PLC project directly as a library reference
- **VS 2022 support** -- 64-bit engineering environment

## VAR_GENERIC CONSTANT (Generics)
Build 4026 introduces generics via `VAR_GENERIC CONSTANT`. A generic constant is declared inside an FB and its value is set per-instance at declaration time. The constant is fixed for the lifetime of each instance (no online change support).

```iecst
FUNCTION_BLOCK FB_Buffer
VAR_GENERIC CONSTANT
    nSize : UDINT := 1;        // initial value only for compile checks
END_VAR
VAR
    aData : ARRAY[0..nSize-1] OF BYTE;
END_VAR
```

Instantiation uses angle brackets (literal) or `<( expression )>` syntax:

```iecst
VAR CONSTANT
    cLen : DINT := 50;
END_VAR
VAR
    fbBuf1  : FB_Buffer<100>;           // literal: nSize = 100
    fbBuf2  : FB_Buffer<(2 * cLen)>;    // expression: nSize = 100
    aBufs   : ARRAY[0..3] OF FB_Buffer<16>;  // array of generic instances
END_VAR
```

**Inheritance with generics**: `VAR_GENERIC CONSTANT` must come before `EXTENDS`/`IMPLEMENTS`. A derived FB can fix the generic or forward its own.

```iecst
FUNCTION_BLOCK FB_Queue
VAR_GENERIC CONSTANT
    nCapacity : UDINT := 1;
END_VAR
IMPLEMENTS I_Queue
VAR
    aItems : ARRAY[0..nCapacity-1] OF INT;
END_VAR

// Fix parent generic to 256
FUNCTION_BLOCK FB_FixedQueue EXTENDS FB_Queue<256>

// Forward own generic to parent
FUNCTION_BLOCK FB_FlexQueue
VAR_GENERIC CONSTANT
    nCap : UDINT := 1;
END_VAR
EXTENDS FB_Queue<nCap>
```

### Generic Limitations

- **Constants only, not types** -- no type parameterization (`FB_List<T>` is not possible), only integer constant generics
- **Integer data types only** -- `UDINT`, `DINT`, `LINT`, `ULINT`, `INT`, `UINT`, `SINT`, `USINT`, `BYTE`, `WORD`, `DWORD`, `LWORD`
- **No online change** -- edits to an FB with `VAR_GENERIC CONSTANT` require login with download
- **Compile-time expressions only** -- `<( expr )>` must resolve to a constant at compile time; no runtime variables

## __POUNAME Operator
Returns the containing POU name as a STRING at runtime. Useful for logging without hardcoding names.

```iecst
// In MAIN program → 'MAIN'
// In FB_Motor.Start method → 'FB_Motor.Start'
// In FB_Motor.Status property Get → 'FB_Motor.Status.Get'
sSource := __POUNAME();
```

## __POSITION Operator
Returns source file position as a STRING: `'Line 5 (Decl)'` or `'Line 12, Column 3 (Impl)'`. Combined with `__POUNAME`, replaces hardcoded location strings in error/log messages.

```iecst
sWhere := __POSITION();   // e.g. 'Line 7, Column 1 (Impl)'
```

## XSIZEOF Operator
Platform-aware `SIZEOF` replacement. Returns `ULINT` on 64-bit, `UDINT` on 32-bit. Prefer over `SIZEOF` when assigning to `__UXINT` -- `SIZEOF` always returns `UDINT`, which truncates on 64-bit.

```iecst
VAR
    nBytes : __UXINT;   // ULINT on x64, UDINT on x86/ARM
    aData  : ARRAY[0..99] OF DINT;
END_VAR
nBytes := XSIZEOF(aData);   // 400 on all platforms, return type matches platform
```

## Mandatory Method Inputs (Build 4026)

From Build 4026, inputs WITHOUT an initial value MUST be assigned at the call site. Inputs WITH a default remain optional. Applies to methods, functions, and FB calls.

```iecst
METHOD DoWork : BOOL
VAR_INPUT
    nRequired : INT;        // no default → MUST assign at call site
    nOptional : INT := 0;   // has default → CAN omit
END_VAR

// fbX.DoWork(nRequired := 5);           // OK — nOptional defaults to 0
// fbX.DoWork(nOptional := 3);           // COMPILE ERROR — nRequired missing
```

Migration note: existing code that relied on implicit zero-initialization of unassigned inputs will fail to compile under Build 4026.

## 64-Bit Date and Time Types (Build 4026)

New LINT-based date/time types with nanosecond precision. Use for EtherCAT distributed clocks and high-speed logging. Existing `DATE`/`DT`/`TOD` remain 32-bit second-resolution.

```iecst
VAR
    dLong     : LDATE;              // LDATE#2025-12-31
    dtLong    : LDATE_AND_TIME;     // LDT#2025-12-31-23:59:59.999999999
    todLong   : LTIME_OF_DAY;       // LTOD#23:59:59.999999999
END_VAR
// Aliases: LDT = LDATE_AND_TIME, LTOD = LTIME_OF_DAY
// Complements the existing LTIME (nanosecond duration) from earlier builds
```
