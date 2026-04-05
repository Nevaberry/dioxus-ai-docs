# PLC++ Next-Gen Compiler

## What Changed (Build 4026+)
TwinCAT PLC++ is a new PLC runtime + compiler generation shipping with TwinCAT 3.1 Build 4026. It coexists with classic TwinCAT PLC on the same runtime. Existing PLC libraries remain fully compatible.

| | Classic TwinCAT PLC | TwinCAT PLC++ |
|---|---|---|
| **File format** | `.TcPOU` / `.TcDUT` (XML wrapping ST) | Plain-text `.st` files |
| **IDE requirement** | Visual Studio + XAE Shell | XAE Shell or standalone CLI compiler |
| **CI/CD builds** | COM Automation Interface (needs VS DTE) | `tccompiler` CLI — no VS install needed |
| **Online change safety** | Pointers may dangle after online change | Pointers/references auto-adjusted |
| **IEC conformity** | Partial Edition 3 | Near-full Edition 4 (classes, access modifiers) |
| **Emergency mode** | Not available | Dedicated emergency program for orderly shutdown |
| **Runtime perf** | Baseline | Up to 1.5x faster (3x with optimizer) |

## Plain-Text File Format
PLC++ stores code as plain `.st` files — no XML wrapping. Git diffs, code reviews, and merge tools work natively.

```iecst
// File: ConveyorControl.st — this IS the file on disk, no XML envelope
FUNCTION_BLOCK FB_ConveyorControl
VAR_INPUT
    bStart       : BOOL;
    fTargetSpeed : LREAL := 1.5;  // m/s
END_VAR
VAR
    fbDrive : FB_DriveController;
    eState  : E_ConveyorState;
END_VAR

// Declaration + implementation in one file — no separate editors
CASE eState OF
    E_ConveyorState.Idle:
        IF bStart THEN eState := E_ConveyorState.Starting; END_IF
    E_ConveyorState.Running:
        fbDrive(fSetpoint := fTargetSpeed);
END_CASE
```

Compare with classic TwinCAT, which wraps the same ST inside XML:

```xml
<!-- Classic .TcPOU — XML envelope around ST code -->
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_ConveyorControl" Id="{...guid...}" SpecialFunc="None">
    <Declaration><![CDATA[
FUNCTION_BLOCK FB_ConveyorControl
VAR_INPUT
    bStart : BOOL;
END_VAR
    ]]></Declaration>
    <Implementation>
      <ST><![CDATA[ (* code here *) ]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
```

## CLI Compiler
Standalone CLI compiler (`tccompiler`) — no Visual Studio or XAE install needed on the build machine.

```bash
# Build a PLC++ project
tccompiler build --project ./MyMachine/PlcProject.plcproj

# Build with optimizations (up to 3x runtime speed improvement)
tccompiler build --project ./MyMachine/PlcProject.plcproj --optimize

# Run unit tests headlessly after build
tccompiler build --project ./MyMachine/PlcProject.plcproj --run-tests
```

## CI/CD Pipeline Example

```yaml
# .github/workflows/plc-build.yml
name: PLC++ Build & Test
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest # tccompiler requires Windows
    steps:
      - uses: actions/checkout@v4
      - name: Install PLC++ compiler via package manager
        run: |
          tcpkg install TwinCAT.PlcPlusPlus.Compiler
      - name: Build
        run: tccompiler build --project ./src/PlcProject.plcproj --optimize
      - name: Test
        run: tccompiler build --project ./src/PlcProject.plcproj --run-tests
```

## Package Manager (`tcpkg`)
Build 4026 introduced `tcpkg` for modular TwinCAT component management. NuGet-compatible feeds; myBeckhoff account required for the default Beckhoff feed.

```bash
tcpkg list                                 # show installed packages
tcpkg search TwinCAT.PlcPlusPlus           # find available packages
tcpkg install TwinCAT.PlcPlusPlus.Compiler # install a component
tcpkg update                               # update all packages
# Enterprise: use a custom NuGet feed
tcpkg install MyCompany.PlcLib --source https://nuget.mycompany.com/v3/index.json
```

## Migration from Classic TwinCAT
Built-in converter handles XML-to-plain-text transformation and adjusts syntax for Edition 4 conformity.

1. Open existing `.plcproj` in TwinCAT XAE (Build 4026+)
2. Right-click PLC project > **Convert to PLC++**
3. Converter extracts ST from `.TcPOU` XML into plain `.st` files
4. Review compiler warnings — implicit type conversions that classic PLC allowed may need explicit casts
5. Both project types can coexist in the same solution during gradual migration

## Emergency Mode
Dedicated emergency program that executes separately from the normal PLC cycle. When triggered, the runtime switches to this code path for orderly machine shutdown.

```iecst
// Emergency program — runs ONLY on emergency trigger
// Separate from MAIN; guaranteed to execute even if MAIN faults
PROGRAM P_Emergency
VAR
    fbAxis1 : FB_DriveController;
    fbValve : FB_SafetyValve;
END_VAR

fbAxis1(eCommand := E_DriveCommand.QuickStop);   // controlled stop
fbValve(bClose := TRUE);                          // close safety valves
GVL_Status.bEmergencyActive := TRUE;              // signal HMI
```

## Secure Online Change
Classic online change can leave dangling pointers when memory layout shifts. PLC++ automatically adjusts all pointers and references — no application code changes needed.

```iecst
FUNCTION_BLOCK FB_DataProcessor
VAR
    refBuffer : REFERENCE TO ARRAY[1..100] OF LREAL;
    ptrConfig : POINTER TO ST_Config;
    // Classic PLC: online change may invalidate ptrConfig^ and refBuffer
    // PLC++: runtime auto-updates both to correct new addresses
END_VAR
```

This eliminates one of the most dangerous bug classes in classic TwinCAT deployments where online changes are frequent (e.g., commissioning).
