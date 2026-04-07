# Local Reference & Orphan Mode

## activate Option on local Directive (4.6)

Prevents the local reference from activating until the root distance first drops below the specified threshold (in seconds). Ensures a server has successfully synced to an upstream source at least once before it begins serving time locally.

```
local stratum 10 orphan distance 0.1 activate 0.5
```

With `activate 0.5`, the local reference remains inactive until chrony achieves a root distance under 0.5 seconds — confirming at least one successful upstream sync.

## waitsynced / waitunsynced on local Directive (4.7)

Control the timing of local reference activation and deactivation:

- **`waitsynced N`** — minimum seconds after the last clock update before activating the local reference
- **`waitunsynced N`** — minimum seconds without clock updates before deactivating the local reference

```
# Activate local only after 2h of stable sync, deactivate after 5min unsynced
local stratum 10 orphan distance 0.0 waitsynced 7200 waitunsynced 300
```

These options add hysteresis to prevent the local reference from flapping on/off with intermittent connectivity.

## Combined Pattern: Robust Local Stratum Server

For a server that must serve local time but should only do so after confirming upstream connectivity, combine all three options:

```
server ntp.upstream.com iburst
local stratum 10 orphan distance 0.0 activate 0.5 waitsynced 7200 waitunsynced 300
```

Behavior:
1. `activate 0.5` — local reference stays inactive until root distance first drops below 0.5s (initial upstream sync confirmed)
2. `waitsynced 7200` — even after activation threshold is met, wait 2 hours of continuous sync before serving local time
3. `waitunsynced 300` — if upstream is lost, keep serving local time for 5 minutes before deactivating

This prevents a freshly booted server from immediately serving unsynchronized time to clients.
