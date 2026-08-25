# Devices, Energy, and Climate

## Robot Vacuum Cleaner

The SDK data model defines dedicated Robot Vacuum Cleaner operational states and
errors. Implementations should use these definitions rather than mapping the
device onto unrelated generic states (since sdk-1.4.2.0).

Sequential commands and job transitions have revised, more predictable
behavior. Implement the exact state-machine requirements from the authorized
specification and test plan (since 1.4.2).

## Scenes

Scenes have certifiable, standardized time-based behavior. Controllers can
define their own scenes and coordinate transitions with fewer commands (since
1.4.2).

## Closures

The SDK provides the Closure Dimension schema and generated code, server
support, and implementations for stop, step, set-target, move-to, and
dimension-control commands (since sdk-1.5.0.0).

Targets are rounded to the dimension's declared resolution. Motion commands
validate secure-state and latching constraints; applications must not bypass
those checks (since sdk-1.5.0.0).

The unified closure model composes sliding, rotating, and opening motions with
single-panel, dual-panel, or nested mechanisms. It can model shades, drapes,
awnings, gates, garage doors, and similar products while keeping position
reporting consistent (since 1.5).

## EVSE and bidirectional charging

The Energy EVSE implementation and tests provide groundwork for Plug and
Charge, RFID, and vehicle-to-everything features (since sdk-1.5.0.0).

Certifiable EV capabilities include state-of-charge reporting and bidirectional
charging (since 1.5). Treat the SDK groundwork and certifiable feature
requirements as separate maturity signals.

## Commodity, tariff, and smart metering

Commodity Metering includes schema and generated code, a server implementation,
a general example, and a tariff example. These are implementation starting
points for metered commodities and tariff data (since sdk-1.5.0.0).

The electrical-energy tariff device type distributes current and forecast
pricing, tariff, and carbon data for reporting or preference-aware scheduling.
Smart metering also covers historical data, time-varying tariffs,
grid-connection information, and power limits (since 1.5).

## Soil Measurement

Soil Measurement is code-driven and uses revised initial-value behavior.
Generated-code consumers and application initialization must account for both
changes (since sdk-1.5.0.0).

## Thermostats

Thermostat Suggestions are available in the data model and SDK, and thermostat
events appear in cluster XML for generated-code consumers (since
sdk-1.5.0.0).

Context-aware thermostats can evaluate suggestions against user preferences,
demand-response commitments, recent manual changes, and other context. Presets
can be time-bounded. When a thermostat declines a suggestion, it can return a
standardized explanation to the controller or user (since 1.6).

## Security sensors

Security sensors can expose current status and event history. Smoke and
carbon-monoxide alarms can also report that they are unmounted (since 1.6).

