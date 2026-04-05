# Libraries & Placeholders

## Placeholder vs Direct Reference
Always prefer **placeholders** over direct library references. A placeholder maps a logical name to a resolved version, so dev/prod can resolve differently without changing `.plcproj` files.

Direct reference -- hardcodes a specific version:

```xml
<LibraryReference Include="Tc2_Standard,3.3.3.0,Beckhoff Automation GmbH"
                  Namespace="Tc2_Standard"
                  SystemLibrary="true" />
```

Placeholder with pinned version (production best practice):

```xml
<PlaceholderReference Include="Tc2_Standard">
  <DefaultResolution>Tc2_Standard, 3.3.3.0 (Beckhoff Automation GmbH)</DefaultResolution>
  <Namespace>Tc2_Standard</Namespace>
</PlaceholderReference>
```

Placeholder with always-newest (`*`) -- auto-upgrades to latest installed:

```xml
<PlaceholderReference Include="Tc3_JsonXml">
  <DefaultResolution>Tc3_JsonXml, * (Beckhoff Automation GmbH)</DefaultResolution>
  <Namespace>Tc3_JsonXml</Namespace>
</PlaceholderReference>
```

`DefaultResolution` format: `LibraryName, Version (Company)`. **WARNING:** `*` in production means a TwinCAT update can silently change library versions and break your program. Pin versions on production machines; use `*` only in development.

## Library Repository and Search Order

Libraries live on disk under the TwinCAT installation:

```
C:\TwinCAT\3.1\Components\Plc\Managed Libraries\
  Beckhoff Automation GmbH\Tc2_Standard\3.3.3.0\Tc2_Standard.compiled-library
  Beckhoff Automation GmbH\Tc3_EventLogger\3.2.25.0\Tc3_EventLogger.compiled-library
```

Multiple repositories are supported. When resolving, they are searched **in listed order** (PLC > Library Repository). First match wins. Add custom repos via Library Repository > Edit Locations > Add. Folder must follow the `Company\LibName\Version\` structure. Build 4026 added **activate/deactivate** per repository without removing them.

## Creating and Distributing Libraries

- **Export**: right-click PLC project > Save as library (`.library`) or compiled library (`.compiled-library`).
- **Install**: PLC > Library Repository > Install > browse to file. Appears in Managed Libraries.
- **Team distribution**: commit `.library` files to a shared git repo, add that folder as a Library Repository on each dev machine.

## Build 4026 Library Improvements

- **PLC project as referenced library**: use another PLC project directly as a dependency without exporting first.
- **Force Qualified_only**: project property forcing `Tc2_Standard.TON` instead of bare `TON`. Prevents symbol ambiguity.
- **Add library without placeholder**: separate command for direct refs vs placeholders.
- **Multiple selection** in Add Library dialog.

## Common Library Quick Reference

| Library | Purpose |
|---------|---------|
| `Tc2_Standard` | IEC 61131-3 FBs: TON/TOF/TP, CTU/CTD, R_TRIG/F_TRIG, string functions |
| `Tc2_System` | ADS communication, file I/O, memory copy, time conversion, task info |
| `Tc2_Utilities` | REAL/DWORD bit conversion, string formatting, CRC |
| `Tc2_MC2` | Motion control: MC_MoveAbsolute, MC_Power, MC_Home, axis FBs |
| `Tc3_Module` | Base classes for custom TcCOM drivers |
| `Tc3_EventLogger` | Structured alarms: FB_TcMessage, FB_TcAlarm, EventClasses |
| `Tc3_JsonXml` | FB_JsonSaxWriter, FB_JsonDomParser, XML DOM |
| `Tc3_IotBase` | MQTT: FB_IotMqttClient for broker publish/subscribe |

## Using a Library in Structured Text

```iecst
VAR
    fbAlarm : Tc3_EventLogger.FB_TcAlarm;  // qualified -- avoids symbol collision
    fbTimer : TON;                          // unqualified -- OK if no collision
END_VAR

fbTimer(IN := bTrigger, PT := T#5S);
IF fbTimer.Q THEN
    fbAlarm.Raise(0);
END_IF
```
