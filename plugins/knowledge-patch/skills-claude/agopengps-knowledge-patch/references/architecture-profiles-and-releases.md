# Architecture, Profiles, and Classic Release Behavior

Versioned compatibility attribution: `6.7.0-6.8.5`.

## WinForms modernization

The 6.7 line retained the existing AgIO plus AgOpenGPS product split and kept
WinForms as the production architecture. It converted the projects to SDK style,
removed x86 builds, moved shared facilities into `AgLibrary`, and centralized
logging. A WPF example did not replace WinForms. Extensions coupled to 6.6.x
project locations or internals need compatibility review. Prefer 6.7.1 as the
6.7 baseline because it corrected multiple 6.7.0 behaviors.

The 6.8.0 release established a 64-bit-only deployment baseline and overhauled
configuration and profile workflows. It also added or expanded track import,
AgShare, boundary creation from tracks, headland detection, hotkeys, field I/O,
ISOXML support, AgDiag, updater rollback, and Smart WAS zero calibration.

## Machine switching and timing

Section control became switch-based in 6.7. Machine nudge is custom PGN 222.
Beginning in 6.8.1, section processing is scheduled at a fixed 10 Hz, independent
of the render loop. Diagnose and integrate section timing against that fixed
schedule rather than the display frame rate.

## Independent profiles

Starting in 6.8.2, a single vehicle file no longer owns all configuration.
Vehicle and implement profiles can be selected and recombined independently:

```text
VehicleProfiles/{name}.xml  # steering, IMU, GPS, hardware brand
ToolProfiles/{name}.xml     # sections, tramlines, relays, Arduino Machine
Environment/environment.xml # display, sound, window position
```

The converter reads legacy profiles from `Vehicles/` and allows conversion
without a tool profile. From 6.8.3, changing profiles first saves the currently
active profile. Nudge step size is stored per tool rather than globally.

## Task Controller transport

The ISOBUS Task Controller introduced in 6.8.2 launches through AgIO and talks
to AgOpenGPS over the existing UDP/custom-PGN channel. An integration should use
the repository's PGN protocol and must not assume a separate Task Controller
transport.

## Easy Drive lifecycle

Easy Drive, added in 6.8.4, is temporary guidance without creating a field. It
uses a rigid single-section tool, disables field-dependent features, writes no
session data to disk, and restores the original vehicle and tool settings when
the operator exits.

## Release and maintenance policy

Feature work moved to the cross-platform rewrite after 6.8.2, and 6.8.3 marked
WinForms as maintenance-only. WinForms was not frozen: critical fixes continued
in 6.8.4 and 6.8.5. Use an official unprefixed release tag rather than a moving
branch and prefer 6.8.5 for a classic 6.8 deployment. Treat AgValoniaGPS and
AgOpenWeb as separate release lines; their date-like versions are not comparable
to classic `6.8.x` versions.

## Field-data and turn fixes

In 6.8.5, AgShare downloads preserve local `Sections.txt`, Flags, Headland, and
Contour data rather than replacing those with empty placeholders. Cancelling an
already-triggered U-turn restores the original path. Drive In distance accepts
comma-decimal locales.

