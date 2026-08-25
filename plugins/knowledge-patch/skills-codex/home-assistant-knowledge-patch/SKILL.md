---
name: home-assistant-knowledge-patch
description: Home Assistant
version: 2026.7
license: MIT
metadata:
  author: Nevaberry
---


# Home Assistant Knowledge Patch

Use this skill when configuring, upgrading, automating, extending, or
troubleshooting a current Home Assistant installation. Start with the migration
checks below, then open the task-specific reference before changing YAML,
entity assumptions, integrations, dashboards, backups, or custom code.

## Reference index

| Reference | Topics |
| --- | --- |
| [Assist, Voice, and AI](references/assist-ai.md) | Assist pipelines, satellites, speech, conversation agents, AI Tasks, and intents |
| [Automations, Scripts, and Templates](references/automation-templates.md) | Triggers, conditions, actions, variable scope, templates, helpers, selectors, and editors |
| [Backups, Installation, and System Operations](references/backup-system.md) | Backup encryption and retention, restore, supported installations, Apps, runtime, networking, and updates |
| [Breaking Changes and Migrations](references/breaking-changes.md) | Removed APIs and entities, renamed states, unit changes, minimum versions, defaults, and patch corrections |
| [Dashboards and User Interface](references/dashboards-ui.md) | Built-in dashboards, cards, pickers, Activity, energy views, search, and navigation |
| [Custom Integration and Frontend Development](references/integration-development.md) | Config flows, entity APIs, discovery, services, selectors, frontend interfaces, and custom panels |
| [Integrations, Devices, and Protocols](references/integrations-devices.md) | Integrations, device capabilities, actions, sensors, Matter, MQTT, Z-Wave, KNX, ESPHome, IR, RF, and Bluetooth |

## Upgrade triage

Before an upgrade or migration:

1. Create and verify a restorable backup, including its encryption key and all
   configured destination uploads.
2. Confirm that the installation method, CPU architecture, container runtime,
   integrations, device firmware, and protocol servers remain supported.
3. Search YAML, templates, dashboards, and exported state consumers for removed
   fields, old service data, renamed states, exact units, and device IDs.
4. Inspect Repairs after startup; several device, backup, entity, and mapping
   migrations deliberately surface there.
5. Reauthenticate or reconfigure integrations whose login method, API, server
   minimum, or setup flow changed.
6. Run representative automations and inspect traces, especially flows using
   nested variables, response data, labels, Supervisor actions, or exact states.
7. Review disabled-by-default replacement entities before deleting compatibility
   templates or legacy references.

Open [Breaking Changes and Migrations](references/breaking-changes.md) for the
complete migration inventory rather than treating these checks as exhaustive.

## Installation and backup essentials

- Home Assistant OS and Container are the supported installation paths. Core,
  Supervised, and the retired 32-bit architectures do not receive updates or
  security fixes.
- Current container images use `zstd`; an old Docker or containerd runtime may
  fail before Home Assistant starts.
- Backups use a mandatory encryption key by default. Preserve the emergency kit:
  a stored encrypted backup is not useful without the key.
- Retention is destination-specific. Automatic cleanup does not delete manual
  backups, but update backups and scheduled backups have their own retention
  behavior.
- A backup can finish creation while uploads are still running. Check each
  location's upload status before restarting, replacing hardware, or removing
  the source installation.
- A requested restart waits for an active backup, while Supervisor action
  failures now stop scripts unless the action explicitly permits continuation.
- Home Assistant OS calls managed sidecar software **Apps**. Do not confuse an
  App, which runs alongside Core, with an integration, which connects devices or
  services to Home Assistant.

See [Backups, Installation, and System Operations](references/backup-system.md)
for location behavior, restore paths, update safeguards, logging, and web-server
configuration.

## High-impact YAML and entity migrations

### Use Kelvin color temperature

Light actions and state consumers should use:

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.desk
    data:
      color_temp_kelvin: 3000
```

Do not rely on mired-based `color_temp`, `min_mireds`, or `max_mireds` fields.
Use `min_color_temp_kelvin` and `max_color_temp_kelvin` where limits matter.

### Use modern template configuration

Legacy template platforms under domain keys have been removed. Define supported
template entities beneath `template:` and account for explicit `unknown` and
`unavailable` behavior. In particular, returning `None` is not equivalent to a
false or off state for binary sensors and fans.

### Update MQTT configuration

- Put templates directly in `mqtt.publish` `topic` and `payload`; the old
  `topic_template` and `payload_template` fields are gone.
- Use `default_entity_id` instead of the removed MQTT `object_id` option.
- Modern MQTT setup and tools live on the integration's Configure page; broker
  reconfiguration is in the integration-entry context menu.
- Migrate old JSON-light color-mode parameters and legacy platform assumptions.

### Treat machine states as machine data

Many integrations moved display-oriented values to lowercase snake case, split
attributes into dedicated entities, or changed `off`, `standby`, `unknown`, and
`unavailable` semantics. Prefer stable entity capabilities and translated UI
labels for presentation. Audit every exact string comparison after an upgrade.

### Read battery sensors

Vacuum and device-tracker battery properties have broadly moved to dedicated
battery sensor entities. Cards, templates, automations, and scripts should target
those sensors instead of entity attributes or platform properties.

### Review device targets

Sub-devices and one-device-per-integration ownership can change registry device
IDs while preserving entity IDs. Prefer entity, area, or label targets when they
match the intent, and repair device-ID-based targets after a registry split.

## Automation guidance

- Purpose-specific triggers and conditions are the editor default. Generic state
  triggers, templates, existing automations, and YAML still work.
- Purpose-specific blocks understand relevant `unknown`, `unavailable`, target,
  repeated-event, and cross-domain semantics. Recreate preview-era blocks whose
  keys or target behavior changed.
- A label target can include configuration and diagnostic entities. Expand and
  audit broad targets before invoking actions with side effects.
- Nested `variables`, `wait`, and `response_variable` results can propagate to an
  outer script-run scope. Do not depend on former local shadowing.
- Response actions and AI Tasks should always store their result in a named
  response variable before templates consume returned fields.
- Use `continue_on_error: true` only where proceeding after a failed action is an
  intentional workflow decision.
- Time triggers can use weekdays, datetime-helper triggers can use offsets, and
  purpose-specific state checks can require a duration.
- Automation and script notes survive duplication, export, and blueprint use;
  use them to record non-obvious target and failure behavior.

Open [Automations, Scripts, and Templates](references/automation-templates.md)
before rewriting templates, selectors, helper-driven triggers, or editor-produced
YAML.

## Frequently used capabilities

### Ask, generate, and continue conversations

Assist satellites can announce, start a conversation, and ask a question whose
matched answer and slots return to an automation. AI Task entities can generate
text, selector-defined structured data, or images from instructions and media
attachments. A configured default AI Task entity allows reusable calls to omit
the provider entity.

Conversation systems can stream responses, call tools, use exposed calendar or
to-do context, and continue listening after a question. Exposure and diagnostic
views matter: verify which entities, prompts, tools, arguments, and results enter
the conversation.

See [Assist, Voice, and AI](references/assist-ai.md) for action shapes,
satellite behavior, speech features, intents, and provider-specific changes.

### Clean mapped areas

Supported vacuums can map their segments to Home Assistant areas and use
`vacuum.clean_area` from automations or voice. Refresh mappings when a Repair
reports that the segment layout changed. Template vacuums can expose compatible
room segments and cleaning actions too.

### Use native infrared and radio-frequency proxies

Device integrations can select native IR or RF transmitters supplied by ESPHome,
Broadlink, or other supported integrations. A transmitter alone does not provide
an appliance protocol; the corresponding device integration must implement it.
IR receiver event entities can also turn original remote commands into automation
events.

### Model current energy and utility flow

Energy configuration accepts cumulative energy plus live power, signed flow or
separate import/export sensors, parent-child meters, downstream water meters, and
battery capacity and state-of-charge data. Configure device hierarchy and battery
capacity to avoid double counting and misleading aggregate charge percentages.

### Prefer entity-backed controls

Many former attributes and integration actions now have sensor, event, button,
switch, select, number, update, notification, or siren entities. Entity-backed
controls improve discoverability and targeting, but may require enabling a new
entity and migrating exact references.

Open [Integrations, Devices, and Protocols](references/integrations-devices.md)
for device coverage and protocol details.

## Dashboard and UI guidance

- Overview and the other built-in dashboards derive organization from areas,
  floors, labels, favorites, and primary sensors. Correct registry organization
  before compensating with card-specific configuration.
- Sections support backgrounds, spacing, auto height, sticky footers, strategies,
  and richer card interactions. Theme overrides may be needed where defaults
  changed.
- Energy, Activity, protocol, Maintenance, Security, and device-management views
  expose operational detail that previously required custom cards or developer
  tools.
- Target pickers show expanded entities for floors, areas, devices, and labels.
  Use that preview to audit broad actions and visibility conditions.
- Quick search covers navigation, commands, entities, devices, and areas; editor
  tooling adds YAML linting, Jinja completion, hover values, and full-screen views.

See [Dashboards and User Interface](references/dashboards-ui.md) before migrating
an Areas or Home dashboard, changing card layouts, or relying on old navigation.

## Custom integration checklist

- Validate imports for moved discovery models and removed typed-dictionary fields.
- Treat frozen core dataclasses as immutable and use current entity descriptions,
  features, units, and device classes.
- Migrate deprecated service registration helpers, device-tracker APIs, config
  entry listeners, trigger initialization flags, and platform-mismatched IDs.
- Do not assume one registry device can remain attached to multiple config entries.
- Test config-entry reconfiguration, unique IDs, subentries, backup-agent progress,
  OAuth errors, webhook reconfiguration, and update-coordinator retries.
- Update frontend cards and custom panels for current typography, safe-area,
  selector, dashboard-strategy, and entity-suggestion interfaces.

Open [Custom Integration and Frontend Development](references/integration-development.md)
for the detailed API and frontend migration notes.
