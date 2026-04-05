# ST Language & TwinCAT Extensions

## Overflow/Underflow Intermediate Result Promotion
TwinCAT promotes intermediate results to native register size (32-bit on x86/ARM, 64-bit on x64). This means overflow/underflow is NOT truncated in expressions — only on assignment to a variable.

```iecst
VAR
    nWord : WORD := 65535;
    nZero : WORD := 0;
    bResult : BOOL;
    nAssigned : WORD;
END_VAR

// SURPRISE: bResult is FALSE — intermediate (65535+1) = 65536, not 0
bResult := (nWord + 1) = nZero;

// But assignment truncates: nAssigned becomes 0, then comparison is TRUE
nAssigned := nWord + 1;
bResult := (nAssigned = nZero);  // TRUE

// Force truncation with explicit cast:
bResult := (TO_WORD(nWord + 1) = nZero);  // TRUE
```

## STRING Defaults and T\_MaxString
- `STRING` without length = 80 characters (81 bytes with null terminator)
- Maximum STRING length = 255 characters
- `T_MaxString` = alias for `STRING(255)` — use in function/FB interfaces to avoid silent truncation
- TwinCAT silently truncates strings to destination variable length on assignment

## S= / R= (Set/Reset Operators)
ExST latching operators — equivalent to SET/RESET coils in ladder. Once set/reset, the value persists even after the trigger goes FALSE. Last-executed wins if both trigger simultaneously.

```iecst
VAR
    bMotorRunning : BOOL;
    bStart, bStop : BOOL;
END_VAR

bMotorRunning S= bStart;   // Latch TRUE when bStart is TRUE
bMotorRunning R= bStop;    // Latch FALSE when bStop is TRUE
// If both TRUE simultaneously: bStop wins (R= executes last)
```

## Chained Assignment & Inline Assignment
Multiple variables can be assigned in one expression. Assignments can also be embedded inside IF conditions.

```iecst
// Chained: all get the same value (works across types with implicit conversion)
v1 := v2 := v3 := v4 + 5;

// Inline assignment in IF — assigns b4 AND uses it as the condition
IF b4 := (v5 = 100) THEN
    // b4 is TRUE here, v5 was 100
END_IF
```

## REF= (Type-Safe Reference Assignment)
Assigns a typed reference to a variable. Unlike raw pointers, REF= enforces type safety — the reference must match the target's data type, preventing invalid pointer access at compile time.

```iecst
VAR
    myData1, myData2 : DUT_Test;
    refData : REFERENCE TO DUT_Test;
END_VAR

refData REF= myData1;      // refData now aliases myData1
refData.Value := 42;        // modifies myData1.Value

refData REF= myData2;      // re-seat to myData2
refData.Value := 99;        // modifies myData2.Value
```

## AND_THEN / OR_ELSE (Short-Circuit Evaluation)
Standard `AND`/`OR` in Structured Text evaluate ALL operands regardless of earlier results. `AND_THEN` and `OR_ELSE` are TwinCAT/CODESYS extensions that short-circuit — critical for null-pointer guards.

```iecst
// WRONG: ptrFB^.DoWork() is called even when ptrFB is NULL → crash
IF ptrFB <> 0 AND ptrFB^.DoWork() THEN ... END_IF

// CORRECT: short-circuits — ptrFB^.DoWork() only called if ptrFB <> 0
IF ptrFB <> 0 AND_THEN ptrFB^.DoWork() THEN
    Execute();
END_IF

// OR_ELSE: skip evaluation if first condition is already TRUE
IF bAutoMode OR_ELSE btnStart.RisingEdge() THEN
    // btnStart not polled when bAutoMode is TRUE (avoids side effects)
END_IF
```

## Key Attribute Pragmas Reference
Attributes are defined in the declaration part on the line before the target. In Actions/Transitions (ST only), place at the start of the implementation part since there's no declaration part.

```iecst
// Structure packing: 0=default(8), 1=byte, 2=2-byte, 4=4-byte, 8=8-byte
{attribute 'pack_mode' := '1'}
TYPE ST_Packed :
STRUCT
    bFlag : BOOL;    // offset 0
    nValue : DINT;   // offset 1 (not 4!) with pack_mode 1
END_STRUCT
END_TYPE

// Enum safety: qualified_only forces Enum.Value syntax, strict prevents implicit conversion
{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_State : (Idle, Running, Error);
END_TYPE
// Must use: eState := E_State.Running;  (not just: eState := Running)
// Cannot: nVal := eState;  (strict prevents implicit INT conversion)

// Instance path: auto-filled STRING with FB instance path at init
FUNCTION_BLOCK FB_Logger
VAR
    {attribute 'instance-path'}
    {attribute 'noinit'}
    sPath : STRING;   // e.g. 'MAIN.fbLogger' — must also have 'noinit'
END_VAR

// Prevent copy/assignment of FB instances
{attribute 'no_assign'}
FUNCTION_BLOCK FB_Singleton
// Assignment fbA := fbB; produces compiler error

// TcLinkTo: auto-link I/O variables in declaration (no manual mapping needed)
VAR
    {attribute 'TcLinkTo' := 'TIID^Device 1^Term 1 (EL1008)^Channel 1^Input'}
    bInput AT%I* : BOOL;
END_VAR

// TcRpcEnable: expose method for ADS RPC calls from .NET/C++
{attribute 'TcRpcEnable'}
METHOD DoWork : BOOL

// call_after_init: method called after FB_init completes (useful when FB_init order matters)
{attribute 'call_after_init'}
METHOD Init : BOOL

// Global init ordering: lower slot = earlier init (default is 0)
{attribute 'global_init_slot' := '100'}
PROGRAM MAIN

// Enable dynamic creation with __NEW / __DELETE
{attribute 'enable_dynamic_creation'}
FUNCTION_BLOCK FB_DynObj
```

## Conditional Compilation
TwinCAT conditional pragmas control code inclusion at compile time. Use `{define}` to set identifiers, `{IF}`/`{ELSIF}`/`{ELSE}`/`{END_IF}` to branch.

```iecst
// Define in code (local scope) or PLC project properties (global scope)
{define SIMULATION}
{define TARGET_VERSION '4026'}

// Basic conditional
{IF defined (SIMULATION)}
    bSimMode := TRUE;
{ELSE}
    bSimMode := FALSE;
{END_IF}

// Check define value
{IF hasvalue(TARGET_VERSION, '4026')}
    // Build 4026-specific code
{END_IF}

{undefine SIMULATION}   // removes the definition
```

## Advanced Conditional Operators (Implementation Part Only)
These operators only work in the implementation part, not in declarations (except plain `defined()` and `hasvalue()`).

```iecst
// Check if a variable exists in current scope
{IF defined (variable: g_bTest)}
    g_bTest := TRUE;
{END_IF}

// Check if a data type exists
{IF defined (type: ST_MyStruct)}
    myVar : ST_MyStruct;
{END_IF}

// Check if a POU exists — also supports method check with dot notation
{IF defined (pou: CheckBounds)}
    arrTest[CheckBounds(0, i, 10)] := 0;
{END_IF}
{IF defined (pou: FB_Motor.Reset)}
    // FB_Motor has a Reset method
{END_IF}

// Check variable data type
{IF hastype (variable: g_multitype, LREAL)}
    g_multitype := 0.9 * 1.1;
{ELSIF hastype (variable: g_multitype, STRING)}
    g_multitype := 'text';
{END_IF}

// Check if POU or variable has a user-defined attribute
{IF hasattribute (pou: fun1, 'vision')}
    result := fun1(42);
{END_IF}
{IF hasattribute (variable: g_globalInt, 'DoCount')}
    g_globalInt := g_globalInt + 1;
{END_IF}

// Combine with AND, OR, NOT
{IF defined (pou: PLC_PRG1) AND NOT defined (pou: CheckBounds)}
    bNoBoundsCheck := TRUE;
{END_IF}
```
