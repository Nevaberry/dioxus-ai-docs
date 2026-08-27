# Devices, Energy, and Closures

Use this reference for device-type state behavior, closure mechanisms, energy
and tariff features, metering, thermostats, soil measurement, and security
sensors.

## Robot Vacuum Cleaner

The SDK supplies dedicated Robot Vacuum Cleaner operational states and errors.
Implementations can use these definitions instead of inventing device-specific
state and error values (sdk-1.4.2.0).

Sequential-command and job-transition behavior is changed to make operations
more predictable. The exact state machine remains defined by the authorized
specification and test plan (1.4.2).

## Closure control

### SDK command and dimension support

The SDK adds the Closure Dimension schema, generated code, and server support.
It implements stop, step, set-target, move-to, and dimension-control commands.
Targets are rounded to the dimension's declared resolution. Motion validates
secure state and latching constraints (sdk-1.5.0.0).

### Modular mechanisms

The unified closure model composes reusable sliding, rotating, and opening
motions with single-panel, dual-panel, or nested mechanisms. The same model can
represent shades, drapes, awnings, gates, garage doors, and similar products
while keeping position reporting consistent (1.5).

## Electric-vehicle charging

The Energy EVSE implementation and tests add groundwork for Plug and Charge,
RFID, and vehicle-to-everything behavior (sdk-1.5.0.0).

Certifiable capabilities include electric-vehicle state-of-charge reporting
and bidirectional charging (1.5).

## Commodity metering

Commodity metering includes schema and generated code, a server
implementation, a general example, and a tariff example. Applications can use
these SDK components as the starting point for metered commodities and tariff
data (sdk-1.5.0.0).

## Electrical-energy tariff and metering

The electrical-energy tariff device type distributes real-time and forecast
pricing, tariff, and carbon data for reporting or preference-aware scheduling.
Smart-metering behavior also includes historical data, time-varying tariffs,
grid-connection details, and power limits (1.5).

Keep the device-type distribution behavior distinct from the SDK's general
commodity-metering examples.

## Soil Measurement

Soil Measurement becomes a code-driven cluster and has revised initial-value
behavior. Generated-code consumers must account for both changes
(sdk-1.5.0.0).

## Thermostats

### Suggestions and generated events

The data model and SDK add Thermostat Suggestions. Thermostat events are
represented in cluster XML for generated-code consumers (sdk-1.5.0.0).

### Context-aware control

Thermostats can evaluate suggestions against user preferences, demand-response
commitments, recent manual changes, and other context. Presets can be
time-bounded. A thermostat that declines a suggestion can return a standardized
explanation to the controller or user (1.6).

## Security sensors

Security sensors can expose current status and event history. Smoke and
carbon-monoxide alarms can also report that they are unmounted (1.6).
