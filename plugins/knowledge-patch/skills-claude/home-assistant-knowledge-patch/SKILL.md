---
name: home-assistant-knowledge-patch
description: Home Assistant
version: 2026.7
license: MIT
metadata:
  author: Nevaberry
---


# Home Assistant Knowledge Patch

Use this skill for Home Assistant configuration, automations, templates, Assist, dashboards, backups, integrations, installation, and custom-integration work.

Start with the task index. When a task touches an existing configuration, entity, action, state comparison, unit comparison, or integration requirement, also read the migrations reference before proposing changes.

## Reference index

| Reference | Topics |
| --- | --- |
| [Automations, Templates, Assist, and AI](references/automations-templates-assist.md) | Automation and script behavior, purpose-specific triggers and conditions, templates, YAML, selectors, Assist, voice, AI Task, and editor tooling |
| [Backups, System Operations, and Installation](references/backups-system-installation.md) | Backup creation, encryption, storage, retention, restore, updates, Apps, logs, installation methods, runtimes, and web-server configuration |
| [Custom Integration Development](references/custom-integration-development.md) | Config flows, discovery models, entity and service APIs, frontend interfaces, and developer deprecations |
| [Dashboards, Cards, and Energy](references/dashboards-cards-energy.md) | Built-in dashboards, cards, graphs, Activity, Energy, resource monitoring, search, pickers, and UI organization |
| [Integrations, Devices, and Services](references/integrations-devices-services.md) | Integration availability, setup, device and service capabilities, protocols, networking, proxies, and discovery |
| [Migrations and Breaking Changes](references/migrations-breaking-changes.md) | Removed integrations and interfaces, state and unit changes, renamed values, requirements, authentication, polling, and behavior changes |

## Working method

1. Identify whether the request is about a new configuration, an upgrade, existing behavior, or custom-integration development.
2. Open the matching topic reference from the index.
3. For upgrades and exact comparisons, cross-check the migrations reference.
4. Preserve the precise machine value, key name, action name, unit, minimum version, and conditional wording given in the reference.
5. Do not invent a replacement when an entry only states that behavior changed or an interface was removed.

## Breaking changes first

### Supported installation methods

Home Assistant Core and Supervised installations and the `i386`, `armhf`, and `armv7` architectures no longer receive updates, including security updates.
Migrate affected systems to a supported installation method and architecture.

Container images use `zstd` compression. Updating requires Docker 23.0.0 or newer or containerd 1.5.0 or newer, unless the older runtime otherwise supports `zstd` images.

See [Backups, System Operations, and Installation](references/backups-system-installation.md).

### Purpose-specific automation keys

Purpose-specific triggers and conditions are the automation editor's default
starting point. Existing automations, generic building blocks, templates, and
YAML continue to work without migration.

Old preview keys that were renamed no longer work. Reselect and save affected
blocks in the editor or replace the YAML keys, including:

```text
battery.low                 -> battery.became_low
battery.not_low             -> battery.no_longer_low
lawn_mower.docked           -> lawn_mower.returned_to_dock
schedule.turned_off         -> schedule.block_ended
schedule.turned_on          -> schedule.block_started
timer.time_remaining        -> timer.remaining_time_reached
update.update_became_available -> update.became_available
vacuum.docked               -> vacuum.returned_to_dock
climate.target_humidity     -> climate.is_target_humidity
climate.target_temperature  -> climate.is_target_temperature
```

See [Automations, Templates, Assist, and AI](references/automations-templates-assist.md).

### Kelvin-only light color temperature

Light actions no longer accept the mired-based `color_temp`. The `color_temp`,
`kelvin`, `min_mireds`, and `max_mireds` state attributes are removed. Use
`color_temp_kelvin`, `min_color_temp_kelvin`, and
`max_color_temp_kelvin` instead.

LIFX action data likewise uses `color_temp_kelvin` rather than `color_temp` or
`kelvin`:

```yaml
color_temp_kelvin: 3000
```

See [Migrations and Breaking Changes](references/migrations-breaking-changes.md).

### Modern template configuration

Legacy template entities under the individual `alarm_control_panel`,
`binary_sensor`, `cover`, `fan`, `light`, `lock`, `sensor`, `switch`, `vacuum`,
and `weather` platform keys are removed. Migrate them under modern `template:`
configuration.

A template binary sensor whose state template returns `None` becomes `unknown`,
not `off`; return `False` explicitly for `off`. A template fan state template
returning `None` also produces `unknown`, while a syntax error makes the fan
`unavailable`.

See [Automations, Templates, Assist, and AI](references/automations-templates-assist.md)
and [Migrations and Breaking Changes](references/migrations-breaking-changes.md).

### Device and entity targeting

A physical device merged across multiple integrations is split into one device
entry per integration, with entities reassigned. Review device-ID-based
automations when a Repair appears. Custom integrations should migrate away from
associating a device with multiple config entries.

Reolink Duo PoE and Duo WiFi cameras create one sub-device per lens. Existing
entity IDs and custom names remain, but device-targeted automations must target
the new lens sub-device.

See [Migrations and Breaking Changes](references/migrations-breaking-changes.md)
and [Integrations, Devices, and Services](references/integrations-devices-services.md).

### Removed battery properties

Many vacuum integrations remove the vacuum `battery_level` property in favor
of a dedicated battery sensor. This includes Ecovacs, Matter, Miele, Roborock,
Tuya, SwitchBot Bluetooth, LG ThinQ, Neato, Romy, Shark IQ, SwitchBot Cloud,
Template, TP-Link, and Xiaomi Miio. Update cards, templates, scripts, and
automations to use the dedicated sensor.

iCloud, StarLine, and Tractive device trackers also remove their `battery_level`
attribute in favor of dedicated battery sensors.

See [Migrations and Breaking Changes](references/migrations-breaking-changes.md).

### Failure and validation behavior

Supervisor actions such as `hassio.addon_start`, `hassio.backup_partial`, and
`hassio.host_reboot` raise on failure and stop scripts and automations by
default. Add `continue_on_error: true` only when continuation is required.

Webhook `local_only` accepts only the booleans `true` and `false`; replace
truthy values such as `1` or `"yes"`. Telegram bot actions reject undefined or
unused parameters.

See [Migrations and Breaking Changes](references/migrations-breaking-changes.md)
and [Backups, System Operations, and Installation](references/backups-system-installation.md).

### Service and server requirements

Check the migration reference before upgrading Z-Wave JS, UniFi Protect,
Paperless-ngx, BSB-LAN, pyLoad, Sentry, Zabbix, Mealie, or other version-gated
integrations. Notable current requirements in the reference include:

- Z-Wave JS uses `zwave-js-server` 3.9.0 or newer with schema 49.
- UniFi Protect requires version 7.1 or newer and uses its Public API.
- Paperless-ngx requires server version 2.19 or newer.
- BSB-LAN devices must use firmware supporting the version 2 API.
- pyLoad requires pyLoad-ng 0.5.0 or newer.

See [Migrations and Breaking Changes](references/migrations-breaking-changes.md).

## High-value features

### Backups and restore

Backups use AES-128 encryption by default with a mandatory generated key. The
key can be saved in an emergency kit and is required for restoration. Every
installation method can restore local, Cloud, or integration-provided backups.

Locations can have separate encryption and retention policies, except Cloud is
always encrypted. Downloads through the Home Assistant interface are delivered
unencrypted. Automatic schedules can select times and weekdays, and update
dialogs can create automatic backups before Core, Operating System, or App
updates as described in the reference.

The backup page distinguishes creation from upload and can show upload progress
per supported location.

See [Backups, System Operations, and Installation](references/backups-system-installation.md).

### Ask Question and AI Task

`assist_satellite.ask_question` lets an automation ask a question, define local
sentence patterns, and receive the matched answer ID and slots in a response
variable. Optional `preannounce` and `preannounce_media_id` fields can precede
the question.

`ai_task.generate_data` can send files or camera images to a provider and
return text or selector-defined structured data. Capable AI Task entities can
also call `ai_task.generate_image`; its response variable exposes the generated
asset through `url`.

See [Automations, Templates, Assist, and AI](references/automations-templates-assist.md).

### Area-aware cleaning and access control

`vacuum.clean_area` sends supported Matter, Ecovacs, and Roborock vacuums to
Home Assistant areas after map segments are associated with those areas. Voice
control can invoke the same mapped-area cleaning capability.

Matter lock pages provide **Manage lock** for users and PINs, including one-time
access. Z-Wave lock pages provide **Manage access** for users and credentials.
Both expose corresponding automation actions described in the integration
reference.

See [Integrations, Devices, and Services](references/integrations-devices-services.md).

### Infrared, radio, and serial proxies

Infrared and Radio frequency entity platforms let device integrations select a
transmitter. ESPHome supplies infrared transmitters and receivers and can proxy
common RF bands; Broadlink RF support is limited to 433 MHz RM4 Pro. An ESPHome
`serial_proxy` exposes a wired UART over the network and appears in the live
serial selector beside local USB ports.

See [Integrations, Devices, and Services](references/integrations-devices-services.md).

### Dashboards, Activity, and Energy

Overview is the default Home dashboard for new installations. Activity presents
Logbook data as a day-grouped timeline and can export CSV or clear and reset its
data. Built-in Maintenance and Security dashboards provide battery and security
views described in the dashboard reference.

Energy configuration accepts cumulative energy and live power sensors, supports
signed or paired positive grid and battery flows, and can weight combined
battery state of charge by assigned capacities. Gas, water, and electricity
views include live flow information where configured.

See [Dashboards, Cards, and Energy](references/dashboards-cards-energy.md).

### YAML and template authoring

UI code editors provide YAML and Jinja autocomplete, signatures, argument
placeholders, ID suggestions, hover details, and inline syntax and indentation
errors. UI YAML and template editors can also expand to full screen.

See [Automations, Templates, Assist, and AI](references/automations-templates-assist.md).

## Custom integration checks

For custom integration changes, read the developer reference before changing
discovery imports, config flows, device associations, entity services, units,
frontend components, storage serialization, or platform APIs.

Pay particular attention to these migrations:

- DHCP, SSDP, USB, and zeroconf `ServiceInfo` models moved.
- `UnitSystem` is frozen and must be treated as immutable.
- The `FlowResult` typed dictionary no longer has a `result` attribute.
- The legacy device-tracker platform API is deprecated.
- Entity IDs whose domains do not match their platforms are deprecated.
- Serial-based custom integrations must migrate from `pyserial` to the async
  `serialx` driver.
- Devices are being restricted to one config entry and at most one subentry.

See [Custom Integration Development](references/custom-integration-development.md).
