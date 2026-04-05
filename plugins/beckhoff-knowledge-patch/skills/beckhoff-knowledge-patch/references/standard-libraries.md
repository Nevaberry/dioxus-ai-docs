# Standard Libraries (Tc2_Standard & Tc2_System)

## Tc2_Standard — Standard IEC 61131-3
Standard IEC 61131-3 FBs: TON, TOF, TP, CTU/CTD/CTUD, R_TRIG/F_TRIG, and string functions.

### String Functions and T_MaxString
`STRING` defaults to 80 chars, max 255. `T_MaxString` = `STRING(255)`. TwinCAT silently truncates on assignment.

```iecst
VAR
    s1      : STRING := 'Hello';       // 80 char capacity (default)
    s2      : STRING(20) := ' World';  // 20 char capacity
    sResult : T_MaxString;             // STRING(255) — use for function I/O
    nPos    : INT;
END_VAR
// GOTCHA: CONCAT only takes 2 args — chain calls for 3+ strings
sResult := CONCAT(CONCAT(s1, s2), '!');  // 'Hello World!'
nPos := FIND(sResult, 'World');           // 7 (1-based, 0 = not found, case-sensitive)
sResult := MID(sResult, 5, 7);           // 'World' — MID(str, length, position)
// DANGER: long string to short variable silently truncates
s2 := 'This string is way too long for 20 chars';  // truncated, no error!
```

## Tc2_System — TwinCAT System Library

### File I/O
Async FBs via ADS (3-phase: Open → Read/Write → Close). Rising-edge `bExecute`, `bBusy`/`bError`/`nErrId` outputs. FOPEN_MODE constants (combine with `OR`): `FOPEN_MODEREAD`(1), `FOPEN_MODEWRITE`(2), `FOPEN_MODEAPPEND`(4), `FOPEN_MODETEXT`(16), `FOPEN_MODEBINARY`(32).

```iecst
VAR
    fbFileOpen  : FB_FileOpen;
    fbFileWrite : FB_FileWrite;
    fbFileClose : FB_FileClose;
    hFile       : UINT;
    nState      : INT;
    sNetId      : T_AmsNetId;  // empty = local
END_VAR
CASE nState OF
0:  fbFileOpen(sNetId := sNetId, sPathName := 'C:\Data\log.csv',
        nMode := FOPEN_MODEWRITE OR FOPEN_MODETEXT, bExecute := TRUE);
    IF NOT fbFileOpen.bBusy THEN
        fbFileOpen(bExecute := FALSE);
        IF NOT fbFileOpen.bError THEN hFile := fbFileOpen.hFile; nState := 1; END_IF
    END_IF
1:  fbFileWrite(sNetId := sNetId, hFile := hFile,
        pWriteBuff := ADR(sData), cbWriteLen := LEN2(ADR(sData)), bExecute := TRUE);
    IF NOT fbFileWrite.bBusy THEN fbFileWrite(bExecute := FALSE); nState := 2; END_IF
2:  fbFileClose(sNetId := sNetId, hFile := hFile, bExecute := TRUE);
    IF NOT fbFileClose.bBusy THEN fbFileClose(bExecute := FALSE); nState := 3; END_IF
END_CASE
```

### Multi-task Synchronization
`FB_IecCriticalSection` (mutual exclusion via `Enter()`/`Leave()`), `TestAndSet(flag)` (atomic), `GETCURTASKINDEX`.

```iecst
VAR
    fbCritSection  : FB_IecCriticalSection;
    nSharedCounter : DINT;  // accessed from multiple tasks
    bFlag          : BOOL;
END_VAR
// DANGER: any RETURN or runtime error between Enter/Leave = permanent deadlock!
fbCritSection.Enter();
nSharedCounter := nSharedCounter + 1;  // keep critical section SHORT
fbCritSection.Leave();

// TestAndSet — returns TRUE if flag was already SET (atomic)
IF NOT TestAndSet(bFlag) THEN
    // ... exclusive work (flag was FALSE, now TRUE) ...
    bFlag := FALSE;  // release
END_IF
```

### Memory Functions
`MEMCPY`, `MEMMOVE`, `MEMSET`, `MEMCMP` via `ADR()`/`SIZEOF()`. Incorrect params crash the runtime.

```iecst
VAR
    stSrc  : ST_MyData;
    stDest : ST_MyData;
    arrBuf : ARRAY[0..99] OF BYTE;
END_VAR
// MEMCPY(destAddr, srcAddr, size) — same param order as C
MEMCPY(ADR(stDest), ADR(stSrc), SIZEOF(stSrc));
// MEMSET — zero-initialize a struct
MEMSET(ADR(stDest), 0, SIZEOF(stDest));
// MEMCMP — returns 0 if equal
IF MEMCMP(ADR(stSrc), ADR(stDest), SIZEOF(stSrc)) = 0 THEN (* equal *) END_IF
// MEMMOVE — safe for overlapping regions (MEMCPY is NOT)
MEMMOVE(ADR(arrBuf[10]), ADR(arrBuf[0]), 50);
```

### Time Functions
`F_GetSystemTime` returns FILETIME (100ns since 1601). `F_GetTaskTime` returns current cycle start time.

```iecst
VAR
    fbGetSystemTime : GETSYSTEMTIME;
    fileTime        : T_FILETIME;
    sTimestamp      : STRING;
END_VAR
// Get FILETIME (two DWORDs)
fbGetSystemTime(timeLoDW => fileTime.dwLowDateTime, timeHiDW => fileTime.dwHighDateTime);
// Convert chain: FILETIME → TIMESTRUCT → STRING
sTimestamp := SYSTEMTIME_TO_STRING(FILETIME_TO_SYSTEMTIME(fileTime));
// Result: e.g. '2025-03-15-14:30:05.123'
```

### FB_FormatString (Tc2_Utilities)
sprintf-style string formatting with `%s`, `%d`, `%f` placeholders, up to 10 args.

```iecst
VAR
    fbFmt : FB_FormatString;
    sOut  : T_MaxString;
END_VAR
// GOTCHA: args must be wrapped with F_INT(), F_LREAL(), F_STRING() type helpers
fbFmt(sFormat := 'Axis %d pos=%.2f mm', arg1 := F_INT(3), arg2 := F_LREAL(124.56));
sOut := fbFmt.sOut;  // 'Axis 3 pos=124.56 mm'
```

### EventLogger Migration (Build 4026+)
The older `ADSLOGEVENT` / `ADSCLEAREVENTS` / `FB_SimpleAdsLogEvent` in Tc2_System only work up to Build 4024. Build 4026+ requires the `Tc3_EventLogger` library instead — the old FBs are no longer supported.
