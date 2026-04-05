# OOP: Function Blocks, Interfaces & Design Patterns

## FB_init Initialization Order & Additional Parameters
FB_init runs BEFORE input variable assignments are applied — inputs are not yet known during FB_init. To pass values needed at init time, declare additional parameters in FB_init beyond the two implicit ones. No `SUPER^.FB_init` call is allowed — the base FB_init runs automatically first for derived FBs.

```iecst
FUNCTION_BLOCK FB_Sensor
VAR
    nComPort : INT;
END_VAR

METHOD FB_init : BOOL
VAR_INPUT
    bInitRetains : BOOL;  // implicit — TRUE on cold/warm start
    bInCopyCode  : BOOL;  // implicit — TRUE during online change
    nPort        : INT;   // additional custom parameter
END_VAR
nComPort := nPort;
```

## Combined FB_init + Input/Property Initialization Syntax
Declare instances with FB_init params in parentheses, then input/property values in `:= (...)`. Works for arrays too.

```iecst
VAR
    // FB_init param, then input + property init
    fbSensor : FB_Sensor(nPort := 1) := (nInput := 100, nMyProp := 42);

    // Array: each element gets its own FB_init params and init values
    aSensors : ARRAY[1..2] OF FB_Sensor[(nPort := 1), (nPort := 2)]
                             := [(nInput := 10, nMyProp := 1), (nInput := 20, nMyProp := 2)];
END_VAR
```

## VAR_INST — Persistent Method-Local Variables
Normal method variables are re-initialized every call (stack-allocated). `VAR_INST` variables persist across calls — they're stored in the FB instance, not on the stack.

```iecst
METHOD DoWork : BOOL
VAR
    nTemp : INT;       // reset to 0 every call
END_VAR
VAR_INST
    nCallCount : INT;  // persists across calls, stored in FB instance
END_VAR
nCallCount := nCallCount + 1;
```

## REFERENCE TO Return Type for Direct Member Access
Returning `REFERENCE TO <struct>` from a property/method lets callers access individual members directly without a temp variable. Use `REF=` (not `:=`) in the Get accessor.

```iecst
PROPERTY MyData : REFERENCE TO ST_Data

// Get accessor:
MyData REF= stLocalData;   // REF= required, not :=

// Caller can now do:
nVal := fbSample.MyData.nField;   // direct member access, no temp needed
```

## VAR_IN_OUT Access in Methods — Warning C0371
Accessing the FB's VAR_IN_OUT variables from a method/property is risky because they may not be assigned yet (they're only guaranteed assigned when the FB body is called). Guard with `__ISVALIDREF` and suppress the warning.

```iecst
METHOD MyMethod
{warning disable C0371}
IF NOT __ISVALIDREF(bInOut) THEN
    RETURN;
END_IF
bInOut := NOT bInOut;
{warning restore C0371}
```

## Property Monitoring Attributes
Properties aren't visible in online mode by default. Add monitoring pragmas to the property declaration:

```iecst
// Cache last value — may become stale if property isn't accessed
{attribute 'monitoring' := 'variable'}
PROPERTY nStatus : INT

// Call Get accessor each monitoring refresh — live but may trigger side effects
{attribute 'monitoring' := 'call'}
PROPERTY nLiveValue : INT
```

## Build 4026: Mandatory Method Input Assignment
From Build 4026, method inputs WITHOUT an explicit initial value MUST be assigned at the call site. Inputs WITH an initial value are optional.

```iecst
METHOD DoWork : BOOL
VAR_INPUT
    nRequired : INT;           // MUST be assigned when calling (no default)
    nOptional : INT := 0;     // CAN be omitted (has default)
END_VAR

// fbX.DoWork(nRequired := 5);           // OK — nOptional defaults to 0
// fbX.DoWork(nOptional := 3);           // COMPILE ERROR in 4026+ — nRequired missing
```

## {attribute 'is_connected'} on FB Inputs
Detect at runtime whether an input was explicitly assigned from outside when calling the FB.

```iecst
FUNCTION_BLOCK FB_Motor
VAR_INPUT
    {attribute 'is_connected'}
    bEnable : BOOL;           // bEnable also works as a flag: TRUE if assigned from outside
END_VAR
```

## Interface Multiple Extends (but FB Single Inheritance)
Interfaces can extend multiple interfaces. Function blocks cannot extend multiple FBs — only single inheritance. This is the sole exception to "no multiple inheritance" in TwinCAT.

```iecst
// Interfaces CAN extend multiple interfaces
INTERFACE I_Combined EXTENDS I_Movable, I_Loggable, I_Configurable

// FBs: single inheritance only — this is a COMPILE ERROR:
// FUNCTION_BLOCK FB_Bad EXTENDS FB_Base1, FB_Base2

// But FBs CAN implement multiple interfaces:
FUNCTION_BLOCK FB_Motor EXTENDS FB_Actuator IMPLEMENTS I_Movable, I_Loggable
```

## No Method Overloading
When overriding a base class method in a subclass, the declaration **must match exactly** — access modifier, return type, and all variable declarations. TwinCAT does not support method overloading (same name, different parameters).

## Virtual Function Calls (Dynamic Dispatch)
Method calls are dynamically dispatched (virtual) ONLY when called through:
- **Interface variable**: `iBase.Method1()` — dispatches to the actual implementing FB
- **Pointer to FB**: `pFB^.Method1()` — dispatches based on actual pointed-to type
- **REFERENCE TO FB**: `refBase.Method1()` — dispatches based on actual referenced type
- **VAR_IN_OUT of base type**: same dynamic dispatch when a derived instance is passed

Direct calls on a typed instance (`fbSub1.Method1()`) are **statically** bound — always calls the declared type's method.

## \_\_QUERYINTERFACE (Runtime Interface Cast)
Performs runtime type conversion between interface references. Returns TRUE if the underlying FB actually implements the target interface, FALSE otherwise (and sets target to 0).

**Prerequisite**: Both source and destination interfaces must ultimately extend `__System.IQueryInterface`. This interface is implicitly available (no library needed).

```iecst
// All interfaces in the hierarchy must extend __System.IQueryInterface
INTERFACE I_Base EXTENDS __System.IQueryInterface
METHOD BaseMethod : BOOL

INTERFACE I_Extended EXTENDS I_Base
METHOD ExtMethod : BOOL

INTERFACE I_Other EXTENDS __System.IQueryInterface
METHOD OtherMethod : BOOL

// FB implements both I_Extended and I_Other
FUNCTION_BLOCK FB_Multi IMPLEMENTS I_Extended, I_Other

VAR
    fbMulti  : FB_Multi;
    iBase    : I_Base := fbMulti;
    iOther   : I_Other;
    bSuccess : BOOL;
END_VAR

// Runtime check: does the object behind iBase also implement I_Other?
bSuccess := __QUERYINTERFACE(iBase, iOther);
// bSuccess = TRUE, iOther now references fbMulti

// Failed cast: target set to 0
bSuccess := __QUERYINTERFACE(iBase, iUnrelated);
// bSuccess = FALSE, iUnrelated = 0
```

## Interface vs Abstract FB — Array Limitation
Arrays of interface variables work; arrays of REFERENCE TO abstract FB do NOT compile. This drives the design choice between interfaces and abstract FBs.

```iecst
// WORKS — interfaces are assignable array elements
aEmployees : ARRAY[1..10] OF I_Employee;
aEmployees[1] := fbFullTime;    // FB implementing I_Employee
aEmployees[2] := fbContract;    // different FB implementing I_Employee

// COMPILE ERROR — cannot make array of references to FB
// aEmployees : ARRAY[1..10] OF REFERENCE TO FB_Employee;

// Workaround: use pointers (but pointers break on online change)
aEmployees : ARRAY[1..10] OF POINTER TO FB_Employee;
```

## Combine Abstract FB + Interface (Library Best Practice)
Define an interface first, then create an abstract FB implementing it with shared logic. Consumers can inherit the abstract FB (easy) or implement the interface directly (flexible).

```iecst
INTERFACE I_Employee
METHOD GetFullName : STRING
METHOD GetMonthlySalary : LREAL

// Abstract FB provides shared implementation of GetFullName
FUNCTION_BLOCK ABSTRACT FB_Employee IMPLEMENTS I_Employee
// GetFullName is non-abstract — implemented once here
// GetMonthlySalary is ABSTRACT — each derived FB must implement

FUNCTION_BLOCK FB_FullTimeEmployee EXTENDS FB_Employee
// Only implements GetMonthlySalary — inherits GetFullName for free
```

## Composition via Delegation (Multiple Interface Workaround)
Since FBs can only EXTENDS one base, simulate multiple inheritance by embedding FBs and delegating interface methods to them.

```iecst
// FB_MyLight needs both dimming and delay behavior
FUNCTION_BLOCK FB_MyLight EXTENDS FB_Light IMPLEMENTS I_Delayable, I_Dimmable
VAR
    fbDimmingLight  : FB_DimmingLight;    // delegate dimming to this
    fbDelayedLight  : FB_DelayedLight;    // delegate delay to this
END_VAR

// I_Dimmable.SetControlLevel delegates to internal instance
METHOD SetControlLevel
VAR_INPUT nControlLevel : BYTE; END_VAR
fbDimmingLight.SetControlLevel(nControlLevel);
```

## FB_init Nesting Pitfall — Call Order Is Undefined
When an FB contains instances of other FBs with custom FB_init params, the inner FB_init runs BEFORE the outer FB_init. Parameters forwarded from outer to inner are not yet assigned. Workaround: explicitly call inner FB_init from outer FB_init.

```iecst
FUNCTION_BLOCK FB_Cluster
VAR
    // PROBLEM: nInternalPort not yet set when fbSensor.FB_init runs
    fbSensor : FB_Sensor(nPort := nInternalPort);
    nInternalPort : INT;
END_VAR

METHOD FB_init : BOOL
VAR_INPUT
    bInitRetains : BOOL;
    bInCopyCode  : BOOL;
    nPort        : INT;
END_VAR
nInternalPort := nPort;
// WORKAROUND: explicitly re-call inner FB_init with correct values
fbSensor.FB_init(bInitRetains := bInitRetains, bInCopyCode := bInCopyCode, nPort := nPort);
```

**Warning**: Explicit `FB_init()` call reinitializes ALL local variables of the target instance. Never call it from the PLC task at runtime — only from another FB_init during startup.
