# ADS Protocol & .NET SDK

## Modern AdsClient API (v6.x)
The current .NET ADS API uses the sealed `AdsClient` class (namespace `TwinCAT.Ads`, NuGet package `Beckhoff.TwinCAT.Ads`). This replaces the legacy `TcAdsClient`. The `AdsClient` is `IDisposable` and supports both synchronous and async methods for all operations.

```csharp
using TwinCAT.Ads;

// Connect to local PLC runtime 1
using var client = new AdsClient();
client.Connect(AmsPort.PlcRuntime1);  // local, port 851

// Connect to remote PLC
client.Connect("5.1.2.3.1.1", 851);
// or: client.Connect(new AmsNetId("5.1.2.3.1.1"), 851);
```

## Two Access Patterns: Symbolic vs Handle-Based
**Symbolic access** (preferred) — read/write by variable path string, type-safe:

```csharp
// Read by symbol path — simplest approach
short nCounter = client.ReadValue<short>("MAIN.nCounter");
client.WriteValue("MAIN.nCounter", (short)42);

// Async variants
short val = await client.ReadValueAsync<short>("MAIN.nCounter", cancel);
await client.WriteValueAsync("MAIN.bEnable", true, cancel);
```

**Handle-based access** — create a handle once, read/write by handle (faster for repeated access):

```csharp
uint hCounter = client.CreateVariableHandle("MAIN.nCounter");
try
{
    short val = client.ReadAny<short>(hCounter);
    client.WriteAny(hCounter, (short)99);
}
finally
{
    client.DeleteVariableHandle(hCounter);
}
```

## C# ↔ PLC Data Type Size Mapping
PLC types have different sizes than C# defaults. Mismatches cause "parameter size not correct" exceptions.

| PLC Type | Size | C# Type |
|----------|------|---------|
| BOOL     | 1 byte | bool (or byte) |
| BYTE     | 1 byte | byte |
| INT      | 2 bytes | short (NOT int!) |
| DINT     | 4 bytes | int |
| LINT     | 8 bytes | long |
| REAL     | 4 bytes | float |
| LREAL    | 8 bytes | double |
| STRING(n)| n+1 bytes | string (specify length in args) |

## ADS Notifications (Change Subscriptions)
Register for value change notifications instead of polling. Use `AddDeviceNotificationEx` for typed notifications.

```csharp
// Subscribe to typed notifications
client.AdsNotificationEx += (s, e) =>
{
    short value = (short)e.Value;
    Console.WriteLine($"MAIN.nCounter changed: {value}");
};

uint notifHandle = client.AddDeviceNotificationEx(
    "MAIN.nCounter",
    new NotificationSettings(AdsTransMode.OnChange, 100, 0),  // cycleTime=100ms, maxDelay=0
    null,     // userData
    typeof(short));

// Later: cleanup
client.DeleteDeviceNotification(notifHandle);
```

`NotificationSettings` modes: `AdsTransMode.OnChange` (on value change), `AdsTransMode.Cyclic` (periodic regardless of change).

## RPC Method Invocation
Call PLC methods (on FBs with `{attribute 'TcRpcEnable'}`) remotely via ADS:

```csharp
// Call a method on an FB instance — returns the method's return value
object result = await client.InvokeRpcMethodAsync(
    "MAIN.fbMotor",    // FB instance path
    "Start",           // method name
    new object[] { },  // input parameters
    CancellationToken.None);
```

## Symbol Browsing
Browse all PLC symbols programmatically via `SymbolLoaderFactory`:

```csharp
using TwinCAT.Ads.TypeSystem;
using TwinCAT.TypeSystem;

var settings = new SymbolLoaderSettings(SymbolsLoadMode.Flat);
var loader = SymbolLoaderFactory.Create(client, settings);

foreach (ISymbol symbol in loader.Symbols)
{
    Console.WriteLine($"{symbol.InstancePath} : {symbol.TypeName} ({symbol.Size} bytes)");
}
```

## Reactive Extensions (Ads.Rx)
NuGet package `Beckhoff.TwinCAT.Ads.Reactive` adds Rx-style polling and notification observables:

```csharp
using TwinCAT.Ads.Reactive;

// Poll a value every 500ms as an IObservable<short>
IDisposable sub = client.PollValues<short>("MAIN.nCounter", TimeSpan.FromMilliseconds(500))
    .Subscribe(val => Console.WriteLine($"Value: {val}"));

// Poll ADS state
client.PollAdsState(TimeSpan.FromSeconds(1))
    .Subscribe(state => Console.WriteLine($"State: {state}"));
```
