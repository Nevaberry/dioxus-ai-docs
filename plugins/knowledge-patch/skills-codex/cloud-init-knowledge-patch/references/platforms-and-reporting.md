# Platforms and Reporting

Use this reference when diagnosing environment detection, building Raspberry
Pi images, consuming reporting events, or integrating boot analysis.

## Platform detection

### Tilaa

Since 26.1, cloud-init detects the Tilaa cloud platform. Before carrying a
local Tilaa detection workaround forward, check whether built-in detection
already covers the image and environment.

### s390x LXD

Since 26.1, cloud-init detects s390x LXD environments. Re-evaluate local
architecture-specific LXD detection logic before retaining it in an image.

## Raspberry Pi image behavior

Since 26.1, Raspberry Pi support includes:

- keymap handling
- USB-gadget handling
- a systemd network service template

Cloud-init also changes two defaults for this platform:

- fallback network configuration is disabled
- APT mirror configuration is removed

Account for those defaults when assembling or debugging a Raspberry Pi image.
The absence of generic fallback networking or emitted APT mirror configuration
is expected platform behavior, not by itself evidence of failed detection.

## Reporting integration

### Finish-event duration

Since 26.1, reporting finish events include their duration. Consumers can use
that field to obtain stage timing directly from the finish event rather than
reconstructing timing elsewhere.

When updating an event pipeline, retain the duration through:

- parsing
- storage
- export
- downstream stage-timing calculations

### Boot-analysis exit status

Since 26.2, `analyze_boot` returns an integer exit code. Callers can interpret
the result as a conventional process status.

Update integrations that ignored, loosely typed, or otherwise treated the
return as a non-status result. Preserve the integer through wrappers so calling
automation can make its normal success-or-failure decision.
