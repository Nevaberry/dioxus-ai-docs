# Motion Control

## PLCopen Axis State Machine

All TwinCAT MC function blocks follow the PLCopen state model. Every axis is in exactly one state at a time:

```
Disabled ──MC_Power──► Standstill ──MC_MoveAbsolute──► DiscreteMotion
    ▲                      │   ▲          │                    │
    │                      │   └──Done─────┘                   │
    │                      │                                   │
    │                MC_Jog/MC_MoveVelocity──► ContinuousMotion│
    │                                                          │
    │              MC_Stop from ANY motion state                │
    │                      │                                   │
    │                      ▼                                   │
    │                  Stopping ──Done──► Standstill            │
    │                                                          │
    └──MC_Power(OFF)── any state         Error ──► ErrorStop ──┘
                                                      │
                                              MC_Reset │
                                                      ▼
                                                  Standstill
```

Key transitions: `MC_Power` enables/disables. Any motion FB moves from Standstill into DiscreteMotion or ContinuousMotion. `MC_Stop` forces Stopping from any motion state. Errors transition to ErrorStop; `MC_Reset` returns to Standstill.

## Rising-Edge Execute Pattern

Every PLCopen motion FB uses a rising edge on `Execute`. The FB latches inputs on the rising edge and runs asynchronously. Outputs remain valid until the next rising edge.

```iecst
// WRONG: holding Execute TRUE prevents re-triggering
fbMove.Execute := bStartMove;

// RIGHT: use R_TRIG for clean edge, or pulse for one cycle
rtrigStart(CLK := bStartMove);
fbMove.Execute := rtrigStart.Q;
```

## MC_Power — Enable an Axis

```iecst
VAR
    fbPower      : MC_Power;
    stAxis       : AXIS_REF;
    bEnableReq   : BOOL;   // operator request
    bEnabled     : BOOL;
    bPowerError  : BOOL;
    nPowerErrID  : UDINT;
END_VAR

fbPower(
    Axis            := stAxis,
    Enable          := bEnableReq,
    Enable_Positive := bEnableReq,   // allow forward motion
    Enable_Negative := bEnableReq,   // allow reverse motion
    Override        := 100.0,        // 0-100% velocity override
    Status          => bEnabled,
    Error           => bPowerError,
    ErrorID         => nPowerErrID
);
```

`Enable` is level-sensitive (not edge): TRUE keeps the axis enabled, FALSE disables it. `Enable_Positive` and `Enable_Negative` can be set independently to restrict direction. `Override` scales all commanded velocities (useful for operator speed dial).

## MC_MoveAbsolute — Point-to-Point Motion

```iecst
VAR
    fbMoveAbs     : MC_MoveAbsolute;
    stAxis        : AXIS_REF;
    bStart        : BOOL;
    fTargetPos    : LREAL := 250.0;
    bMoveDone     : BOOL;
    bMoveError    : BOOL;
    nMoveErrID    : UDINT;
    nState        : INT;
END_VAR

CASE nState OF
0: // IDLE — wait for start command
    IF bStart THEN
        fbMoveAbs.Execute := FALSE;  // ensure clean edge
        nState := 1;
    END_IF

1: // TRIGGER — rising edge starts the move
    fbMoveAbs(
        Axis          := stAxis,
        Execute       := TRUE,
        Position      := fTargetPos,
        Velocity      := 500.0,
        Acceleration  := 2000.0,
        Deceleration  := 2000.0,
        Jerk          := 10000.0,
        Direction     := MC_Positive_Direction,
        BufferMode    := MC_Aborting,   // abort any active motion
        Done          => bMoveDone,
        Error         => bMoveError,
        ErrorID       => nMoveErrID
    );
    nState := 2;

2: // MOVING — wait for completion
    fbMoveAbs(Axis := stAxis, Execute := FALSE);  // drop Execute, FB continues
    IF fbMoveAbs.Done THEN
        bStart := FALSE;
        nState := 0;
    ELSIF fbMoveAbs.Error THEN
        nState := 99;
    END_IF

99: // ERROR
    bStart := FALSE;
    // handle error: nMoveErrID contains the NC error code
END_CASE
```

`Direction` accepts `MC_Positive_Direction`, `MC_Negative_Direction`, `MC_Shortest_Way`, or `MC_Current_Direction`. Dropping `Execute` does NOT stop the motion -- the profile runs to completion. Use `MC_Stop` or `MC_Halt` to abort.

## MC_Home — Homing Sequence

```iecst
VAR
    fbHome       : MC_Home;
    stAxis       : AXIS_REF;
    bStartHome   : BOOL;
    bHomeDone    : BOOL;
    bHomeError   : BOOL;
    nHomeErrID   : UDINT;
    nHomeState   : INT;
END_VAR

CASE nHomeState OF
0: // IDLE
    IF bStartHome THEN
        nHomeState := 1;
    END_IF

1: // START homing — edge-triggered
    fbHome(
        Axis       := stAxis,
        Execute    := TRUE,
        Position   := 0.0,       // position assigned after homing completes
        HomingMode := MC_DefaultHoming,  // use NC-configured homing params
        Done       => bHomeDone,
        Error      => bHomeError,
        ErrorID    => nHomeErrID
    );
    nHomeState := 2;

2: // WAIT for homing to finish
    fbHome(Axis := stAxis, Execute := FALSE);
    IF fbHome.Done THEN
        // axis position is now 0.0; Axis.Status.Homed = TRUE
        bStartHome := FALSE;
        nHomeState := 0;
    ELSIF fbHome.Error THEN
        nHomeState := 99;
    END_IF

99: // ERROR
    bStartHome := FALSE;
END_CASE
```

`HomingMode` values: `MC_DefaultHoming` uses the homing parameters configured on the NC axis (direction, velocity, sensor assignment). `MC_Direct` sets the position immediately without moving. `MC_ReferenceFlagAndHWSync` homes to a hardware sync signal. Homing speeds and direction are configured in the axis Parameter tab, not in the FB itself.

## MC_Stop + MC_Reset — Error Recovery

```iecst
VAR
    fbStop       : MC_Stop;
    fbReset      : MC_Reset;
    stAxis       : AXIS_REF;
    bStopAxis    : BOOL;
    bResetAxis   : BOOL;
    bStopped     : BOOL;
    bResetDone   : BOOL;
    nRecovState  : INT;
END_VAR

// Trigger stop on any error or E-stop condition
bStopAxis := stAxis.Status.Error OR bEStopActive;

CASE nRecovState OF
0: // NORMAL — monitor for errors
    IF bStopAxis THEN
        nRecovState := 1;
    END_IF

1: // STOPPING — bring axis to controlled halt
    fbStop(
        Axis         := stAxis,
        Execute      := TRUE,
        Deceleration := 5000.0,   // aggressive decel for safety
        Jerk         := 50000.0,
        Done         => bStopped
    );
    IF bStopped THEN
        fbStop(Axis := stAxis, Execute := FALSE);
        nRecovState := 2;
    END_IF

2: // WAIT for operator reset
    IF bResetAxis AND NOT bEStopActive THEN
        nRecovState := 3;
    END_IF

3: // RESET — clear ErrorStop state, return to Standstill
    fbReset(
        Axis    := stAxis,
        Execute := TRUE,
        Done    => bResetDone
    );
    IF bResetDone THEN
        fbReset(Axis := stAxis, Execute := FALSE);
        bResetAxis := FALSE;
        nRecovState := 0;
    END_IF
END_CASE
```

`MC_Stop` differs from `MC_Halt`: `MC_Stop` locks the axis in the Stopping state and rejects all other motion commands until `Done`. `MC_Halt` brings the axis to Standstill and allows new commands immediately. Use `MC_Stop` for safety/error scenarios, `MC_Halt` for normal "pause" situations.

## MC_Jog — Continuous and Incremental

```iecst
VAR
    fbJog        : MC_Jog;
    stAxis       : AXIS_REF;
    bJogFwd      : BOOL;   // momentary HMI button
    bJogBwd      : BOOL;
    bInchMode    : BOOL;   // operator selects inching vs continuous
END_VAR

// Switch mode based on operator selection — use ONE instance
IF bInchMode THEN
    fbJog.Mode     := MC_JOGMODE_INCHING;
    fbJog.Position := 1.0;   // move 1 unit per button press
ELSE
    fbJog.Mode     := MC_JOGMODE_STANDARD_SLOW;
    fbJog.Position := 0.0;   // unused in continuous mode
END_IF

fbJog(
    Axis          := stAxis,
    JogForward    := bJogFwd,
    JogBackward   := bJogBwd,
    Velocity      := 50.0,
    Acceleration  := 500.0,
    Deceleration  := 500.0,
    Jerk          := 5000.0
);
```

In continuous mode (`MC_JOGMODE_STANDARD_SLOW`), the axis moves as long as the button is held. In inching mode (`MC_JOGMODE_INCHING`), each rising edge on JogForward/JogBackward moves exactly `Position` units. Always condition jog inputs with a manual-mode guard so jogging is disabled during automatic operation.

## MC_ReadParameter / MC_WriteParameter

```iecst
VAR
    fbReadParam  : MC_ReadParameter;
    fbWriteParam : MC_WriteParameter;
    stAxis       : AXIS_REF;
    fMaxVelo     : LREAL;
    bReadDone    : BOOL;
    bWriteDone   : BOOL;
    nReadState   : INT;
END_VAR

CASE nReadState OF
0: // READ current max velocity
    fbReadParam(
        Axis        := stAxis,
        Execute     := TRUE,
        ParameterNumber := MC_AxisParameter.MaxVelocity,
        Value       => fMaxVelo,
        Done        => bReadDone
    );
    IF bReadDone THEN
        fbReadParam(Axis := stAxis, Execute := FALSE);
        nReadState := 1;
    END_IF

1: // WRITE new max velocity (e.g. reduce for recipe change)
    fbWriteParam(
        Axis        := stAxis,
        Execute     := TRUE,
        ParameterNumber := MC_AxisParameter.MaxVelocity,
        Value       := 200.0,
        Done        => bWriteDone
    );
    IF bWriteDone THEN
        fbWriteParam(Axis := stAxis, Execute := FALSE);
        nReadState := 2;
    END_IF

2: // DONE
    ;
END_CASE
```

Common `MC_AxisParameter` values: `MaxVelocity`, `MaxAcceleration`, `MaxDeceleration`, `MaxJerk`, `ActualPosition`, `CommandedPosition`, `SWLimitPos`, `SWLimitNeg`. This is how you change axis limits at runtime (e.g., per recipe or after a mechanical changeover).

## BufferMode — Motion Command Queuing

BufferMode controls what happens when you issue a new motion command while one is already active:

| BufferMode | Behavior |
|---|---|
| `MC_Aborting` | Aborts current motion, starts new command immediately |
| `MC_Buffered` | Queues new command; starts after current finishes (axis stops briefly at transition) |
| `MC_BlendingLow` | Blends at the lower velocity of the two moves (smooth transition, no stop) |
| `MC_BlendingHigh` | Blends at the higher velocity of the two moves |
| `MC_BlendingPrevious` | Blends at the velocity of the finishing move |
| `MC_BlendingNext` | Blends at the velocity of the starting move |

```iecst
// Two-move blended sequence: go to 100, then 500 without stopping
fbMove1(
    Axis       := stAxis,
    Execute    := TRUE,
    Position   := 100.0,
    Velocity   := 200.0,
    BufferMode := MC_Aborting    // first move, nothing to buffer against
);

// Issue second move while first is active
fbMove2(
    Axis       := stAxis,
    Execute    := TRUE,
    Position   := 500.0,
    Velocity   := 300.0,
    BufferMode := MC_BlendingLow  // blend at 200 (lower of 200, 300)
);
```

`MC_Aborting` is the safest default. Use blending modes only for known multi-point paths where stopping between segments is unacceptable.

## MC3 vs MC2 (TF5400 Advanced Motion Pack)

MC3 is the newer motion library from TF5400. Key PLC-visible differences:

**MC_Default constant:** In MC2, passing `0` for dynamics means "use axis default." In MC3, `0` is a literal (invalid) value. Use `MC_Default` explicitly.

```iecst
// MC2 — 0 means "use axis default"
fbMoveAbs.Velocity := 0;

// MC3 — must use MC_Default
fbMoveAbs.Velocity := MC_Default;   // reads default from axis config
fbMoveAbs.Velocity := 0;            // ERROR in MC3: 0 is invalid
```

**Dynamics limits:** MC3 enforces explicit maximum values for velocity, acceleration, deceleration, and jerk that cap what FBs can command. MC2 only treats axis velocity as a physical max; other dynamics in axis params are defaults used when FBs pass 0.

**FB output timing:** MC2 FB outputs reflect values at PLC cycle start. MC3 outputs reflect the moment code executes within the cycle -- causes timing differences with the cyclic interface.

**Decoupling slaves:** MC2 has dedicated FBs (`MC_GearOut`, `MC_CamOut`). MC3 decouples by issuing any motion command with `BufferMode := MC_Aborting` -- no dedicated decoupling FBs.

## Coupled Motion — MC_GearIn / MC_CamIn

Electronic gearing and camming link a slave axis to a master axis.

```iecst
VAR
    fbGearIn     : MC_GearIn;
    stMaster     : AXIS_REF;
    stSlave      : AXIS_REF;
    bStartGear   : BOOL;
    bGearActive  : BOOL;
    bGearError   : BOOL;
END_VAR

// Engage 2:1 gear ratio (slave moves 2 units per 1 master unit)
fbGearIn(
    Axis            := stSlave,       // slave axis controlled by this FB
    Master          := stMaster,      // master axis to follow
    Execute         := bStartGear,
    RatioNumerator  := 2,             // slave distance
    RatioDenominator := 1,            // per master distance
    Acceleration    := 1000.0,
    Deceleration    := 1000.0,
    BufferMode      := MC_Aborting,
    InGear          => bGearActive,
    Error           => bGearError
);

// Disengage (MC2): use MC_GearOut
// Disengage (MC3): send any command with BufferMode := MC_Aborting
```

`MC_CamIn` works similarly but follows a cam table (position-position profile) instead of a linear ratio. Define cam tables in the NC configuration or build them at runtime with `MC_CamTableSelect`. Camming is used for rotary knife cuts, flying shears, and registration-based synchronization.
