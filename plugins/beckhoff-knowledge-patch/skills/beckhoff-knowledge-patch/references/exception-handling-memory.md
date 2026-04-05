# Exception Handling & Memory

## \_\_TRY / \_\_CATCH / \_\_FINALLY / \_\_ENDTRY
TwinCAT exception handling (Build 4024+ for 32-bit, Build 4026+ for 64-bit). Catches access violations, divide-by-zero, etc. without stopping the PLC runtime. `__FINALLY` always executes (like other languages). Exception type is `__SYSTEM.ExceptionCode`.

```iecst
VAR
    exc : __SYSTEM.ExceptionCode;
    pData : POINTER TO INT;
    nResult : INT;
    nDivisor : INT;
END_VAR

__TRY
    nResult := pData^;              // may throw RTSEXCPT_ACCESS_VIOLATION
    nResult := 100 / nDivisor;     // may throw RTSEXCPT_DIVIDEBYZERO
__CATCH(exc)
    // exc holds the exception code
    IF exc = __SYSTEM.ExceptionCode.RTSEXCPT_ACCESS_VIOLATION THEN
        pData := ADR(nResult);     // fix the pointer
    ELSIF exc = __SYSTEM.ExceptionCode.RTSEXCPT_DIVIDEBYZERO THEN
        nDivisor := 1;
    END_IF
__FINALLY
    // always runs, even if no exception
__ENDTRY
```

**Raise exceptions explicitly** with `F_RaiseException` (Tc2\_System library). Outside a `__TRY` block, it stops the controller.

```iecst
F_RaiseException(__SYSTEM.ExceptionCode.RTSEXCPT_ARRAYBOUNDS);
```

**x86 caveat**: Intercepted floating-point exceptions on x86 (not x64) can cause stack overflow or unrecoverable state. Use implicit check functions for float ops inside try-catch on x86 targets.

## \_\_NEW / \_\_DELETE (Dynamic Memory)
Dynamically allocate/free FBs, DUTs, or scalar arrays from the router memory pool. Returns a typed pointer (0 on failure). FBs/DUTs require `{attribute 'enable_dynamic_creation'}`.

```iecst
{attribute 'enable_dynamic_creation'}
FUNCTION_BLOCK FB_Worker
VAR
    nCount : INT;
END_VAR
```

```iecst
VAR
    pWorker : POINTER TO FB_Worker;
    pBuffer : POINTER TO BYTE;
END_VAR

// Allocate FB instance
IF pWorker = 0 THEN
    pWorker := __NEW(FB_Worker);
END_IF

// Use it
IF pWorker <> 0 THEN
    pWorker^.nCount := pWorker^.nCount + 1;
END_IF

// Allocate scalar array (25 bytes)
pBuffer := __NEW(BYTE, 25);
pBuffer[0] := 42;

// Free memory — __DELETE calls FB_exit, then sets pointer to 0
__DELETE(pWorker);
__DELETE(pBuffer);
```

**Key rules:**
- Always `__DELETE` in the same cycle or before PLC shutdown — no garbage collector, leaks are permanent
- For STRING allocation: use `__NEW(BYTE, length)` with `POINTER TO STRING(length)`
- On `__DELETE` of an FB pointer, `FB_exit` is called automatically — use the *derived* type pointer (not base) for inheritance, or `FB_exit` won't fire
- Memory comes from router memory pool — monitor with `FB_GetRouterStatusInfo` (Tc2\_Utilities)
- Online change breaks if you change the data layout of a dynamically-created type

## Null Guard Patterns (Preventing Page Faults)
Three sources of page faults: uninitialized pointers, references, and interfaces. Each has a different guard.

```iecst
// Pointer: check <> 0 before dereferencing
IF pData <> 0 THEN
    nVal := pData^;
END_IF

// Reference: use __ISVALIDREF
VAR
    refNum : REFERENCE TO INT;
END_VAR
IF __ISVALIDREF(refNum) THEN
    refNum := 42;
END_IF

// Interface: check <> 0 (unassigned interface = null pointer)
VAR
    iMotor : I_Motor;
END_VAR
IF iMotor <> 0 THEN
    iMotor.Start();
END_IF
```

**Implicit CheckPointer POU**: Add via right-click PLC project > Add > POU for implicit checks > Pointer Check. Called automatically before every pointer dereference — useful for diagnostics but adds overhead per use.
