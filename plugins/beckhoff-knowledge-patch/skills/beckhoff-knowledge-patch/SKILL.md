---
name: beckhoff-knowledge-patch
description: TwinCAT changes since training cutoff (latest: 4026) — PLC++ next-gen compiler, VAR_GENERIC generics, __TRY/__CATCH, ADS .NET SDK v6, TcUnit, Linux/Docker. Load before working with TwinCAT.
version: "4026"
license: MIT
metadata:
  author: Nevaberry
---

# Beckhoff TwinCAT Knowledge Patch

Covers TwinCAT 3.1 Build 4024–4026, PLC++ next-gen compiler, IEC 61131-3 Edition 4, and the broader TwinCAT ecosystem (ADS, MQTT, HMI, motion, Linux/Docker). Claude Opus 4.6 knows basic IEC 61131-3, Structured Text syntax, and general PLC concepts, but is **unaware** of TwinCAT-specific extensions, pragmas, OOP patterns, Build 4026 features, and the topics below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| ST language & extensions | [references/st-language-extensions.md](references/st-language-extensions.md) | Overflow promotion, STRING defaults, S=/R=, REF=, AND_THEN/OR_ELSE, pragmas, conditional compilation |
| Exception handling & memory | [references/exception-handling-memory.md](references/exception-handling-memory.md) | `__TRY`/`__CATCH`/`__FINALLY`, `__NEW`/`__DELETE`, null guard patterns |
| OOP patterns | [references/oop-patterns.md](references/oop-patterns.md) | FB_init, VAR_INST, interfaces, inheritance, `__QUERYINTERFACE`, design patterns |
| Build 4026 & generics | [references/build-4026-generics.md](references/build-4026-generics.md) | `VAR_GENERIC CONSTANT`, mandatory method inputs, `__POUNAME`, `XSIZEOF` |
| PLC++ next-gen compiler | [references/plcpp-next-gen.md](references/plcpp-next-gen.md) | Plain-text projects, CLI compiler, CI/CD, secure online change, IEC Ed4 |
| Project structure & CI/CD | [references/project-structure-cicd.md](references/project-structure-cicd.md) | File extensions, source control, LineIDs, git filters, automation interface, community tools |
| Unit testing (TcUnit) | [references/testing-tcunit.md](references/testing-tcunit.md) | Test suites, multi-cycle tests, TcUnit-Runner, CI/CD integration |
| ADS protocol & .NET SDK | [references/ads-dotnet-sdk.md](references/ads-dotnet-sdk.md) | AdsClient v6.x, symbolic/handle access, notifications, RPC, Rx extensions |
| MQTT & IoT (TF6701) | [references/mqtt-iot.md](references/mqtt-iot.md) | FB_IotMqttClient, publish/subscribe, JSON serialization |
| Standard libraries (Tc2) | [references/standard-libraries.md](references/standard-libraries.md) | Tc2_Standard, Tc2_System file I/O, synchronization, memory, time |
| HMI & visualization | [references/hmi-visualization.md](references/hmi-visualization.md) | TE2000 architecture, scripting types, framework API patterns |
| Motion control | [references/motion-control.md](references/motion-control.md) | PLCopen state machine, MC_Power/MoveAbsolute/Home/Stop/Reset/Jog patterns, BufferMode, MC3 vs MC2, gearing/camming |
| Linux & Docker | [references/linux-docker.md](references/linux-docker.md) | RT Linux runtime, Docker containers, ADS-over-MQTT, VFIO |
| IEC 61131-3 Edition 4 | [references/iec-edition-4.md](references/iec-edition-4.md) | MUTEX/SEMAPHORE, USTRING, standard properties, ASSERT |
| EventLogger & diagnostics | [references/eventlogger-diagnostics.md](references/eventlogger-diagnostics.md) | Tc3_EventLogger, FB_TcMessage, FB_TcAlarm, display text arguments |
| Libraries & placeholders | [references/libraries-placeholders.md](references/libraries-placeholders.md) | Placeholder vs direct references, pinned vs newest, library repositories |

---

## Essential Pragmas — Quick Reference (inline)

```iecst
{attribute 'pack_mode' := '1'}           // Struct packing: 0=default(8), 1=byte, 2/4/8
{attribute 'qualified_only'}              // Enum: force Enum.Value syntax
{attribute 'strict'}                      // Enum: prevent implicit INT conversion
{attribute 'instance-path'} + {attribute 'noinit'}  // Auto-filled FB instance path
{attribute 'no_assign'}                   // Prevent FB copy/assignment
{attribute 'TcLinkTo' := '...'}          // Auto-link I/O variable
{attribute 'TcRpcEnable'}                // Expose method for ADS RPC
{attribute 'call_after_init'}            // Method called after FB_init completes
{attribute 'enable_dynamic_creation'}    // Allow __NEW/__DELETE
{attribute 'monitoring' := 'variable'}   // Property visible in online mode (cached)
{attribute 'monitoring' := 'call'}       // Property visible in online mode (live)
{attribute 'is_connected'}               // Detect if FB input was assigned externally
{attribute 'hide'}                       // Hide variable from symbol config (not exposed via ADS)
{attribute 'obsolete' := 'Use NewFB instead'}  // Compiler warning when FB/method is used
```

---

## Critical Gotchas (inline)

### Overflow/Underflow: Intermediate Results Are NOT Truncated

TwinCAT promotes intermediates to native register size. Overflow only happens on assignment.

```iecst
VAR
    nWord : WORD := 65535;
    nZero : WORD := 0;
END_VAR

// SURPRISE: FALSE — intermediate (65535+1) = 65536, not 0
bResult := (nWord + 1) = nZero;

// Fix: explicit cast forces truncation
bResult := (TO_WORD(nWord + 1) = nZero);  // TRUE
```

### AND/OR Evaluate ALL Operands — Use AND_THEN/OR_ELSE for Short-Circuit

```iecst
// WRONG: ptrFB^.DoWork() called even when ptrFB is NULL → crash
IF ptrFB <> 0 AND ptrFB^.DoWork() THEN ... END_IF

// CORRECT: short-circuits
IF ptrFB <> 0 AND_THEN ptrFB^.DoWork() THEN
    Execute();
END_IF
```

### FB_init Runs BEFORE Input Assignments

Inputs are not yet assigned during FB_init. Pass values as additional FB_init parameters.

### Build 4026: Method Inputs Without Defaults Are Mandatory

```iecst
METHOD DoWork : BOOL
VAR_INPUT
    nRequired : INT;        // MUST assign at call site
    nOptional : INT := 0;   // CAN omit
END_VAR
```

### MC3: Use MC_Default, Not 0

```iecst
// MC2: 0 means "use axis default"
fbMoveAbs.Velocity := 0;

// MC3: 0 is invalid — must use MC_Default
fbMoveAbs.Velocity := MC_Default;
```

### EventLogger Migration (Build 4026+)

```iecst
// Build 4024 and earlier: Tc2_System event logging
ADSLOGSTR(msgCtrlMask := ADSLOG_MSGTYPE_WARN,
    msgFmtStr := 'Motor %s overtemp',
    strArg := sMotorName);

// Build 4026+: Tc2_System event FBs REMOVED — use Tc3_EventLogger
VAR
    fbMsg : FB_TcMessage;
END_VAR
fbMsg.CreateEx(TC_Events.MyClass.MotorOvertemp, 0);
fbMsg.ipArguments.AddString(sMotorName);
fbMsg.Send(0);
```

### T_MaxString for FB Interface Inputs

```iecst
// WRONG: caller's string silently truncated to 10 chars
METHOD ProcessName
VAR_INPUT
    sName : STRING(10);
END_VAR

// CORRECT: use T_MaxString (= STRING(255)) at FB boundaries
METHOD ProcessName
VAR_INPUT
    sName : T_MaxString;   // Tc2_System typedef, STRING(255)
END_VAR
```

### FB_IecCriticalSection — Forgetting Leave() Deadlocks

```iecst
// DANGER: early RETURN between Enter/Leave = permanent deadlock
fbCS.Enter();
IF bError THEN
    fbCS.Leave();    // MUST Leave before RETURN!
    RETURN;
END_IF
// ... work with shared data ...
fbCS.Leave();
```

---

## C# ↔ PLC Type Mapping (inline)

| PLC Type | Size | C# Type |
|----------|------|---------|
| BOOL | 1 byte | bool (or byte) |
| BYTE | 1 byte | byte |
| INT | 2 bytes | **short** (NOT int!) |
| DINT | 4 bytes | int |
| LINT | 8 bytes | long |
| REAL | 4 bytes | float |
| LREAL | 8 bytes | double |
| STRING(n) | n+1 bytes | string (specify length) |

---

## TwinCAT Project File Extensions (inline)

| Extension | What | Mergeable? |
|-----------|------|------------|
| `.tsproj` | TwinCAT project | Yes (Project Compare Tool) |
| `.plcproj` | PLC project | Yes (Project Compare Tool) |
| `.TcPOU` | POU (program, FB, function) | Yes |
| `.TcDUT` | Data type (struct, enum) | Yes |
| `.TcGVL` | Global Variable List | Yes |
| `.TcTTO` | PLC Task Object | Yes |
| `.tmc` | TcCOM module class | **Not mergeable** (auto-regenerated) |

Exclude from SCM: `.sln`, `.suo`, `.tpy`. The `.tmc` does NOT need to be in source control from Build 4018+.

---

## Null Guard Patterns (inline)

```iecst
// Pointer: check <> 0
IF pData <> 0 THEN nVal := pData^; END_IF

// Reference: use __ISVALIDREF
IF __ISVALIDREF(refNum) THEN refNum := 42; END_IF

// Interface: check <> 0 (unassigned = null)
IF iMotor <> 0 THEN iMotor.Start(); END_IF
```

---

## Generics — VAR_GENERIC CONSTANT (inline, Build 4026)

```iecst
FUNCTION_BLOCK FB_Buffer
VAR_GENERIC CONSTANT
    nSize : UDINT := 1;
END_VAR
VAR
    aData : ARRAY[0..nSize-1] OF BYTE;
END_VAR

// Instantiation
VAR
    fbBuf : FB_Buffer<100>;              // literal
    fbBuf2 : FB_Buffer<(2 * cLen)>;     // expression
END_VAR
```

---

## __TRY / __CATCH / __FINALLY (inline)

```iecst
VAR
    exc : __SYSTEM.ExceptionCode;
END_VAR

__TRY
    nResult := pData^;
    nResult := 100 / nDivisor;
__CATCH(exc)
    IF exc = __SYSTEM.ExceptionCode.RTSEXCPT_ACCESS_VIOLATION THEN
        pData := ADR(nResult);
    END_IF
__FINALLY
    // always runs
__ENDTRY
```
