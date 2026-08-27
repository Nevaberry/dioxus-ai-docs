# Application Evolution and Profiles

The `6.7.0-6.8.5` source batch is organized here by application-maintenance
task rather than as a release inventory.

## Modernized WinForms architecture

The 6.7 line retained the two-process AgIO plus AgOpenGPS design while changing
the development baseline:

- projects use SDK style;
- x86 builds were removed;
- shared facilities moved into `AgLibrary`;
- logging was centralized.

Review extensions coupled to the 6.6.x project structure or internal classes.
The WPF example did not change production guidance away from WinForms. When a
deployment must use the 6.7 line, prefer 6.7.1 because it corrects several
6.7.0 behaviors.

## Section timing and machine nudge

Section control became switch-based in 6.7. Machine nudge is custom PGN 222.
From 6.8.1 onward, section processing runs at a fixed 10 Hz, independently of
the render-frame rate. Diagnose section latency against that processing loop,
not display performance.

## Deployment and operator capabilities

6.8.0 made the desktop line 64-bit-only and overhauled configuration and
profile workflows. It also added or expanded:

- track import and boundary creation from tracks;
- AgShare;
- headland detection and hotkeys;
- field input/output and ISOXML support;
- AgDiag diagnostics;
- an updater with rollback;
- Smart WAS zero calibration.

Account for the 64-bit requirement in packaging, dependencies, and support
instructions.

## Independent configuration domains

Starting in 6.8.2, settings no longer live in one vehicle file. Vehicle and
implement profiles can be selected and recombined independently:

```text
VehicleProfiles/{name}.xml  # steering, IMU, GPS, hardware brand
ToolProfiles/{name}.xml     # sections, tramlines, relays, Arduino Machine
Environment/environment.xml # display, sound, window position
```

The converter reads legacy profiles from `Vehicles/` and can convert without
a tool profile. In 6.8.3, profile switching first saves the current profile,
and nudge step size is stored per tool. Migration code must preserve each
domain separately and tolerate a missing legacy tool.

## ISOBUS Task Controller transport

The ISOBUS Task Controller added in 6.8.2 launches through AgIO. It communicates
with AgOpenGPS over the existing UDP/custom-PGN channel. Integrations should
follow the repository's PGN framing rather than assume that Task Controller
traffic uses a separate application transport.

## Easy Drive lifecycle

Easy Drive, added in 6.8.4, provides quick guidance without creating a field.
It deliberately:

- uses a rigid single-section tool;
- disables field-dependent features;
- writes no session data to disk;
- restores the original vehicle and tool settings when exited.

Treat it as temporary runtime state, not a shortened normal field workflow.

## Maintained classic line

Feature development moved to the Avalonia rewrite after 6.8.2, and 6.8.3
marked WinForms maintenance-only. Critical fixes nevertheless continued in
6.8.4 and 6.8.5. Use an official unprefixed release tag rather than a moving
branch and prefer 6.8.5 for a 6.8 deployment.

AgValoniaGPS and AgOpenWeb are separate version lines. Do not compare their
date-like internal versions numerically with 6.8.x.

## Data-preserving fixes

In 6.8.5, AgShare downloads preserve local `Sections.txt`, Flags, Headland,
and Contour data rather than replacing them with empty placeholders. The same
release restores the original path when an already-triggered U-turn is
cancelled and accepts comma-decimal locales for Drive In distance.
