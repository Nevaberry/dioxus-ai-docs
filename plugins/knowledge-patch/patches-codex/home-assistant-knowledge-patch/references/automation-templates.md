# Automations, Scripts, and Templates

Use this reference for automation building blocks and editor behavior, scripts, templates, helpers, selectors, and webhooks. Entries are grouped by task; the parenthetical batch ID identifies when the guidance entered this patch.

## Editors, blueprints, and selectors

### Automation editor context and notes (2026.6)

Floor, area, device, and label targets now show their expanded entity count, honor domain and device-class filters, and reveal the included entities when selected. Conditions show live pass, fail, neutral, or error badges in automations and dashboard visibility rules, while every trigger, condition, action, option, and script field can carry a note that survives duplication, export, and blueprint sharing.

### Automation editor refinements (2025.10)

The automation sidebar is resizable, and `Ctrl+V` pastes a previously copied block immediately below the selected block. Undo and redo retain up to 75 editing steps with `Ctrl+Z` and `Ctrl+Y`; the repeat chooser is split into fixed-count, until, while, and for-each blocks, but repeat YAML is unchanged.

### Automation editor sidebar (2025.9)

Selecting a trigger, condition, or action now opens its settings in a right-hand sidebar while preserving the automation overview. On small screens this becomes a resizable bottom sheet, and mobile editing now supports drag and drop.

### Blueprint device-model filtering (2025.4)

Blueprint device selectors can now filter eligible devices by model ID.

### Dashboard and automation editor improvements (2025.5)

Dashboard header badges can retain the default wrapping behavior or scroll horizontally. Automation and script editors keep structured controls around individual templated fields, and pasted YAML can be converted into UI form whether it contains a whole automation or a single trigger, condition, or action.

### Dashboard, unit, and selector additions (2026.1)

The Energy dashboard period picker is now fixed to the bottom of the screen, and the statistics graph card can open History with the same entities and time range. Picture-elements state badges accept a custom `name`, volume-flow-rate entities accept gallons per day, and custom integrations can offer a choose selector whose alternatives use different input types.

### Object selector extensions (2025.7)

Object selectors for integrations and blueprints can now expose fields and permit multiple selections.

## Templates, YAML, and helpers

### Active issues in templates (2025.12)

The `issues()` template function now returns only active issues; fixed issues are no longer included.

### Datetime-helper trigger offsets (2025.2)

Automation time triggers based on datetime input helpers now support offsets.

### Media search and template helpers (2025.5)

Media players gain the `media_player.search_media` action. Templates gain `device_name`, while `floor_id` and `area_id` also resolve configured aliases.

### MQTT and template device trackers (2026.6)

MQTT gains a message-expiry interval and extends subentry support to date, datetime, and time entities. Template entities now support the device-tracker platform, providing the modern replacement for the deprecated `device_tracker.see` action.

### Reloadable shell commands and template vacuum rooms (2026.5)

A new Shell Command reload action rereads its YAML without restarting Home Assistant. Template vacuums can expose room segments and a `clean_segment` action, allowing them to participate in area-based cleaning.

### Relocated tools, themes, and template previews (2026.2)

Theme selection moves to each user's profile and follows that user across signed-in devices, while Developer tools move under **Settings**. The template editor now shows a live inline result as a template is edited.

### Removed template syntax and Velux action (2026.6)

Legacy template entities under the individual `alarm_control_panel`, `binary_sensor`, `cover`, `fan`, `light`, `lock`, `sensor`, `switch`, `vacuum`, and `weather` platform keys are removed; migrate them under modern `template:` configuration. The deprecated `velux.reboot_gateway` action is also removed in favor of the gateway's reboot button entity.

### Template and dashboard utilities (2025.12)

Templates gain the `clamp`, `wrap`, and `remap` math functions. The Activity card can filter by state, Tile-card bar gauges accept `min` and `max`, and the Blueprints panel shows how many automations and scripts use each blueprint.

### Template binary-sensor `None` semantics (2025.8)

A template binary sensor whose state template returns `None` now becomes `unknown` instead of `off`. Return `False` explicitly when the intended state is `off`.

### Template entities and units (2025.9)

All modern template-entity YAML syntax can set a default entity ID, and the template integration can now create event and update entities. Volume-flow-rate entities also support `m³/min`.

### Template entity and filter additions (2025.6)

Modern-style YAML now supports template fans, locks, alarm control panels, and vacuums, while covers can be trigger-based. Trigger `for` clauses can use `trigger_variables`; templates also gain the `from_hex` filter, and `base64_encode` accepts both bytes and strings.

### Template entity configuration (2025.5)

Switch and light template entities can now be trigger-based, and cover template entities support modern YAML syntax.

### Template entity state restoration (2026.8.0)

Template fan, cover, and device-tracker entities now restore their previous state after a restart instead of starting without that state.

### Template fan error and unknown states (2026.3)

A template fan whose `state` template has a syntax error is now `unavailable`, and a syntax error in its `percentage` template yields `None` rather than `0`. A `state` template returning `None` now produces `unknown` instead of `off`.

### Template integration extensions (2025.7)

Variables, icons, and pictures can now be used across all compatible template platforms. Template alarm control panels, locks, vacuums, and fans can be trigger-based, and `label_description` returns a configured label's description.

### Template integration extensions (2025.8)

Trigger-based numeric template sensors can explicitly become `unknown`, and template locks support the `opening` state. Covers, fans, lights, locks, and vacuums can be configured in the UI; availability templates are available there across supported platforms; and alarm panels, fans, lights, locks, switches, and vacuums support all optimistic YAML modes.

### Template name and translation helpers (2026.4)

The new `state_attr_translated` template function retrieves translated values for attributes such as fan modes, HVAC actions, and presets. The new `entity_name` function returns an entity's name and is preferred over reading its `friendly_name` attribute directly.

### Template YAML and data helpers (2025.4)

Template lights and switches now support the modern YAML style. New template helpers include `combine`, `difference`, `flatten`, `intersect`, `union`, `symmetric_difference`, `shuffle`, `floor_entities`, `typeof`, and the `md5`, `sha1`, `sha256`, and `sha512` hashing functions.

### Timer, Matter, media, and template additions (2026.7)

A running timer's duration can now be changed from its dialog, and automation or script traces always include template errors. Matter adds soil-moisture sensors, media players gain a projector device class, template lights gain xy-color support, and Google Assistant can request vacuum cleaning for a specific mapped room.

## Triggers, conditions, actions, and script execution

### Automation and script metadata (2025.1)

When creating or renaming an automation or script, the editor can now set its description, category, labels, and areas directly.

### Automation and script variable scopes (2025.4)

A `variables` action in a nested scope now updates an existing variable in an outer scope; a newly named variable is created in the top-level script-run scope. Rename variables that previously relied on local shadowing.

```yaml
actions:
  - variables:
      x: 1
  - sequence:
      - variables:
          x: 2
          y: 3
  - action: persistent_notification.create
    data:
      message: "{{ x }}, {{ y }}"  # 2, 3
```

### Automation and sensor schema additions (2025.10)

Webhook triggers can template `webhook_id`, while lawn-mower entities gain voice intents for starting mowing and docking. Accepted units now include `MCF` for volume, `m/min` for speed, and `inH₂O` for pressure.

### Cross-domain purpose-specific automations (2026.4)

The Labs preview now offers triggers and conditions organized by real-world meaning across entity domains: doors, garage doors, gates, windows, motion, occupancy, temperature, humidity, illuminance, power, battery, air quality, and climate. They can target areas, floors, or labels, so a concept such as an upstairs window automatically includes matching binary sensors and covers.

### Discovery automation event (2025.5)

Device discovery no longer creates the `config_entry_discovery` persistent notification. Automations must trigger on the `config_entry_discovered` event instead.

### Duration-aware purpose-specific automations (2026.5)

State-based purpose-specific triggers gain a visual **for** duration across domains such as motion, occupancy, doors, lights, climate, and covers. Every Labs entity condition can likewise require that its state has held for a specified duration.

### Expanded domain-specific triggers and conditions (2026.4)

New purpose-specific coverage includes counter increment/decrement/reset/limit events, every cover type, generic event-entity events, remote on/off, schedule activity, select changes, to-do item changes, valve open/close, and water-heater modes. Input booleans can use switch triggers, input text can use text triggers, and moisture, humidifier, temperature, and text entities gain additional threshold or state conditions.

### Labs trigger behavior rename (2026.6)

Purpose-specific trigger behavior values change from `any` to `each` and from `last` to `all`, with `each` now the default. Existing preview automations must reselect the behavior in the editor or update those values in YAML.

### Media, camera, and automation integrations (2026.6)

Alexa Devices gains media-player entities for Echo playback, volume, and mute plus event entities for heard voice commands; Sonos gains cross-service media search. Reolink battery cameras can connect directly without a hub or NVR, although support is incomplete and a camera cannot use both connection methods simultaneously; Google Nest adds `nest.set_fan_timer`, OneDrive a delete action, and Portainer container-recreation actions.

### More purpose-specific automation building blocks (2026.5)

New conditions cover update availability, remote state, to-do-list completion, media-player mute state, and numeric volume; media players also gain playback, power, mute, and volume triggers. Timers gain started, paused, restarted, cancelled, finished, and time-remaining triggers, and standardized doorbell event entities gain a brand-independent doorbell-rang trigger.

### Person and tracker trigger rollback (2026.5)

Labs removes `entered_home`, `left_home`, `is_home`, and `is_not_home` from Person and Device Tracker pending cross-domain replacements. Existing preview automations must temporarily use ordinary state triggers or conditions against `home`.

### Purpose-specific automations become the default (2026.7)

Purpose-specific triggers and conditions have graduated from Labs and are now the automation editor's default starting point; existing automations, generic building blocks, templates, and YAML continue to work without migration. These building blocks can target areas, handle `unknown`, `unavailable`, and repeated event-entity events according to their purpose, and can now be supplied by integrations, including custom integrations.

### Purpose-specific key migrations (2026.7)

Several preview trigger and condition keys were renamed for consistency, and the old keys no longer work; reselect and save affected blocks in the editor or replace the YAML keys:

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

### Purpose-specific trigger expansion (2026.1)

The Labs preview adds triggers for button presses; device-tracker arrivals and departures, including first arrival and last departure; humidifier activity and humidity; lock state; scene activation; siren state; and available updates. Climate triggers now cover HVAC mode, target and current temperature, and humidity changes or threshold crossings, while light triggers cover brightness changes and thresholds; the automation flow also has a redesigned target summary.

### Purpose-specific triggers and conditions (2025.12)

A Labs preview lets domains such as Light, Climate, and Fan provide target-aware triggers and conditions instead of requiring generic state logic. Entity, device, area, and label targets are supported, so an automation can react when any matching light turns on or test whether any is on, while area targets automatically follow membership changes.

### Purpose-specific triggers and conditions (2026.2)

The Labs preview adds calendar event start/end, person home arrival/departure, and vacuum dock-return triggers. New conditions cover alarm-panel armed variants/disarmed/triggered; Assist-satellite activity; climate, humidifier, mower, lock, media-player, and vacuum states; and home/not-home or on/off checks for trackers, people, fans, sirens, and switches.

### Recorder statistics action (2025.6)

The new `recorder.get_statistics` action queries statistics directly from the recorder for use in automations and scripts.

### Script variable propagation (2025.3)

`wait` and `response_variable` values created in an inner script or automation scope now propagate outward even when that scope contains a `variables` action. A `response_variable` also propagates out of `parallel` sequences, so flows relying on the former isolation need adjustment.

### Strict webhook booleans (2026.5)

Webhook `local_only` now accepts only the booleans `true` or `false`; replace formerly accepted truthy values such as `1` or `"yes"`.

### Vibration and Moon automations (2026.8.0)

Purpose-specific vibration triggers now have matching vibrating and not-vibrating conditions. Moon adds a phase-change trigger and conditions for a particular phase or any phase.

### Weekdays in time triggers (2025.8)

Time triggers can now be restricted to specified weekdays, allowing a time-based automation to run only on selected days without a separate weekday condition.

### Zone-oriented purpose-specific automations (2026.6)

The Labs preview adds triggers for a person or device tracker entering or leaving any zone and for a zone becoming occupied or empty, plus matching in-zone, not-in-zone, occupied, and empty conditions. All eight building blocks support `for` durations and replace the home-only Person and Device Tracker options withdrawn in 2026.5.
