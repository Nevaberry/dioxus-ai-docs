# EventLogger & Diagnostics

## Tc3_EventLogger Library
The `Tc3_EventLogger` library provides structured event/alarm handling. Events are organized in **EventClasses** (created in SYSTEM > Type System > Event Classes tab). Each event has a name, severity (Info/Warning/Error/Critical), and optional display text with `{0}`, `{1}` argument placeholders.

Events are referenced as constants: `TC_Events.<ClassName>.<EventName>`.

## FB_TcMessage — Stateless Messages
For one-shot informational events (no state tracking).

```iecst
VAR
    fbMessage : FB_TcMessage;
    bInit : BOOL;
END_VAR

IF NOT bInit THEN
    bInit := TRUE;
    fbMessage.CreateEx(TC_Events.MyEvents.Start, 0);  // 0 = default source
END_IF

fbMessage.Send(0);  // 0 = current timestamp
```

## FB_TcAlarm — Stateful Alarms
Alarms have Raised/Cleared states plus optional Confirmed state.

```iecst
VAR
    fbAlarm : FB_TcAlarm;
    bInit : BOOL;
END_VAR

IF NOT bInit THEN
    bInit := TRUE;
    // CreateEx(event, bWithConfirmation, nSourceInfo)
    fbAlarm.CreateEx(TC_Events.MyEvents.Stop, TRUE, 0);
END_IF

// Set display text arguments via fluent interface
fbAlarm.ipArguments.Clear().AddString('Operator name');
fbAlarm.Raise(0);       // Raise alarm (0 = current time)
fbAlarm.Confirm(0);     // Mark as acknowledged
fbAlarm.Clear(0, FALSE); // Clear alarm; FALSE = keep confirmation state
                          // TRUE = reset confirmation (can't confirm after clear)
```

## FB_TcSourceInfo — Custom Source Names
By default, event source = POU path. Override with `FB_TcSourceInfo` for meaningful names.

```iecst
VAR
    fbSourceInfo : FB_TcSourceInfo;
    fbAlarm : FB_TcAlarm;
END_VAR

fbSourceInfo.Clear();
fbSourceInfo.sName := 'Water pump 3';
fbAlarm.CreateEx(TC_Events.MyEvents.Stop, FALSE, fbSourceInfo);
```

## Display Text Arguments
Use `{0}`, `{1}` placeholders in event display text, fill via fluent `ipArguments`:
`fbAlarm.ipArguments.Clear().AddString('value').AddInt(42);`

Logged events stored in `C:\TwinCAT\3.1\Boot\LoggedEvents.db` (default max 1000, configurable in Tools > Options > TwinCAT XAE Environment > EventLogger).
