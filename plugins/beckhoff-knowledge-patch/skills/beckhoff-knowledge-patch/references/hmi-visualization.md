# HMI & Visualization

## TwinCAT HMI Architecture
TwinCAT HMI (TE2000) is an HTML5/JavaScript-based HMI framework integrated into Visual Studio. The HMI server communicates with PLC via ADS; browser clients render the UI. TypeScript support from HMI version 1.12+ (transpiled to JavaScript).

## Three Scripting Types
1. **Actions** -- Inline JavaScript in the Actions and Conditions Editor. No TypeScript. Simple one-liner event handling only.
2. **Functions** -- Standalone files registered with `TcHmi.Functions.registerFunction()`. Reusable in the editor and Properties window.
3. **Code-Behind** -- Separate files for complex global logic. Register control events by control ID independently of HMI pages.

## Code-Behind: Full Pattern

Every Code-Behind file wraps logic in an IIFE receiving `TcHmi`. The `onInitialized` event fires once at startup.

```javascript
(function (TcHmi) {
    var destroyOnInit = TcHmi.EventProvider.register(
        'onInitialized', function (e, data) {
            e.destroy(); // fires once -- free the listener
            var label = TcHmi.Controls.get('TcHmiTextblock_Status');
            if (label) { label.setText('HMI Ready'); }
        }
    );

    // Register a button press handler by control ID
    var destroyBtn = TcHmi.EventProvider.register(
        'TcHmiButton_Start.onPressed', function (evt, data) {
            TcHmi.Symbol.writeEx2('%s%PLC1.MAIN.bStart%/s%', true,
                function (d) {
                    if (d.error !== TcHmi.Errors.NONE)
                        console.error('Write failed:', d.error);
                });
        }
    );
})(TcHmi);
```

## Reading PLC Variables: `TcHmi.Symbol.readEx2()`

Symbol expression format: `%s%PLC1.MAIN.varName%/s%`. Callback receives `.error` and `.value`.

```javascript
TcHmi.Symbol.readEx2('%s%PLC1.MAIN.nTemperature%/s%', function (data) {
    if (data.error === TcHmi.Errors.NONE) {
        var display = TcHmi.Controls.get('TcHmiTextblock_Temp');
        if (display) { display.setText(data.value.toFixed(1) + ' C'); }
    } else {
        console.error('Read failed:', data.error);
    }
});
```

## Writing PLC Variables: `TcHmi.Symbol.writeEx2()`

```javascript
TcHmi.Symbol.writeEx2('%s%PLC1.MAIN.nSetpoint%/s%', 42, function (data) {
    if (data.error === TcHmi.Errors.NONE) {
        console.log('Setpoint written');
    } else {
        console.error('Write error:', data.error);
    }
});
```

## Promise Wrappers for Async/Await

Nested callbacks become unmanageable with multiple reads. Define these in a Code-Behind file for global access:

```javascript
function ReadFromServer(symbol) {
    return new Promise(function (resolve, reject) {
        new TcHmi.Symbol(symbol).readEx(function (data) {
            if (data.error === TcHmi.Errors.NONE) resolve(data.value);
            else reject(data.error);
        });
    });
}

function WriteToServer(symbol, value) {
    return new Promise(function (resolve, reject) {
        TcHmi.Symbol.writeEx(symbol, value, function (data) {
            if (data.error === TcHmi.Errors.NONE) resolve(data.error);
            else reject(data.error);
        });
    });
}
```

Usage -- sequential reads become flat:

```javascript
async function StartMotorIfSafe() {
    try {
        var doorClosed = await ReadFromServer('%s%PLC1.MAIN.bDoorClosed%/s%');
        var motorReady = await ReadFromServer('%s%PLC1.MAIN.bMotorReady%/s%');
        if (doorClosed && motorReady) {
            await WriteToServer('%s%PLC1.MAIN.bMotorStart%/s%', true);
        }
    } catch (err) {
        console.error('Motor start sequence failed:', err);
    }
}
```

## Live Variable Subscription

For continuous monitoring without declarative binding, poll with `setInterval` + `readEx2`:

```javascript
(function (TcHmi) {
    setInterval(function () {
        TcHmi.Symbol.readEx2('%s%PLC1.MAIN.nActualSpeed%/s%', function (data) {
            if (data.error === TcHmi.Errors.NONE) {
                var label = TcHmi.Controls.get('TcHmiTextblock_Speed');
                if (label) { label.setText(data.value + ' RPM'); }
            }
        });
    }, 500);
})(TcHmi);
```

## Symbol Binding in Markup

`%s%...%/s%` = mapped PLC/server symbols. `%pp%...%/pp%` = user control parameters. `%f%Fn(args)%/f%` = function binding.

```html
<!-- Bind textblock to PLC variable -->
<div id="TcHmiTextblock_Pressure" data-tchmi-type="tchmi-textblock"
     data-tchmi-text="%s%PLC1.MAIN.rPressure%/s%"
     data-tchmi-width="200" data-tchmi-width-unit="px">
</div>

<!-- Bind using a registered function (computed value) -->
<div id="TcHmiImage_Valve" data-tchmi-type="tchmi-image"
     data-tchmi-src="%f%GetValveImage(%s%PLC1.MAIN.nValveState%/s%)%/f%">
</div>
```

## Registering a Reusable Function

Registered functions become available in the graphical editor and in markup via `%f%FnName(args)%/f%`.

```javascript
(function (TcHmi) {
    var GetValveImage = function (nState) {
        switch (nState) {
            case 0: return 'Images/valve_closed.svg';
            case 1: return 'Images/valve_opening.svg';
            case 2: return 'Images/valve_open.svg';
            default: return 'Images/valve_unknown.svg';
        }
    };
    TcHmi.Functions.registerFunction('GetValveImage', GetValveImage);
})(TcHmi);
```

## Dynamic Control Creation with ControlFactory

Wait for the parent container's `onAttached` event before adding children.

```javascript
TcHmi.EventProvider.register('Desktop.onAttached', function (e, data) {
    var btn = TcHmi.ControlFactory.createEx(
        'tchmi-button', 'BtnEmergencyStop', {
            'data-tchmi-top': 100, 'data-tchmi-left': 50,
            'data-tchmi-width': 200, 'data-tchmi-height': 60,
            'data-tchmi-text': 'EMERGENCY STOP',
            'data-tchmi-background-color': { 'color': 'rgba(220,40,40,1)' }
        }
    );
    var desktop = TcHmi.Controls.get('Desktop');
    if (desktop && btn) { desktop.addChild(btn); }
});
```

## User Control Parameters

User controls are reusable components. Parameters use `%pp%ParamName%/pp%` binding. Each instance binds parameters to different PLC symbols.

```html
<!-- Inside UserControl "MotorPanel" definition -->
<div id="TcHmiTextblock_Name" data-tchmi-type="tchmi-textblock"
     data-tchmi-text="%pp%MotorName%/pp%"></div>
<div id="TcHmiGauge_Speed" data-tchmi-type="tchmi-linear-gauge"
     data-tchmi-value="%pp%ActualSpeed%/pp%"
     data-tchmi-end-value="%pp%MaxSpeed%/pp%"></div>

<!-- Instance on a page -- each motor gets its own PLC symbols -->
<div id="MotorPanel_1" data-tchmi-type="MotorPanel"
     data-tchmi-motor-name="Motor 1"
     data-tchmi-actual-speed="%s%PLC1.MAIN.stMotor1.nSpeed%/s%"
     data-tchmi-max-speed="3000"></div>
```

## Alarm and Event Display

TwinCAT alarms (from `TC3_EventLogger`) display via the `TcHmiEventGrid` control:

```html
<div id="TcHmiEventGrid_Alarms" data-tchmi-type="tchmi-event-grid"
     data-tchmi-width="800" data-tchmi-width-unit="px"
     data-tchmi-height="400" data-tchmi-height-unit="px"
     data-tchmi-server-domain="TcHmiEventLogger"
     data-tchmi-filter='[{"path":"severity","comparator":">=","value":2}]'>
</div>
```

Acknowledge alarms programmatically:

```javascript
TcHmi.Server.requestEx({
    'requestType': 'ReadWrite',
    'commands': [{
        'commandOptions': ['SendErrorMessage'],
        'symbol': 'TcHmiEventLogger.ConfirmAlarm',
        'writeValue': { 'eventId': alarmId }
    }]
}, null, function (data) {
    if (data.error !== TcHmi.Errors.NONE)
        console.error('Alarm confirm failed:', data.error);
});
```

## Data Storage: Symbol Types

- **Internal symbols** -- Client-side only, lost on refresh. Prefix: `%i%MyVar%/i%`.
- **Server symbols** -- Persisted to SQLite on HMI server. Prefix: `%s%TcHmiSrv.Config.MyVar%/s%`.
- **PLC symbols** -- Mapped ADS variables. Prefix: `%s%PLC1.MAIN.varName%/s%`.

## Historization

Built-in time-series historian records PLC values over time. Configure on any mapped symbol in HMI server config. Display via `TcHmiTrendLineChart` control. Storage defaults to SQLite; MS SQL Server supported for large-scale deployments.
