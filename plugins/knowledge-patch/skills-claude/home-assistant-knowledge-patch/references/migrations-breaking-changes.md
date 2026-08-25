# Migrations and Breaking Changes

Use the version attributions on individual entries when exact behavior matters.

## Removed integrations, entities, attributes, and actions

### Counter unit removal (2025.1)

1-Wire and FXCOM RFXtrx counter entities no longer report `count` as a unit of measurement.

### devolo Home Control URL option removal (2025.1)

The development-only option for overriding the mydevolo URL has been removed from devolo Home Control.

### Removed integration entities and attributes (2025.2)

Ecovacs removes main-brush, side-brush, and filter lifespan attributes in favor of dedicated sensors, while Litter-Robot removes vacuum extra-state attributes already migrated to sensors. Home Connect appliances may lose a power entity when their API omits the setting, and IMGW-PIB removes its flood alarm, flood alarm level, flood warning, and flood warning level entities.

### GPSD attribute removal (2025.3)

The deprecated attributes of the GPSD main sensor have been removed; use the dedicated sensor entities introduced in 2024.9.

### Authentication-failure notification removal (2025.4)

An integration authentication failure no longer creates a persistent notification with the ID `config_entry_reconfigure`. Automations triggered by that notification must use another signal.

### Google Calendar action removal (2025.7)

The deprecated Google Calendar `add_event` action is removed. Automations and scripts must use the entity-based `create_event` action instead.

### Plex client-scan action removal (2025.7)

The deprecated `plex.scan_for_clients` action is removed. Use the Plex **Scan Clients** button entity in automations and scripts instead.

### Vacuum battery-property removal (2025.8)

Ecovacs, Matter, Miele, Roborock, and Tuya vacuum entities remove their battery property in favor of a dedicated battery-level sensor. Update templates, cards, scripts, and automations to use that sensor; vacuum battery properties are deprecated at the platform API level.

### 1-Wire raw-value removal (2025.9)

The deprecated `raw_value` attribute has been removed from 1-Wire entities. Update any templates, automations, or exports that read it.

### Removed integration entities and attributes (2025.10)

Home Connect removes the alarm-clock time entity in favor of its number entity, and ZHA removes the unpopulated `target_lift_position` and `target_tilt_position` cover attributes. Shelly Gas removes `Detected` and `Self test` attributes in favor of dedicated entities; Shelly Air removes the Lamp Life entity's `Operational hours` attribute, which now requires a template entity if still needed.

### ONVIF preset speed default removal (2025.11)

The `Speed` parameter for ONVIF `GoToPreset` is now optional, but omitting it no longer supplies the former `0.5` default. Set `speed` to `0.5` explicitly when that behavior is required.

### Removed and suppressed integration entities (2025.11)

Xbox removes the non-updating **Account tier**, **Gold tenure**, **In party**, and **In multiplayer** entities. Renault no longer creates entities inferred from unsupported functionality, so previously present invalid entities can disappear.

### Hive security entity removal (2025.12)

Hive has removed security-product support from its API, so Home Assistant no longer provides Hive alarm-control-panel entities.

### Tailscale hairpinning sensor removal (2026.1)

The Tailscale **Supports hairpinning** binary sensor has been removed because the upstream API no longer supplies the value.

### Tractive sensor removals (2026.2)

Tractive no longer provides the `activity`, `calories burned`, or `sleep` sensors because its API removed them. Update dashboards, automations, scripts, and templates that reference those entities.

### Removed entities, attributes, and actions (2026.3)

Snapcast group media-player entities and Snapcast-specific grouping actions are removed. StarLine engine-switch `ignition` and `autostart` attributes move to binary sensors, while Tado removes mobile-device tracking and its device-tracker entities.

### Litter-Robot night-light removal (2026.4)

The deprecated Litter-Robot 4 night-light mode switch is removed. Replace any remaining references with the select entity introduced in 2025.10.

### Tuya and Z-Wave removals (2026.4)

Tuya removes deprecated valve-control switch entities in favor of valve entities. The hidden YAML-enabled Z-Wave Installer panel is also removed; use the equivalent functionality in Z-Wave JS UI.

### Removed template syntax and Velux action (2026.6)

Legacy template entities under the individual `alarm_control_panel`, `binary_sensor`, `cover`, `fan`, `light`, `lock`, `sensor`, `switch`, `vacuum`, and `weather` platform keys are removed; migrate them under modern `template:` configuration. The deprecated `velux.reboot_gateway` action is also removed in favor of the gateway's reboot button entity.

### Removed integrations (2026.7)

Acer projector, Ampio Smog, ATEN Rack PDU, Avi-on, BeeWi SmartClim, BlinkStick, Clementine, Dovado, ELIQ Online, Greenwave Reality, Logentries, Microsoft Face and its Detect/Identify integrations, MS Teams, Mycroft, SCSGate, ThermoWorks Smoke, Tikteck, UniFi LED, and Watson TTS are removed. Gitter's obsolete API integration is also removed, but Gitter is now discoverable as a virtual integration handled by Matrix.

### Integration option removals (2026.8.0)

AirNow removes and automatically discards the ineffective station-radius option. ScreenLogic removes its integration-specific polling interval; use Home Assistant's general polling customization or `homeassistant.update_entity` for a different refresh cadence.

### Ohme sensor removal and Paperless requirement (2026.8.0)

Ohme removes its misleading stored-energy estimate; use an Integration (Riemann sum) helper over a power sensor when an energy estimate is needed. Paperless-ngx now requires server version 2.19 or newer, including for compatibility with Paperless-ngx 3.0.

## State, value, unit, and entity migrations

### HomeWizard water-unit normalization (2025.1)

The HomeWizard Energy water-usage sensor changes from `l/min` to `L/min`; update exact unit comparisons in automations, scripts, and templates. Long-term statistics remain intact, and Repair issues guide the data update.

### UniFi Network device-state values (2025.1)

UniFi Network Device State sensors now expose translatable, lowercase machine values: `connected`, `pending`, `firmware_mismatch`, `upgrading`, `provisioning`, `heartbeat_missed`, `adopting`, `deleting`, `inform_error`, `adoption_failed`, `isolated`, and `unknown`. Update automations, scripts, and templates that compare the former title-cased values.

### KNX State Updater semantics (2025.2)

With State Updater disabled, KNX reads a `state_address` only once when connecting; when enabled, it also rereads an address after one hour without a received value. Existing settings should be reviewed because the option was previously not applied correctly.

### Pentair ScreenLogic state normalization (2025.2)

ScreenLogic dosing states change from title case to `dosing`, `mixing`, and `monitoring`. Climate `preset_mode` values are also lowercase and normalized, including `solar`, `solar_preferred`, `heater`, and `dont_change`; update exact comparisons.

### SmartThings entity and state migrations (2025.3)

Energy and power sensors are removed from switch devices that lack the corresponding capabilities. Many appliance, media, and robot-cleaner states were renamed to translatable values, so exact state comparisons must be reviewed.

### TechnoVE state rename (2025.3)

The TechnoVE status sensor value `high_charge_period` is now `high_tariff_period`; update exact comparisons in automations, scripts, and templates.

### Jewish Calendar state and attribute changes (2025.4)

In Israel, the holiday states change from `Simchat Torah` to `Shmini Atzeret, Simchat Torah`, and the 30th of Shvat now returns `Family Day, Rosh Chodesh`. The `type_id` state attribute is removed; use `type` instead.

### Patch-release entity and validation changes (2025.4)

As of 2025.4.1, the built-in Music Assistant player no longer creates a Home Assistant media-player entity, and SmartThings climate entities gain preset mode. Version 2025.4.2 permits equal minimum and maximum values in MQTT number configuration; 2025.4.4 creates Home Connect active- and selected-program entities only when the appliance exposes programs.

### NUT state and polling changes (2025.5)

Network UPS Tools status sensors separate multiple statuses with commas instead of spaces. The integration's scan-interval option is removed, polling defaults to 60 seconds, and custom intervals must use Home Assistant's integration-independent polling customization.

### Overkiz towel-dryer modes (2025.5)

For Atlantic Electrical Towel Dryers, Home Assistant `auto` now maps to Overkiz `auto`; the former `prog` behavior is available as a preset instead.

### Meater state normalization (2025.7)

Meater probe cook states are now lowercase machine values: `Not Started` becomes `not_started`, `Configured` becomes `configured`, `Started` becomes `started`, `Ready For Resting` becomes `ready_for_resting`, `Resting` becomes `resting`, `Slightly Underdone` becomes `slightly_underdone`, `Finished` becomes `finished`, `Slightly Overdone` becomes `slightly_overdone`, and `OVERCOOK!` becomes `overcooked`. Update exact state comparisons.

### Miele hob-state migration (2025.7)

Miele hob plate values `0` through `18` become `plate_step_0` through `plate_step_18`; `110` and `220` become `plate_step_warm`; and `117`, `118`, and `217` become `plate_step_boost`. Update automations and templates that compare these states.

### Media-player off-state migration (2025.8)

Android Debug Bridge, Apple TV, Cambridge Audio, LOOKin, Mediaroom, Roku, Snapcast, and Sony PlayStation 4 media players now report `off` where they previously reported `standby`. Update exact state comparisons; the platform-level `STANDBY` state is deprecated.

### Reolink Wi-Fi signal units (2025.8)

Reolink Wi-Fi signal strength changes from a 0–4 bar indicator to any dBm value from `-85` through `-30`. Rough old-to-new correspondences are `0`→`-85`, `1`→`-75`, `2`→`-65`, `3`→`-55`, and `4`→`-45` dBm.

### Whirlpool door-state split (2025.8)

Whirlpool washer and dryer door state moves from the main machine-state sensor to a binary sensor, while the main sensor retains only cycle states. Update automations and scripts to use the new door sensor.

### Micro-unit encoding changes (2025.9)

The encoding changed for `μSv/h`, `μS/cm`, `μV`, `μg/ft³`, `μg/m³`, `μmol/s⋅m²`, `μg`, and `μs`. Review exact unit consumers and exported state data such as InfluxDB series.

### KNX scene state updates (2025.9)

KNX scene entities now update their state when a scene is activated externally from the bus, not only when Home Assistant activates it. Automations observing scene state may therefore receive changes from external controllers.

### SIA alarm state mapping (2025.9)

SIA status code `CF` (armed with malfunctions) now maps to `armed_away` instead of `armed_custom_bypass`; update exact state comparisons.

### SwitchBot vacuum battery migration (2025.9)

SwitchBot Bluetooth vacuum entities now also remove the vacuum battery property in favor of a dedicated battery-level sensor. Update cards, templates, scripts, and automations to use that sensor.

### 2025.9.2 configuration and state corrections (2025.9)

As of 2025.9.2, Modbus accepts delays greater than one and non-integer `min_temp` and `max_temp` values for lights. Velux determines closed status from position percentage, which can change the state exposed to automations.

### Integration state semantics (2025.10)

Slide Local's **invert position** option now also inverts open/closed status, so automations around inverted covers may need adjustment. SmartThings renames the AC preset `windFree` to `wind_free`, and ZhongHong climate fan-mode values passed to `set_fan_mode` are now lowercase.

### Tibber 15-minute pricing (2025.10)

`tibber.get_prices` now returns 15-minute rather than hourly data, the `price_level` attribute is removed, and `intraday_price_ranking` is rescaled to the `(0,1)` range.

### Entity state and attribute migrations (2025.11)

Asuswrt device trackers remove `last_time_reachable`; use `last_changed` instead. An LG webOS TV entity without a turn-on automation trigger now becomes `unavailable` rather than `off`.

For zone-name-only mobile updates, custom-zone `person` and device-tracker states now use the friendly name, such as `School`, instead of the object ID `kids_school`. Nederlandse Spoorwegen changes its entity from a string to a timestamp entity.

### OralB machine-value normalization (2025.11)

OralB replaces spaces with underscores in toothbrush states, brushing modes, pressure values, and sectors. Examples include `flight menu` → `flight_menu`, `daily clean` → `daily_clean`, `button pressed` → `button_pressed`, and `sector 1` → `sector_1`; update exact comparisons throughout those value sets.

### Coolmaster fan-mode rename (2026.1)

Coolmaster climate entities now use `medium` instead of `med`; update action data and exact fan-mode comparisons.

### UniFi Protect select-state normalization (2026.1)

UniFi Protect select values now use translated snake-case machine states instead of mixed case, including `Mechanical` → `mechanical`, `Always` → `always`, and `AutoNoLEDsOn` → `auto_no_leds_on`. Update automations, scripts, and templates that set or compare chime, recording, infrared, status-light, HDR, doorbell-text, LCD-message, or other select values.

### VeSync fan-mode rename (2026.1)

VeSync changes the `advancedSleep` fan mode to `advanced_sleep`; update automations and scripts that set or compare it.

### Sensor-group unavailable and unknown states (2026.2)

A sensor group is now `unavailable` when every member is unavailable or absent from the state machine. Otherwise, with the default `ignore_non_numeric: false`, it is calculated only when every member exists and is numeric; a missing or nonnumeric member makes the group `unknown`.

### Tuya HVAC modes converted to presets (2026.2)

Duplicate Tuya HVAC modes are now presets, so affected automation and script calls must move from `set_hvac_mode` to `set_preset_mode`. Version 2026.2.1 also removes a redundant `off` preset.

### VeSync sleep-preset rename (2026.2)

The `advanced_sleep` preset introduced by the 2026.1 normalization is replaced by `sleep`. Update preset selections and exact comparisons in automations and scripts.

### Patch-release capability and state corrections (2026.3)

Versions 2026.3.1 and 2026.3.4 expand Miele steam-oven and oven program support, 2026.3.2 adds area-selector reordering, and Ness Alarm now polls every five seconds. Patch releases also correct state handling for legacy Z-Wave covers and speed mappings for specific GE/Jasco fans, so exact state or percentage checks for affected devices may change.

### Integration state migrations (2026.3)

BSB-Lan water heaters rename operation mode `on` to `performance`. Satel Integra binary sensors and switches now begin as `unknown` until the panel reports them instead of assuming `off`, and corrected Z-Wave fan scaling can change an exact value such as `67%` to `66%`.

### JVC Projector entity migration (2026.4)

Picture Mode and HDR Processing move from deprecated sensors to `select.jvc_projector_picture_mode` and `select.jvc_projector_hdr_processing`. Unreferenced disabled sensors are removed; referenced sensors remain temporarily with a Repair issue so automations, dashboards, scripts, and templates can migrate.

### MQTT entity-ID configuration (2026.4)

The deprecated MQTT `object_id` option is removed from YAML and ignored in discovery payloads. Use `default_entity_id` when suggesting an entity ID.

### Patch-release capability and state changes (2026.4)

Patch releases remove Transmission's port-forward sensor, enable SwitchBot Cloud Bot webhooks and Comelit force-alarm actions, add Matter dry/fan modes for Hisense air conditioners, and add missing Miele dishwasher and steam-oven codes. They also correct Z-Wave cover movement states and Gardena water state/device classes, so exact state or class assumptions for affected entities should be reviewed.

### Ring doorbell event rename (2026.5)

Ring doorbell event entities emit the standardized `ring` event instead of `ding`; update exact event matches.

### Entity value migrations (2026.6)

Certificate Expiry's `error` attribute now returns `None` rather than the string `"None"`, so templates should use `is none`. IronOS uptime changes from elapsed seconds to a startup timestamp, SmartThings media-player sources normalize `D.IN` to `digital_input` and `BT` to `bluetooth`, and Tuya now prefers the unit reported by its API over Home Assistant's default.

### Devices split by integration (2026.8.0)

A physical device previously merged across multiple integrations is automatically split into one device entry per integration, with its entities reassigned; device-ID-based automations and unusual setups may need review when a Repair appears. Custom integrations should migrate away from associating a device with multiple config entries because a device is being restricted to one config entry and at most one subentry.

### Gardena and Edifier state migrations (2026.8.0)

Gardena Bluetooth's valve `activation_reason` changes from free-form text to a fixed value set, so exact comparisons need updating. Corrected infrared mappings for Edifier R2000DB and R2730DB speakers migrate automatically, but automations built around the formerly incorrect buttons need review.

### Additional vacuum battery migrations (2026.8.0)

LG ThinQ, Neato, Romy, Shark IQ, SwitchBot Cloud, Template, TP-Link, and Xiaomi Miio vacuum entities remove the deprecated `battery_level` property; use each vacuum's dedicated battery sensor instead.

## Requirements, authentication, and compatibility

### Tesla Fleet OAuth credentials (2025.1)

Tesla Fleet no longer includes shared OAuth application credentials because Tesla ended open-source application registrations and moved to pay-per-use access.

### Zabbix minimum version (2025.1)

The Zabbix integration now uses the official Python API and requires Zabbix 5.0 or newer; Zabbix 4 and older are unsupported.

### Reolink password limit (2025.4)

Reolink passwords are now limited to 31 characters. Existing longer passwords trigger reauthentication and must be changed to work with the current Reolink API.

### La Marzocco firmware compatibility (2025.5)

La Marzocco now supports gateway firmware v5 and drops older firmware, but boiler temperatures, the shot timer, scales, steam-temperature control, and prebrew/preinfusion controls are unavailable.

### Patch-release compatibility corrections (2025.7)

As of 2025.7.2, the `hddtemp` deprecation is reverted. Version 2025.7.3 ignores an empty MQTT sensor unit of measurement, and 2025.7.4 keeps entities belonging to dead Z-Wave devices available and adds confirmation to Z-Wave USB migration.

### UniFi Protect minimum version and authentication (2025.8)

UniFi Protect versions below 6.0.0 are unsupported because the integration is moving to the Public API. On 6.0.0 or newer it attempts to create an API key automatically when the configured user has enough permission; failure starts reauthentication and requires the password and an API key.

### Z-Wave server requirements (2025.8)

Z-Wave JS now requires `zwave-js-server` 3.2.1 or newer with schema 44. Minimum packaged versions are Z-Wave JS add-on 0.20.0, Z-Wave JS UI add-on 4.8.0, or Z-Wave JS UI Docker 10.11.0.

### Patch-release compatibility (2025.8)

As of 2025.8.3, ESPHome 2025.8.0 is the minimum stable BLE version.

### Yale August OAuth migration (2025.9)

Yale August replaces unofficial authentication with OAuth against the official API. After upgrading, open the August integration, select **Reconfigure**, and complete the one-time sign-in flow.

### Polling and compatibility changes (2025.10)

HERE Travel Time's automatic polling interval increases from 5 to 30 minutes to fit one route within the new free Base Plan. Zabbix 5.0 is no longer officially supported, although existing connections are not immediately blocked.

### Integration compatibility and authentication (2025.11)

Mealie 1 is no longer supported; the integration requires Mealie 2 or later. Traccar Server replaces username/password authentication with an API token, so existing entries must generate a token and enter it through **Settings > Devices & services > Traccar Server > Reconfigure**.

### go2rtc debug authentication (2025.12)

Enabling the go2rtc debug UI now requires both a username and password.

### Self-hosted Sentry minimum version (2026.2)

The Sentry integration now requires a self-hosted Sentry server at version 20.6.0 or newer because it uses the `/envelope` endpoint. Hosted sentry.io users are unaffected.

### pyLoad API requirement (2026.4)

The pyLoad integration drops the deprecated 0.4.x API and now requires pyLoad-ng 0.5.0 or newer.

### BSB-LAN version 2 API requirement (2026.7)

BSB-LAN reduces support for the legacy version 1 JSON API; affected devices raise a Repair issue and must be upgraded to firmware supporting the version 2 API.

### Z-Wave JS server requirement (2026.7)

Z-Wave JS now requires zwave-js-server 3.9.0 or newer with schema 49: use Z-Wave JS app 1.4.0 or newer, Z-Wave JS UI Docker 11.19.1 or newer, or a self-managed server at 3.9.0 or newer.

## Configuration and behavior changes

### Strict HEOS grouping (2025.1)

Grouping Denon HEOS players now raises an exception when any member is not a valid HEOS player instead of silently dropping invalid or unknown members.

### LIFX color-temperature argument (2025.1)

LIFX actions no longer accept `color_temp` or `kelvin`; action data must use:

```yaml
color_temp_kelvin: 3000
```

### MQTT publish action fields (2025.2)

`mqtt.publish` no longer accepts `topic_template` or `payload_template`; put templates directly in `topic` and `payload`. Since 2025.2.1, `payload` may be omitted to publish an empty payload.

```yaml
actions:
  - action: mqtt.publish
    data:
      topic: "home/example/state"
      payload: "{{ states('sensor.example') }}"
```

### Home Connect restrictions (2025.3)

Programs without an `aiohomeconnect` program-key enumeration may no longer be exposed, and undocumented program or option keys no longer work in actions. Only one Home Connect config entry can now be configured.

### MQTT JSON light migration (2025.3)

Legacy `color_mode` support has been removed from MQTT JSON lights. YAML and discovery configurations still using the deprecated parameters must be updated; discovery use logs a warning.

### Proximity distance semantics (2025.3)

Proximity distance is now measured to the edge of a monitored zone, including its radius, rather than to the zone center. Adjust automations that depend on the former distance values.

### Synology DSM polling (2025.3)

The Synology DSM scan-interval option has been removed and polling now defaults to 15 minutes. Use Home Assistant's integration-independent polling customization when another interval is required.

### Theme and typography token migration (2025.5)

Legacy Polymer components and their `paper-*` CSS variables are removed, so custom cards and themes must migrate to the new `--ha-font-*` and `--ha-line-height-*` typography tokens. Notable mappings include `--code-font-family` to `--ha-font-family-code`, the old font-smoothing variables to `--ha-font-smoothing`, and `--paper-item-icon-color` to `--state-icon-color`.

### Integration attribute and device migrations (2025.5)

Deprecated 17TRACK entity attributes and Total Connect alarm-panel attributes are removed; use their dedicated sensors. AVM FRITZ!SmartHome merges all units of a physical device into one registry device, potentially changing device targets, while its climate extra-state attributes are deprecated in favor of dedicated entities and are scheduled for removal in 2025.11.

### Generic Thermostat boundary behavior (2025.5)

Generic Thermostat now turns its target switch on only after the current temperature moves outside the target range plus or minus its tolerances, not when the temperature is exactly at a boundary.

### HomeKit child-accessory names (2025.5)

Home Assistant-configured names now take precedence for HomeKit child accessories representing fan presets, media-player sources, power strips, and triggers; rename them in Home Assistant rather than HomeKit.

### Google Maps Travel Time API migration (2025.5)

The move from Google's Distance Matrix API to Routes API removes the `Destination addresses` and `Origin addresses` attributes. The sensor also polls every 10 minutes instead of every 5 minutes.

### Met Office DataHub migration (2025.6)

The Met Office integration moves from the retired Datapoint API to DataHub and requires a new API key with a Global spot dataset subscription. Forecasts become truly hourly, visibility becomes one precise meter-valued sensor, daily and three-hourly sensor sets are consolidated, and `Site ID`, `Site name`, and `Sensor ID` attributes are removed.

### Husqvarna Automower calendar summaries (2025.8)

Husqvarna Automower calendar-event summaries now prefix the summary with the device name. Update exact summary matching, especially in multi-mower automations.

### Alexa Devices sounds (2025.9)

The available sound list now matches the Alexa mobile app, so automations should verify that their selected sound remains available. The `variant` parameter is now optional.

### Label-target expansion (2025.10)

Service actions targeting a label now include configuration and diagnostic entities carrying that label; audit labeled entities so an action does not unexpectedly affect controls that were previously excluded.

### Motion Blinds tilt inversion (2025.11)

Motion Blinds tilt position now follows `0` = closed and `100` = open, so migrate positions with `new = 100 - old`. Automations that depended on the old orientation must also swap `open_cover_tilt` and `close_cover_tilt`.

### UniFi Protect vehicle events (2025.12)

The nonfunctional legacy license-plate sensor is removed and replaced by a **Vehicle Detection Event** entity with plate, vehicle type, color, and confidence data. The replacement event fires after a three-second delay to improve thumbnail and license-plate-recognition data quality, which timing-sensitive automations must allow for.

### Xbox media and count migrations (2025.12)

Xbox media-source identifiers have changed with the multi-account media-browser rewrite, so saved media-source IDs must be updated. The **following** and **followers** sensors no longer include friends in their counts.

### Telegram bot action validation (2026.1)

Telegram bot actions no longer accept undefined or unused parameters. Remove any fields that are not part of the supported notification-action schema.

### Patch-release integration behavior (2026.2)

As of 2026.2.1, Denon AVR media players map stopped playback to the `stopped` state. Version 2026.2.2 adds Miele TQ1000WP programs and phases, while 2026.2.3 adds Roborock region selection and Miele dishwasher program codes.

### Kelvin-only light color temperature (2026.3)

Light actions no longer accept the mired-based `color_temp`, and the `color_temp`, `kelvin`, `min_mireds`, and `max_mireds` state attributes are removed. Use `color_temp_kelvin`, `min_color_temp_kelvin`, and `max_color_temp_kelvin` instead.

### Gardena watering-finish migration (2026.5)

Gardena Bluetooth replaces its finish-watering binary sensor with a regular timestamp sensor. Update automations, scripts, and dashboards to reference the new entity.

### Strict webhook booleans (2026.5)

Webhook `local_only` now accepts only the booleans `true` or `false`; replace formerly accepted truthy values such as `1` or `"yes"`.

### Patch-release capability changes (2026.5)

Version 2026.5.1 adds option matching to to-do triggers and WiZ `wfsens` occupancy; 2026.5.2 adds Duco target-flow and mode-end sensors but removes its temperature sensors after a connectivity-library migration. Version 2026.5.3 adds CalDAV `uid` and `recurrence_id` values and more Overkiz tilt and stop controls, while 2026.5.4 adds missing Miele dishwasher codes.

### HDMI-CEC and ONVIF action semantics (2026.6)

HDMI-CEC `turn_off` now sends the standard standby command; the former vendor-specific behavior remains possible with `hdmi_cec.send_command` keypresses `0x44` then `0x6c`. An `onvif.ptz` call with `continuous_duration: 0` no longer sends Stop after ContinuousMove, so callers must stop it separately or provide a nonzero duration.

### Patch-release public behavior (2026.6)

Version 2026.6.3 makes `config_entry_attr` return enum values. Version 2026.6.4 corrects Growatt V1 `total_output_power` values that were 1,000 times too low, adds Subaru API generation 4 support, includes Sonos favorites in source lists while exposing source selection only when supported, and stops `zwave_js.set_credential` from validating the number of credential slots.

### Person and zone presence semantics (2026.7)

When a person's location comes from a presence scanner associated with Home, the person entity no longer reports the Home zone's coordinates; use its `in_zones` attribute for zone membership. Zone counts and `persons` now derive from `in_zones`, allowing one person in overlapping zones to count in each, while a position-aware tracker reports the smallest containing zone instead of the zone with the nearest center.

### Patch-release public behavior (2026.7)

Patch releases make HomeKit Controller doorbell event entities use the standardized `ring` event, restore SolarEdge energy-sensor units, fix Proximity matching against trackers with `in_zones`, and stop Teslemetry covers from reporting false open or closed states when data is absent. They also correct YoLink water-meter valve status, refresh App update entities after a store reload, and exempt certain protocol integrations from the entity limit.

### UniFi Protect public-API migration (2026.8.0)

UniFi Protect now requires version 7.1 or newer and removes unsupported AI Port devices and their diagnostic sensors. Detection binary sensors lose `event_score`; event IDs and detected types move to the new **Motion detection**, **Smart detection**, and **Sound detection** event entities, so affected automations need another filtering condition.

### Patch-release public behavior (2026.8.0)

Patch releases make SmartThings air conditioners use their cooling-setpoint range and convert streamed Teslemetry tyre pressure and isolation resistance to their declared units. They also report refused HomematicIP alarm activations, expose Tedee locks as `unknown` during calibration or updates, and retain delayed Israel Rail departures.
