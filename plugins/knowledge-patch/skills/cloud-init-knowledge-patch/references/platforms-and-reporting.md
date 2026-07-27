# Platforms and Reporting

This reference covers platform detection, Raspberry Pi behavior, and reporting
changes from batch `26.1`.

## Newly detected platforms

Cloud-init detects the Tilaa cloud platform. Integrations targeting Tilaa should
check the built-in detection before retaining a local datasource or platform
detection workaround.

Cloud-init also detects s390x LXD environments. Architecture-specific LXD image
logic should allow the built-in detection path to run rather than assuming LXD
detection is unavailable on s390x.

These are detection additions. They do not imply that the two environments
share configuration or datasource behavior.

## Raspberry Pi support

Raspberry Pi platform support includes three positive integration features:

- keymap handling
- USB-gadget handling
- a systemd network service template

Image builders and platform integrations should account for these built-in
features before adding replacement platform scripts or service templates.

### Platform defaults

Cloud-init changes two generic behaviors for Raspberry Pi:

- fallback network configuration is disabled;
- APT mirror configuration is removed.

An absent fallback network configuration is therefore expected on this
platform. Diagnose the intended platform configuration instead of assuming that
generic fallback generation failed.

Likewise, an absent APT mirror configuration can be the result of the
platform-specific removal. Do not re-add generic mirror data without deciding
that the image requires behavior different from the Raspberry Pi default.

### Image review checklist

When preparing a Raspberry Pi image:

1. Check whether keymap handling already meets the image requirement.
2. Check whether USB-gadget handling overlaps local boot scripts.
3. Use or deliberately replace the provided systemd network service template.
4. Supply intentional networking rather than depending on fallback network
   configuration.
5. Treat APT mirror configuration as absent unless the image explicitly adds
   its own policy.

This keeps platform defaults and image policy separate and avoids duplicating
the new built-in handling.

## Finish-event duration

Reporting finish events include their duration. A consumer can obtain stage
timing directly from the finish event.

Event integrations should preserve the duration through each layer that handles
the event:

- decoding or parsing
- internal event representation
- persistence
- logging, metrics, or export

A consumer that previously derived timing from separate timestamps can use the
reported duration instead. When maintaining compatibility with older stored
events, handle the field according to the consumer's existing schema policy;
the current event itself provides the duration.

## Operational review

- Remove Tilaa detection workarounds only after confirming the built-in path is
  used by the target image.
- Let s390x LXD environments reach the built-in detection logic.
- Avoid duplicating Raspberry Pi keymap, USB-gadget, or systemd network-template
  behavior.
- Do not depend on generic fallback networking or APT mirror generation on
  Raspberry Pi.
- Preserve finish-event duration so stage timing remains available to event
  consumers.
