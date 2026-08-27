# Breaking Changes and Migrations

Use this reference for removed behavior, state and unit migrations, minimum versions, compatibility corrections, and changed defaults. Entries are grouped by task; the parenthetical batch ID identifies when the guidance entered this patch.

## Changed semantics, defaults, and compatibility fixes

### Generic Thermostat boundary behavior (2025.5)

Generic Thermostat now turns its target switch on only after the current temperature moves outside the target range plus or minus its tolerances, not when the temperature is exactly at a boundary.

### HDMI-CEC and ONVIF action semantics (2026.6)

HDMI-CEC `turn_off` now sends the standard standby command; the former vendor-specific behavior remains possible with `hdmi_cec.send_command` keypresses `0x44` then `0x6c`. An `onvif.ptz` call with `continuous_duration: 0` no longer sends Stop after ContinuousMove, so callers must stop it separately or provide a nonzero duration.

### Integration compatibility and authentication (2025.11)

Mealie 1 is no longer supported; the integration requires Mealie 2 or later. Traccar Server replaces username/password authentication with an API token, so existing entries must generate a token and enter it through **Settings > Devices & services > Traccar Server > Reconfigure**.

### Kelvin-only light color temperature (2026.3)

Light actions no longer accept the mired-based `color_temp`, and the `color_temp`, `kelvin`, `min_mireds`, and `max_mireds` state attributes are removed. Use `color_temp_kelvin`, `min_color_temp_kelvin`, and `max_color_temp_kelvin` instead.

### LIFX color-temperature argument (2025.1)

LIFX actions no longer accept `color_temp` or `kelvin`; action data must use:

```yaml
color_temp_kelvin: 3000
```

### Patch-release compatibility corrections (2025.7)

As of 2025.7.2, the `hddtemp` deprecation is reverted. Version 2025.7.3 ignores an empty MQTT sensor unit of measurement, and 2025.7.4 keeps entities belonging to dead Z-Wave devices available and adds confirmation to Z-Wave USB migration.

### Person and zone presence semantics (2026.7)

When a person's location comes from a presence scanner associated with Home, the person entity no longer reports the Home zone's coordinates; use its `in_zones` attribute for zone membership. Zone counts and `persons` now derive from `in_zones`, allowing one person in overlapping zones to count in each, while a position-aware tracker reports the smallest containing zone instead of the zone with the nearest center.

### Proximity distance semantics (2025.3)

Proximity distance is now measured to the edge of a monitored zone, including its radius, rather than to the zone center. Adjust automations that depend on the former distance values.

### Strict HEOS grouping (2025.1)

Grouping Denon HEOS players now raises an exception when any member is not a valid HEOS player instead of silently dropping invalid or unknown members.

## Removals, deprecations, and minimum requirements

### 1-Wire raw-value removal (2025.9)

The deprecated `raw_value` attribute has been removed from 1-Wire entities. Update any templates, automations, or exports that read it.

### Authentication-failure notification removal (2025.4)

An integration authentication failure no longer creates a persistent notification with the ID `config_entry_reconfigure`. Automations triggered by that notification must use another signal.

### BSB-LAN version 2 API requirement (2026.7)

BSB-LAN reduces support for the legacy version 1 JSON API; affected devices raise a Repair issue and must be upgraded to firmware supporting the version 2 API.

### Counter unit removal (2025.1)

1-Wire and FXCOM RFXtrx counter entities no longer report `count` as a unit of measurement.

### devolo Home Control URL option removal (2025.1)

The development-only option for overriding the mydevolo URL has been removed from devolo Home Control.

### Google Calendar action removal (2025.7)

The deprecated Google Calendar `add_event` action is removed. Automations and scripts must use the entity-based `create_event` action instead.

### GPSD attribute removal (2025.3)

The deprecated attributes of the GPSD main sensor have been removed; use the dedicated sensor entities introduced in 2024.9.

### Hive security entity removal (2025.12)

Hive has removed security-product support from its API, so Home Assistant no longer provides Hive alarm-control-panel entities.

### Integration additions, setup, and removal (2025.7)

New integrations cover Altruist environmental sensors, PlayStation Network activity, Tilt Pi brewing measurements, and VegeHub garden monitoring and irrigation control. Telegram Bot can now be set up from the UI, while JuiceNet is removed because its API service shut down.

### Integration option removals (2026.8.0)

AirNow removes and automatically discards the ineffective station-radius option. ScreenLogic removes its integration-specific polling interval; use Home Assistant's general polling customization or `homeassistant.update_entity` for a different refresh cadence.

### Integration setup and removal (2025.9)

Bayesian can now be configured from the UI. Uonet+ Vulcan is removed because its changed API policy prohibits unofficial clients.

### Integration setup and removal (2026.6)

Elgato Avea, openSenseMap, and OPNsense can now be configured through the UI. The legacy Konnected integration is removed after its 2025.10 deprecation; affected hardware must migrate to ESPHome firmware.

### Integration setup and removals (2025.1)

Niko Home Control can now be configured from the UI. DTE Energy Bridge, Simulated, and Stookalert are removed; Stookwijzer is the suggested replacement for Stookalert.

### Integration setup and removals (2025.12)

DuckDNS can now be configured from the UI. Dominos Pizza and Flick Electric are removed, as are Bluetooth Tracker, CUPS, Decora, dlib Face Detect, dlib Face Identify, Eddystone Temperature, GStreamer, Keyboard, LIRC, Pandora, Raspberry Pi Camera, SMS, Snips, and TensorFlow because they are incompatible with supported installation methods.

### Integration setup and removals (2026.4)

Leviton Decora Wi-Fi and Orvibo can now be configured through the UI. BMW Connected Drive/Mini Connected, Duke Energy, and Tfiac are removed; BMW's server restrictions leave the CarData API as the alternative for eligible EU vehicles.

### Integration setup and removals (2026.5)

PJLink and Pico TTS can now be configured from the UI. LANnouncer is removed after its companion Android app became unavailable, and the unmaintained pilight integration is disabled until its dependency on `setuptools.pkg_resources` is removed.

### Integration setup and removals (2026.8.0)

AquaLogic and OpenWrt (luci) can now be configured through the UI. Permobil is removed without a replacement, while Volvo On Call is removed in favor of the newer Volvo integration.

### Litter-Robot night-light removal (2026.4)

The deprecated Litter-Robot 4 night-light mode switch is removed. Replace any remaining references with the select entity introduced in 2025.10.

### New and removed integrations (2025.6)

New integrations cover Alexa devices, Immich, Paperless-ngx, Probe Plus Bluetooth thermometers, Swing2Sleep Smarla cradles, and Zimi Cloud devices; Kaiser Nienhaus is available virtually through Motionblinds. RTSPtoWebRTC is removed and replaced by the go2rtc integration.

### New integrations, UI setup, and removals (2025.11)

New integrations add Actron Air, Sunricher DALI, Fing, Firefly III, iNELS, Lunatone Gateway, Meteo.lt, Nintendo Parental Controls, and OpenRGB. London Underground can now be configured from the UI; Vultr, IBM Watson IoT Platform, and Plum Lightpad are removed because their backing services or APIs are no longer functional.

### Ohme sensor removal and Paperless requirement (2026.8.0)

Ohme removes its misleading stored-energy estimate; use an Integration (Riemann sum) helper over a power sensor when an energy estimate is needed. Paperless-ngx now requires server version 2.19 or newer, including for compatibility with Paperless-ngx 3.0.

### ONVIF preset speed default removal (2025.11)

The `Speed` parameter for ONVIF `GoToPreset` is now optional, but omitting it no longer supplies the former `0.5` default. Set `speed` to `0.5` explicitly when that behavior is required.

### Plex client-scan action removal (2025.7)

The deprecated `plex.scan_for_clients` action is removed. Use the Plex **Scan Clients** button entity in automations and scripts instead.

### pyLoad API requirement (2026.4)

The pyLoad integration drops the deprecated 0.4.x API and now requires pyLoad-ng 0.5.0 or newer.

### Removed and suppressed integration entities (2025.11)

Xbox removes the non-updating **Account tier**, **Gold tenure**, **In party**, and **In multiplayer** entities. Renault no longer creates entities inferred from unsupported functionality, so previously present invalid entities can disappear.

### Removed entities, attributes, and actions (2026.3)

Snapcast group media-player entities and Snapcast-specific grouping actions are removed. StarLine engine-switch `ignition` and `autostart` attributes move to binary sensors, while Tado removes mobile-device tracking and its device-tracker entities.

### Removed integration entities and attributes (2025.10)

Home Connect removes the alarm-clock time entity in favor of its number entity, and ZHA removes the unpopulated `target_lift_position` and `target_tilt_position` cover attributes. Shelly Gas removes `Detected` and `Self test` attributes in favor of dedicated entities; Shelly Air removes the Lamp Life entity's `Operational hours` attribute, which now requires a template entity if still needed.

### Removed integration entities and attributes (2025.2)

Ecovacs removes main-brush, side-brush, and filter lifespan attributes in favor of dedicated sensors, while Litter-Robot removes vacuum extra-state attributes already migrated to sensors. Home Connect appliances may lose a power entity when their API omits the setting, and IMGW-PIB removes its flood alarm, flood alarm level, flood warning, and flood warning level entities.

### Removed integrations (2026.7)

Acer projector, Ampio Smog, ATEN Rack PDU, Avi-on, BeeWi SmartClim, BlinkStick, Clementine, Dovado, ELIQ Online, Greenwave Reality, Logentries, Microsoft Face and its Detect/Identify integrations, MS Teams, Mycroft, SCSGate, ThermoWorks Smoke, Tikteck, UniFi LED, and Watson TTS are removed. Gitter's obsolete API integration is also removed, but Gitter is now discoverable as a virtual integration handled by Matrix.

### Self-hosted Sentry minimum version (2026.2)

The Sentry integration now requires a self-hosted Sentry server at version 20.6.0 or newer because it uses the `/envelope` endpoint. Hosted sentry.io users are unaffected.

### Tailscale hairpinning sensor removal (2026.1)

The Tailscale **Supports hairpinning** binary sensor has been removed because the upstream API no longer supplies the value.

### Tractive sensor removals (2026.2)

Tractive no longer provides the `activity`, `calories burned`, or `sleep` sensors because its API removed them. Update dashboards, automations, scripts, and templates that reference those entities.

### Tuya and Z-Wave removals (2026.4)

Tuya removes deprecated valve-control switch entities in favor of valve entities. The hidden YAML-enabled Z-Wave Installer panel is also removed; use the equivalent functionality in Z-Wave JS UI.

### UniFi Protect minimum version and authentication (2025.8)

UniFi Protect versions below 6.0.0 are unsupported because the integration is moving to the Public API. On 6.0.0 or newer it attempts to create an API key automatically when the configured user has enough permission; failure starts reauthentication and requires the password and an API key.

### Vacuum battery-property removal (2025.8)

Ecovacs, Matter, Miele, Roborock, and Tuya vacuum entities remove their battery property in favor of a dedicated battery-level sensor. Update templates, cards, scripts, and automations to use that sensor; vacuum battery properties are deprecated at the platform API level.

### Z-Wave JS server requirement (2026.7)

Z-Wave JS now requires zwave-js-server 3.9.0 or newer with schema 49: use Z-Wave JS app 1.4.0 or newer, Z-Wave JS UI Docker 11.19.1 or newer, or a self-managed server at 3.9.0 or newer.

### Z-Wave server requirements (2025.8)

Z-Wave JS now requires `zwave-js-server` 3.2.1 or newer with schema 44. Minimum packaged versions are Z-Wave JS add-on 0.20.0, Z-Wave JS UI add-on 4.8.0, or Z-Wave JS UI Docker 10.11.0.

### Zabbix minimum version (2025.1)

The Zabbix integration now uses the official Python API and requires Zabbix 5.0 or newer; Zabbix 4 and older are unsupported.

## State, entity, attribute, and unit migrations

### Additional vacuum battery migrations (2026.8.0)

LG ThinQ, Neato, Romy, Shark IQ, SwitchBot Cloud, Template, TP-Link, and Xiaomi Miio vacuum entities remove the deprecated `battery_level` property; use each vacuum's dedicated battery sensor instead.

### Coolmaster fan-mode rename (2026.1)

Coolmaster climate entities now use `medium` instead of `med`; update action data and exact fan-mode comparisons.

### Entity state and attribute migrations (2025.11)

Asuswrt device trackers remove `last_time_reachable`; use `last_changed` instead. An LG webOS TV entity without a turn-on automation trigger now becomes `unavailable` rather than `off`.

For zone-name-only mobile updates, custom-zone `person` and device-tracker states now use the friendly name, such as `School`, instead of the object ID `kids_school`. Nederlandse Spoorwegen changes its entity from a string to a timestamp entity.

### Entity value migrations (2026.6)

Certificate Expiry's `error` attribute now returns `None` rather than the string `"None"`, so templates should use `is none`. IronOS uptime changes from elapsed seconds to a startup timestamp, SmartThings media-player sources normalize `D.IN` to `digital_input` and `BT` to `bluetooth`, and Tuya now prefers the unit reported by its API over Home Assistant's default.

### Gardena and Edifier state migrations (2026.8.0)

Gardena Bluetooth's valve `activation_reason` changes from free-form text to a fixed value set, so exact comparisons need updating. Corrected infrared mappings for Edifier R2000DB and R2730DB speakers migrate automatically, but automations built around the formerly incorrect buttons need review.

### Gardena watering-finish migration (2026.5)

Gardena Bluetooth replaces its finish-watering binary sensor with a regular timestamp sensor. Update automations, scripts, and dashboards to reference the new entity.

### Google Maps Travel Time API migration (2025.5)

The move from Google's Distance Matrix API to Routes API removes the `Destination addresses` and `Origin addresses` attributes. The sensor also polls every 10 minutes instead of every 5 minutes.

### HomeWizard water-unit normalization (2025.1)

The HomeWizard Energy water-usage sensor changes from `l/min` to `L/min`; update exact unit comparisons in automations, scripts, and templates. Long-term statistics remain intact, and Repair issues guide the data update.

### Integration attribute and device migrations (2025.5)

Deprecated 17TRACK entity attributes and Total Connect alarm-panel attributes are removed; use their dedicated sensors. AVM FRITZ!SmartHome merges all units of a physical device into one registry device, potentially changing device targets, while its climate extra-state attributes are deprecated in favor of dedicated entities and are scheduled for removal in 2025.11.

### Integration state migrations (2026.3)

BSB-Lan water heaters rename operation mode `on` to `performance`. Satel Integra binary sensors and switches now begin as `unknown` until the panel reports them instead of assuming `off`, and corrected Z-Wave fan scaling can change an exact value such as `67%` to `66%`.

### Integration state semantics (2025.10)

Slide Local's **invert position** option now also inverts open/closed status, so automations around inverted covers may need adjustment. SmartThings renames the AC preset `windFree` to `wind_free`, and ZhongHong climate fan-mode values passed to `set_fan_mode` are now lowercase.

### JVC Projector entity migration (2026.4)

Picture Mode and HDR Processing move from deprecated sensors to `select.jvc_projector_picture_mode` and `select.jvc_projector_hdr_processing`. Unreferenced disabled sensors are removed; referenced sensors remain temporarily with a Repair issue so automations, dashboards, scripts, and templates can migrate.

### KNX State Updater semantics (2025.2)

With State Updater disabled, KNX reads a `state_address` only once when connecting; when enabled, it also rereads an address after one hour without a received value. Existing settings should be reviewed because the option was previously not applied correctly.

### Meater state normalization (2025.7)

Meater probe cook states are now lowercase machine values: `Not Started` becomes `not_started`, `Configured` becomes `configured`, `Started` becomes `started`, `Ready For Resting` becomes `ready_for_resting`, `Resting` becomes `resting`, `Slightly Underdone` becomes `slightly_underdone`, `Finished` becomes `finished`, `Slightly Overdone` becomes `slightly_overdone`, and `OVERCOOK!` becomes `overcooked`. Update exact state comparisons.

### Media-player off-state migration (2025.8)

Android Debug Bridge, Apple TV, Cambridge Audio, LOOKin, Mediaroom, Roku, Snapcast, and Sony PlayStation 4 media players now report `off` where they previously reported `standby`. Update exact state comparisons; the platform-level `STANDBY` state is deprecated.

### Met Office DataHub migration (2025.6)

The Met Office integration moves from the retired Datapoint API to DataHub and requires a new API key with a Global spot dataset subscription. Forecasts become truly hourly, visibility becomes one precise meter-valued sensor, daily and three-hourly sensor sets are consolidated, and `Site ID`, `Site name`, and `Sensor ID` attributes are removed.

### Micro-unit encoding changes (2025.9)

The encoding changed for `μSv/h`, `μS/cm`, `μV`, `μg/ft³`, `μg/m³`, `μmol/s⋅m²`, `μg`, and `μs`. Review exact unit consumers and exported state data such as InfluxDB series.

### Miele hob-state migration (2025.7)

Miele hob plate values `0` through `18` become `plate_step_0` through `plate_step_18`; `110` and `220` become `plate_step_warm`; and `117`, `118`, and `217` become `plate_step_boost`. Update automations and templates that compare these states.

### MQTT JSON light migration (2025.3)

Legacy `color_mode` support has been removed from MQTT JSON lights. YAML and discovery configurations still using the deprecated parameters must be updated; discovery use logs a warning.

### NUT state and polling changes (2025.5)

Network UPS Tools status sensors separate multiple statuses with commas instead of spaces. The integration's scan-interval option is removed, polling defaults to 60 seconds, and custom intervals must use Home Assistant's integration-independent polling customization.

### OralB machine-value normalization (2025.11)

OralB replaces spaces with underscores in toothbrush states, brushing modes, pressure values, and sectors. Examples include `flight menu` → `flight_menu`, `daily clean` → `daily_clean`, `button pressed` → `button_pressed`, and `sector 1` → `sector_1`; update exact comparisons throughout those value sets.

### Patch-release capability and state changes (2026.4)

Patch releases remove Transmission's port-forward sensor, enable SwitchBot Cloud Bot webhooks and Comelit force-alarm actions, add Matter dry/fan modes for Hisense air conditioners, and add missing Miele dishwasher and steam-oven codes. They also correct Z-Wave cover movement states and Gardena water state/device classes, so exact state or class assumptions for affected entities should be reviewed.

### Pentair ScreenLogic state normalization (2025.2)

ScreenLogic dosing states change from title case to `dosing`, `mixing`, and `monitoring`. Climate `preset_mode` values are also lowercase and normalized, including `solar`, `solar_preferred`, `heater`, and `dont_change`; update exact comparisons.

### Ring doorbell event rename (2026.5)

Ring doorbell event entities emit the standardized `ring` event instead of `ding`; update exact event matches.

### SIA alarm state mapping (2025.9)

SIA status code `CF` (armed with malfunctions) now maps to `armed_away` instead of `armed_custom_bypass`; update exact state comparisons.

### SmartThings entity and state migrations (2025.3)

Energy and power sensors are removed from switch devices that lack the corresponding capabilities. Many appliance, media, and robot-cleaner states were renamed to translatable values, so exact state comparisons must be reviewed.

### SwitchBot vacuum battery migration (2025.9)

SwitchBot Bluetooth vacuum entities now also remove the vacuum battery property in favor of a dedicated battery-level sensor. Update cards, templates, scripts, and automations to use that sensor.

### TechnoVE state rename (2025.3)

The TechnoVE status sensor value `high_charge_period` is now `high_tariff_period`; update exact comparisons in automations, scripts, and templates.

### UniFi Network device-state values (2025.1)

UniFi Network Device State sensors now expose translatable, lowercase machine values: `connected`, `pending`, `firmware_mismatch`, `upgrading`, `provisioning`, `heartbeat_missed`, `adopting`, `deleting`, `inform_error`, `adoption_failed`, `isolated`, and `unknown`. Update automations, scripts, and templates that compare the former title-cased values.

### UniFi Protect public-API migration (2026.8.0)

UniFi Protect now requires version 7.1 or newer and removes unsupported AI Port devices and their diagnostic sensors. Detection binary sensors lose `event_score`; event IDs and detected types move to the new **Motion detection**, **Smart detection**, and **Sound detection** event entities, so affected automations need another filtering condition.

### UniFi Protect select-state normalization (2026.1)

UniFi Protect select values now use translated snake-case machine states instead of mixed case, including `Mechanical` → `mechanical`, `Always` → `always`, and `AutoNoLEDsOn` → `auto_no_leds_on`. Update automations, scripts, and templates that set or compare chime, recording, infrared, status-light, HDR, doorbell-text, LCD-message, or other select values.

### VeSync fan-mode rename (2026.1)

VeSync changes the `advancedSleep` fan mode to `advanced_sleep`; update automations and scripts that set or compare it.

### VeSync sleep-preset rename (2026.2)

The `advanced_sleep` preset introduced by the 2026.1 normalization is replaced by `sleep`. Update preset selections and exact comparisons in automations and scripts.

### Xbox media and count migrations (2025.12)

Xbox media-source identifiers have changed with the multi-account media-browser rewrite, so saved media-source IDs must be updated. The **following** and **followers** sensors no longer include friends in their counts.

### Yale August OAuth migration (2025.9)

Yale August replaces unofficial authentication with OAuth against the official API. After upgrading, open the August integration, select **Reconfigure**, and complete the one-time sign-in flow.
