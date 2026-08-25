# Integrations, Devices, and Protocols

Use this reference for new integrations, device capabilities, protocol support, actions, sensors, setup, and discovery. Entries are grouped by task; the parenthetical batch ID identifies when the guidance entered this patch.

## Device capabilities, actions, and services

### 2025.9.2 configuration and state corrections (2025.9)

As of 2025.9.2, Modbus accepts delays greater than one and non-integer `min_temp` and `max_temp` values for lights. Velux determines closed status from position percentage, which can change the state exposed to automations.

### Absolute-humidity device class (2025.8)

Sensor and number entities now support an absolute-humidity device class.

### Additional device capabilities (2026.3)

Compit adds water-heater, number, and binary-sensor platforms; Velux supports KLF 200 switches; BSB-Lan exposes current HVAC action and a clock-sync button; and Nintendo Parental Controls adds bedtime end time. Nanoleaf's library replacement also restores connectivity for newer Essentials devices affected by authorization errors.

### Additional integration capabilities (2025.6)

Homee gains fans and alarm control panels; Teslemetry gains hazard-light, valet-mode, and credit-balance entities; and SwitchBot gains vacuums plus Lock Ultra and Lock Lite. Squeezebox adds service-update entities, Sonos exposes playlists under favorites, Kostal Plenticore accepts installer login, Anthropic supports Claude 4, and Comelit climate entities gain preset modes.

### Alexa Devices sounds (2025.9)

The available sound list now matches the Alexa mobile app, so automations should verify that their selected sound remains available. The `variant` parameter is now optional.

### Area, group, and energy controls (2025.8)

The Areas dashboard can show an area's first camera, an image, or an icon on its card. Light and cover group dialogs expose controls for individual members, group members can be reordered, and the energy dashboard gains a flow visualization showing energy sources and destinations.

### Area-based vacuum cleaning (2026.3)

The new `vacuum.clean_area` action sends supported Matter, Ecovacs, and Roborock vacuums to one or more Home Assistant areas after the vacuum's map segments are associated with those areas in the entity settings. A changed segment layout raises a Repair issue so the mapping can be refreshed; voice commands for this are not yet available.

### Camera, media, and display controls (2026.3)

Reolink adds diagonal and continuous-rotation PTZ buttons, while UniFi Protect adds PTZ presets through `ptz_goto_preset` and a live patrol select. LG Soundbar gains play/pause, playback state, and track metadata; SwitchBot Cloud adds AI Art Frame controls and its current image; JVC Projector adds extensive picture, source, HDR, installation, and latency controls; and Cambridge Audio adds room-correction switching.

### Capacity-weighted battery charge (2026.8.0)

Energy Dashboard batteries can be assigned capacities so their combined state of charge is weighted by battery size; batteries without capacities continue to use a simple average.

### Climate, appliance, and energy capabilities (2026.8.0)

Overkiz adds contact and tilt sensors, towel-dryer controls, and Somfy Thermostat PRO; SwitchBot adds Candle Warmer Lamp, RGBIC Neon Rope Light, and Standing Fan controls; Roborock Q10 gains switches, a map, volume, and do-not-disturb; and Whirlpool adds oven light, cook-mode, and target-temperature controls. Enphase adds ACB battery sensors and sleep/wake controls, MELCloud and MELCloud Home expand heat-pump and energy controls, and Fronius, Tesla Wall Connector, Gardena Bluetooth, Duco, Victron BLE, and Ecowitt add new sensors, options, or device support.

### Device-tracker battery attributes (2026.7)

iCloud, StarLine, and Tractive device trackers remove their `battery_level` attribute. Update automations, scripts, templates, and cards to use each integration's dedicated battery sensor.

### Devices split by integration (2026.8.0)

A physical device previously merged across multiple integrations is automatically split into one device entry per integration, with its entities reassigned; device-ID-based automations and unusual setups may need review when a Repair appears. Custom integrations should migrate away from associating a device with multiple config entries because a device is being restricted to one config entry and at most one subentry.

### Energy device hierarchy (2025.4)

Energy configuration can define parent-child relationships between devices. When a parent meter's total includes a child's separately measured consumption, the energy dashboard uses the hierarchy to avoid double-counting it.

### Expanded device support (2025.2)

New integration coverage includes Shelly BLU TRV, HomeWizard Plug-In Battery, Vesync humidifiers, TP-Link vacuums, a Reolink baby-crying sensor, and Bang & Olufsen physical-button entities.

### Expanded integration capabilities (2025.11)

SwitchBot adds garage-door openers; Habitica adds notifications; VegeHub adds actuator switches; Portainer adds container controls and sensors; Volvo adds vehicle location and control buttons; and ElevenLabs adds speech-to-text. UniFi adds device LED control, OctoPrint adds tool- and bed-temperature controls, Niko Home Control adds scenes, Control4 adds climate devices, Growatt adds MIN/TLX inverter control and grid charging, and Telegram Bot adds inbound-message event entities.

Xbox adds game, avatar, and Gamerpic images; Victron Remote Monitoring adds solar-production forecasts for the energy dashboard; Shelly adds climate and valve entities; Reolink adds bicycle and person, vehicle, and animal-type detection; and Yardian adds binary sensors.

### Expanded integration capabilities (2025.5)

`openai_conversion.generate_content` accepts PDFs, conversation agents can retrieve to-do items, HomeKit Bridge supports air purifiers, YouTube can monitor the user's own channel, and HEOS can add or remove play-queue items. Mill adds energy statistics, and Synology DSM can monitor external USB drives.

### Expanded integration capabilities (2025.8)

PlayStation Network adds online, current-game, last-online, and PS Plus entities, notifications, friend status, and PS Vita support; Matter adds microwave-oven and temperature-control devices; WiZ and SwitchBot Cloud add fans; SmartThings adds vacuums; Velux exposes rain detection; Pi-hole supports API v6; and Reolink adds Wi-Fi signal, pre-recording, and post-recording controls. Immich gains a file-upload action, Russound RIO gains play-media support, AmberElectric adds forecasts, OSO Energy adds holiday and custom-away controls, Nord Pool adds a normalized-price-indices service, and KNX gains a searchable, filterable group monitor.

### Expanded integration controls (2025.7)

Music Assistant adds a button to favorite the currently playing queue item, external source, or radio station. HomeWizard adds battery group-mode charging and discharging control; Reolink adds IR brightness, baby-cry sensitivity, privacy-mask, and PoE/Wi-Fi floodlight controls; Russound RIO gains sub-devices and zone controls; and Matter adds dishwasher alarms and battery-storage capabilities.

### Expanded integration controls (2025.9)

Husqvarna Automower can reset blade-usage time and exposes error events; Reolink adds speak, doorbell-volume, and chime-silence controls; PlayStation Network can send direct-message notifications; and UniFi gains per-port enable and disable switches. OpenWeatherMap adds wind gusts, EZVIZ adds battery and online sensors, Russound RIO can browse saved presets, Awair adds absolute humidity, Teslemetry gains charging and preconditioning actions, and Enphase Envoy supports IQ Meter Collar and C6 Combiner devices.

### Expanded integration support (2025.3)

ESPHome adds an option to shadow-log a device's logs, and the OpenAI conversation integration adds the `o1`, `o1-preview`, `o1-mini`, and `o3-mini` models. Support also expands to Shelly Gen4 Flood and script-event entities, SwitchBot Remote, UniFi 9 zone-based rules, and Govee light effects.

### Expanded media and device controls (2026.5)

Apple TV adds keyboard text-input actions, Music Assistant exposes configurable number, text, switch, and select entities plus sound modes, and ESPHome water heaters gain away mode. Broadlink and SMLIGHT devices can act as native infrared emitters, WLED can freeze individual segments, and LG Netcast adds a remote-command action.

### Expanded playback, notification, and device support (2026.2)

ESPHome adds water-heater devices; Music Assistant supports pre-announce URLs; Spotify can play Liked Songs; Sonos exposes podcast favorites; Reolink adds a pet chime; and SmartThings adds audio notifications. LG ThinQ gains humidifier and dehumidifier control, while Hikvision gains camera and NVR snapshots and streams.

### Experimental Android wake-word detection (2026.3)

The Android Companion app can use on-device microWakeWord detection to open Assist, even while the phone is locked, for **Okay Nabu**, **Hey Jarvis**, or **Hey Mycroft**. Enable it under **Settings > Companion App > Assist for Android**; nearby satellites arbitrate so only the fastest responds, and notification-command automations can toggle detection to limit its significant battery use.

### Full-page ZHA device management (2026.7)

ZHA moves clusters, bindings, signature, and neighbors from the former dialog into a dedicated tabbed device-management page with a device summary and explicit loading, empty, and error states.

### Generic thermostat preset selection (2025.2)

Setting a Generic Thermostat temperature equal to one of its preset temperatures now automatically makes that preset active.

### go2rtc debug authentication (2025.12)

Enabling the go2rtc debug UI now requires both a username and password.

### Group assumed-state propagation (2025.11)

Switch, fan, light, and cover groups now have an assumed state of `true` when at least one child has an assumed state. Code and UI that inspect group uncertainty can no longer assume it is always false.

### Home Connect restrictions (2025.3)

Programs without an `aiohomeconnect` program-key enumeration may no longer be exposed, and undocumented program or option keys no longer work in actions. Only one Home Connect config entry can now be configured.

### HomeKit child-accessory names (2025.5)

Home Assistant-configured names now take precedence for HomeKit child accessories representing fan presets, media-player sources, power strips, and triggers; rename them in Home Assistant rather than HomeKit.

### Husqvarna Automower BLE setup (2025.9)

New Husqvarna Automower BLE setup requires the mower PIN, including for models and security levels that previously could not communicate reliably.

### Husqvarna Automower calendar summaries (2025.8)

Husqvarna Automower calendar-event summaries now prefix the summary with the device name. Update exact summary matching, especially in multi-mower automations.

### Integration actions and controls (2026.3)

Radarr adds `radarr.get_movies` and `radarr.get_queue` response actions, Mealie adds structured shopping-list retrieval, Renault adds horn and light-flash buttons, and Saunum adds a `start_session` action with duration, temperature, and fan-duration inputs. Portainer adds Docker stack monitoring/control and a `prune_images` action, while NRGkick can pause charging and Control4 can set thermostat fan mode.

### Integration capability additions (2026.7)

Alexa Devices adds announcement and communications switches plus Alexa shopping and to-do lists; SMTP gains notify entities, Environment Canada adds `get_alerts`, Green Planet Energy adds cheapest-price-period actions, and SwitchBot Cloud can upload AI Art Frame images. Other notable additions include Rexel Energeasy Connect through Overkiz's cloud and local APIs, Powerwall 3 support, a Wallbox schedule-resume button, a Yoto media browser and controls, Samsung infrared command buttons, and Imou live camera streaming.

### Integration device controls (2025.12)

Shelly Gen2+ Wi-Fi can be configured over Bluetooth, SwitchBot adds smart radiator thermostats, and Xbox adds multiple accounts and more remote/media controls. Reolink adds exposure and audio-noise controls; Ecovacs adds border-spin and auto-empty controls; VeSync adds child lock; Portainer exposes container resource usage; Volvo adds reduced guard mode; Plugwise adds Anna P1 and Adam zone profiles; Bang & Olufsen exposes Beoremote One buttons as events; and Niko Home Control, Saunum, and NASweb add climate, fan, and alarm-panel control respectively.

### Integration monitoring and configuration additions (2026.1)

FRITZ!SmartHome routines can be enabled or disabled through switch entities, and Ping adds a packet-loss percentage sensor that is disabled by default. HomeWizard adds zero-charge-only and zero-discharge-only battery modes, while KNX UI configuration expands to time, date, datetime, sensor, scene, text, and fan entities.

Squeezebox gains binary sensors for upcoming, active, and snoozed alarms plus a next-alarm timestamp. Hikvision adds NVR support with channel discovery and extended events, Pooldose gains water-meter sensors and dosing and operating-mode controls, and Nederlandse Spoorwegen replaces its monolithic sensor with more than 15 route-specific sensors.

### Integration platform and service additions (2025.12)

ESPHome can use Home Assistant's standard entity-ID generation, System Monitor adds fan and battery sensors, Tuya adds litter-box controls and doorbell events, and Home Connect adds air conditioners and microwaves. SQL queries can use templates, Prometheus exports `water_heater` metrics, Anthropic provides AI Task entities, and OpenAI Conversation supports GPT-5.1 models.

### Integration UI setup (2026.7)

SAJ Solar Inverter, SMTP, Swisscom Internet-Box, and UniFi AP can now be configured through the Home Assistant UI.

### Jewish Calendar state and attribute changes (2025.4)

In Israel, the holiday states change from `Simchat Torah` to `Shmini Atzeret, Simchat Torah`, and the 30th of Shvat now returns `Family Day, Rosh Chodesh`. The `type_id` state attribute is removed; use `type` instead.

### La Marzocco firmware compatibility (2025.5)

La Marzocco now supports gateway firmware v5 and drops older firmware, but boiler temperatures, the shot timer, scales, steam-temperature control, and prebrew/preinfusion controls are unavailable.

### Label-target expansion (2025.10)

Service actions targeting a label now include configuration and diagnostic entities carrying that label; audit labeled entities so an action does not unexpectedly affect controls that were previously excluded.

### LLM calendar access and fallback history (2025.2)

LLM-based conversation agents can retrieve today's and this week's events from calendar entities that have been exposed to Assist. The default local agent and its LLM fallback now share command history, so a fallback can resolve references from earlier locally handled commands.

### Mandatory encryption and universal restore (2025.1)

All backups now use AES-128 encryption by default with a mandatory generated encryption key, which can be saved in an emergency kit and is required for restoration. Restore is now supported by every installation method, including Container installations, and can read local, Cloud, or integration-provided backup locations.

### Media, vehicle, and service capabilities (2026.8.0)

Reolink adds pre-siren entities and a motion class for AI-detection sensors; WiiM adds multi-room grouping; Portainer adds update and health entities; MikroTik, Imou, Steam, and LG Infrared add platforms or device support; and the OpenAI conversation integration adds GPT-5.6. Vizio gains remote-command aliases, Teslemetry seat-cooler controls, Tessie a navigation-destination text entity, and OMIE an action for prices on a specified date.

### Media-player group controls (2025.6)

Media-player cards can directly join or unjoin player groups when the selected media-player integration supports grouping.

### Media-player Tile features (2026.5)

Media-player Tile cards gain source and sound-mode selectors. Their playback feature can now choose and reorder on/off, play, pause, play/pause, stop, previous, and next controls.

### Motion Blinds tilt commands (2026.4)

For tilt-capable devices that do not report an absolute tilt position, tilt-open and tilt-close now send jog-up and jog-down commands instead of attempting 0° and 180° positions. Automations that relied on the former absolute movement may need adjustment.

### Motion Blinds tilt inversion (2025.11)

Motion Blinds tilt position now follows `0` = closed and `100` = open, so migrate positions with `new = 100 - old`. Automations that depended on the old orientation must also swap `open_cover_tilt` and `close_cover_tilt`.

### New device and protocol support (2025.5)

Matter adds the 1.4 water-heater device type, Xiaomi BLE adds the Body Composition Scale S400, and SwitchBot adds Roller Shade and Hub Mini Matter devices.

### New energy, climate, and appliance integrations (2026.3)

New integrations add local monitoring for Homevolt batteries, Indevolt storage, and Powerfox Poweropti, plus Hypontech Cloud solar monitoring and Zinvolt battery data. Hegel Amplifier, IntelliClima ventilation, Liebherr refrigeration, MyNeomitis heating, and Trane Local thermostat control are also newly supported.

### Noteworthy integration capabilities (2025.10)

Philips Hue supports MotionAware sensors on Hue Bridge Pro; LG ThinQ adds energy sensors; AccuWeather adds hourly forecasts; Blue Current adds a start-charge action; Lutron Caseta emits multi-tap actions; and Reolink adds encoding selection, Home Hub sirens, and light color-temperature control. Shelly adds presence, zone, virtual-button, object-based, and Flood Gen4 cable-unplugged entities; Tasmota adds cameras; Workday adds a calendar; ntfy adds rich outbound notifications and inbound-topic events; and Matter adds occupancy hold time, heat/cool fan running state, and thermostat outdoor-temperature sensors.

### Notification and event entities (2026.5)

The Mobile App integration now exposes a notification entity per device, allowing phones and tablets to be grouped with the regular Group helper while retaining existing notify actions. HTML5 gains an event platform and `html5.send_message` entity action, and Transmission gains an event entity for torrent events.

### Opower returned-energy statistics (2025.5)

Opower separates negative consumption and cost into return and compensation statistics. Energy dashboards exporting to the grid must add `Opower {utility name} elec {account number} return` under **Return to grid** and use the corresponding `compensation` statistic for returned-energy compensation.

### Other integration capabilities (2026.4)

Roborock adds Q10 support, Govee BLE adds the H5140 CO2 monitor, Jellyfin adds shuffle and enqueue, and GitHub adds a merged-pull-request count sensor. Teslemetry gains a buy/sell tariff calendar, Cambridge Audio an equalizer switch, Gardena Bluetooth Aqua Contour and Precise devices, HDFury an audio-unmute offset, ToGrill alarm temperature ranges, and Smarla a spring-constellation status sensor.

### Overkiz towel-dryer modes (2025.5)

For Atlantic Electrical Towel Dryers, Home Assistant `auto` now maps to Overkiz `auto`; the former `prog` behavior is available as a preset instead.

### Patch-release capability and state corrections (2026.3)

Versions 2026.3.1 and 2026.3.4 expand Miele steam-oven and oven program support, 2026.3.2 adds area-selector reordering, and Ness Alarm now polls every five seconds. Patch releases also correct state handling for legacy Z-Wave covers and speed mappings for specific GE/Jasco fans, so exact state or percentage checks for affected devices may change.

### Patch-release capability changes (2026.5)

Version 2026.5.1 adds option matching to to-do triggers and WiZ `wfsens` occupancy; 2026.5.2 adds Duco target-flow and mode-end sensors but removes its temperature sensors after a connectivity-library migration. Version 2026.5.3 adds CalDAV `uid` and `recurrence_id` values and more Overkiz tilt and stop controls, while 2026.5.4 adds missing Miele dishwasher codes.

### Patch-release compatibility (2025.8)

As of 2025.8.3, ESPHome 2025.8.0 is the minimum stable BLE version.

### Patch-release integration behavior (2026.2)

As of 2026.2.1, Denon AVR media players map stopped playback to the `stopped` state. Version 2026.2.2 adds Miele TQ1000WP programs and phases, while 2026.2.3 adds Roborock region selection and Miele dishwasher program codes.

### Patch-release public behavior (2026.6)

Version 2026.6.3 makes `config_entry_attr` return enum values. Version 2026.6.4 corrects Growatt V1 `total_output_power` values that were 1,000 times too low, adds Subaru API generation 4 support, includes Sonos favorites in source lists while exposing source selection only when supported, and stops `zwave_js.set_credential` from validating the number of credential slots.

### Patch-release public behavior (2026.7)

Patch releases make HomeKit Controller doorbell event entities use the standardized `ring` event, restore SolarEdge energy-sensor units, fix Proximity matching against trackers with `in_zones`, and stop Teslemetry covers from reporting false open or closed states when data is absent. They also correct YoLink water-meter valve status, refresh App update entities after a store reload, and exempt certain protocol integrations from the entity limit.

### Patch-release public behavior (2026.8.0)

Patch releases make SmartThings air conditioners use their cooling-setpoint range and convert streamed Teslemetry tyre pressure and isolation resistance to their declared units. They also report refused HomematicIP alarm activations, expose Tedee locks as `unknown` during calibration or updates, and retain delayed Israel Rail departures.

### Polling and compatibility changes (2025.10)

HERE Travel Time's automatic polling interval increases from 5 to 30 minutes to fit one route within the new free Base Plan. Zabbix 5.0 is no longer officially supported, although existing connections are not immediately blocked.

### Protocol and appliance support (2026.3)

Matter adds carbon-monoxide alarm states and TVOC air-quality-level sensors, while HomeKit Controller adds water-level sensors. SmartThings supports dual-cavity ovens and dishwasher option controls, Roborock supports Zeo washers and dryers, Alexa Devices supports Amazon Air Quality Monitor, Switcher adds heaters, and Watts Vision + adds smart switches.

### Proxmox and device-management controls (2026.4)

Proxmox VE adds runtime discovery, uptime, memory, storage, network, and backup sensors, a node-level suspend-all button, a snapshot button, and token authentication. Schlage can add, retrieve, and delete lock access codes; Renault can expose and set charge limits; Kostal Plenticore can set active-power limits; and Portainer gains pause and resume buttons.

### Rabbit Air preset values (2026.7)

Rabbit Air preset machine values change from `Auto`, `Manual`, and `Pollen` to `auto`, `manual`, and `pollen`; update exact comparisons and action data.

### Real-time power monitoring (2025.12)

Energy configuration can now associate power sensors with grid imports, exports, sources, and individual devices alongside cumulative energy sensors. The Energy dashboard uses them for current-watt power graphs and live flow visualization.

### Reolink dual-lens sub-devices (2026.7)

Reolink Duo PoE and Duo WiFi cameras now create one sub-device per lens and move the corresponding camera and motion/AI entities beneath them. Entity IDs and custom names remain, but generated names lose the lens suffix and device-targeted automations must target the new lens sub-device.

### Reolink password limit (2025.4)

Reolink passwords are now limited to 31 characters. Existing longer passwords trigger reauthentication and must be changed to work with the current Reolink API.

### Roth Touchline preset names (2026.4)

Roth Touchline climate presets change from `Normal`, `Night`, `Holiday`, and `Pro 1`–`Pro 3` to `none`, `sleep`, `away`, and `program_1`–`program_3`. Update action data and exact preset comparisons.

### Searchable media sources (2026.8.0)

Media-source integrations can now expose search directly in the media browser. Immich initially provides content-aware photo search, while Overseerr can search for and request films and shows from that interface.

### SmartThings and Miele device coverage (2025.6)

SmartThings adds support across cooktops, hobs, water heaters, hood fans, steam closets, refrigeration, washers, valves, heat-pump zones, and atmospheric-pressure sensors. Miele adds vacuums, drying-step and washer-dryer phase sensors, hob-plate sensors, and energy and water forecasts.

### SmartThings and SwitchBot additions (2026.4)

SmartThings robot vacuums gain fan speed, driving and cleaning modes, water-spray and sound controls, a full dust-bag sensor, a HEPA-filter reset button, and Do Not Disturb scheduling; stick cleaners are supported, and dishwashers gain start, pause, resume, cancel, and drain actions. SwitchBot adds Keypad Vision doorbell, tamper, and charging entities, while SwitchBot Cloud can control Standing Fan devices.

### SmartThings setup rewrite (2025.3)

SmartThings setup now uses Samsung account login instead of routing configuration, exposed ports, developer accounts, and access tokens. Push updates work without exposing the Home Assistant instance to the internet.

### Supervisor action failures (2026.5)

Supervisor actions such as `hassio.addon_start`, `hassio.backup_partial`, and `hassio.host_reboot` now raise on failure, stopping scripts and automations by default. Add `continue_on_error: true` to an action step only when the previous continue-after-failure behavior is required.

### Synology DSM polling (2025.3)

The Synology DSM scan-interval option has been removed and polling now defaults to 15 minutes. Use Home Assistant's integration-independent polling customization when another interval is required.

### Telegram bot action validation (2026.1)

Telegram bot actions no longer accept undefined or unused parameters. Remove any fields that are not part of the supported notification-action schema.

### Tesla Fleet OAuth credentials (2025.1)

Tesla Fleet no longer includes shared OAuth application credentials because Tesla ended open-source application registrations and moved to pay-per-use access.

### Tesla route-tracker states (2026.7)

Tesla Fleet and Teslemetry route trackers now derive `home`, `not_home`, or a zone name from route coordinates instead of using the destination as state; Teslemetry also removes the `location_name` attribute. Enable the new, disabled-by-default Destination sensor and migrate destination-name consumers to it.

### Tibber 15-minute pricing (2025.10)

`tibber.get_prices` now returns 15-minute rather than hourly data, the `price_level` attribute is removed, and `intraday_price_ranking` is rescaled to the `(0,1)` range.

### Timestamp display formats (2026.7)

Timestamp entities on Tile cards, Entities cards, and entity badges now expose a visual **Time format** option, including short and long variants of relative time.

### Tuya HVAC modes converted to presets (2026.2)

Duplicate Tuya HVAC modes are now presets, so affected automation and script calls must move from `set_hvac_mode` to `set_preset_mode`. Version 2026.2.1 also removes a redundant `off` preset.

### UniFi Protect vehicle events (2025.12)

The nonfunctional legacy license-plate sensor is removed and replaced by a **Vehicle Detection Event** entity with plate, vehicle type, color, and confidence data. The replacement event fires after a three-second delay to improve thumbnail and license-plate-recognition data quality, which timing-sensitive automations must allow for.

### UniFi security additions (2026.5)

UniFi Protect gains an alarm control panel plus PoE and SuperLink sirens and relay switches, all requiring UniFi Protect 7.1 or newer. UniFi Access adds temporary door-lock rules, access-event direction, UA-HUB-Door support, and console discovery.

### User-facing integration sub-entries (2025.7)

Anthropic, Google Generative AI, MQTT, Ollama, OpenAI Conversation, and Telegram Bot can add sub-entries beneath one credential-bearing integration entry. This supports cases such as several differently prompted agents on one account or UI-configured devices beneath one MQTT broker; the integration page shows which devices and services belong to each entry or sub-entry.

### Vacuum and lawn-mower dialogs (2026.5)

Redesigned more-info dialogs put battery state and actions in a consistent layout; vacuums also gain a **Clean by area** view for mapping and selecting one or more rooms. Lawn mowers receive the same state-aware layout without the area-cleaning view.

### Valve groups and integration-provided backgrounds (2025.11)

Valve entities can now be combined through the Group integration. Dashboard backgrounds can use images supplied by any integration that provides images.

### Visual continue-on-error control (2026.3)

The automation editor's action menu can now enable **Continue on error**, previously a YAML-only option. Actions using it have a visible indicator and no longer stop later actions when they fail.

### Weather and media-player Tile features (2026.6)

Weather tiles gain temperature and precipitation forecast features with automatic daily, twice-daily, or hourly resolution and optional fixed resolution and labels. Media-player tiles add mute controls, shuffle, repeat, volume up/down, and mute playback buttons, plus filtering for source and sound-mode lists.

### Whirlpool door-state split (2025.8)

Whirlpool washer and dryer door state moves from the main machine-state sensor to a binary sensor, while the main sensor retains only cycle states. Update automations and scripts to use the new door sensor.

### Zeroconf discovery announcement (2026.7)

The obsolete `requires_api_password` field is removed from `_home-assistant._tcp` mDNS announcements. Third-party discovery clients must tolerate its absence.

## New integrations and setup

### New integration actions (2025.4)

Microsoft OneDrive can upload files through an action, HEOS can browse media such as TuneIn, and Habitica adds actions for managing habits, rewards, and dailies.

### New integration coverage (2026.5)

New integrations add local Denon RS-232 receivers, Duco ventilation, EARN-E P1 meters, Eurotronic Comet Blue thermostats, Teleinfo meters, and Victron GX systems. Other additions cover Fumis stoves, Kiosker clients, Iberian OMIE prices, and the RF-based Honeywell String Lights and Novy Cooker Hood devices.

### New integration coverage (2026.6)

New local or device-focused integrations cover AiDot lights, Guntamatic heaters, LG TVs over RS-232 or an ESPHome serial proxy, Marantz and Samsung infrared devices, Mitsubishi Comfort HVAC with local control after Kumo Cloud discovery, and Ouman EH-800 heating. Cloud and data additions cover CentriConnect propane tanks, Cielo climate devices, Data Grand Lyon transit and bikes, OVHcloud AI Endpoints, PAJ GPS, PTDevices tank levels, Vistapool controllers, Xthings lights, and Yoto players.

### New integration sensors (2026.3)

Proxmox VE adds node, VM, and container CPU, memory, disk, and status sensors; Uptime Kuma adds uptime-ratio and average-response-time sensors over 1-, 30-, and 365-day periods. MELCloud, Ambient Weather Station, SleepIQ, Tessie, Vera, Green Planet Energy, and Sunricher DALI add new device, health, energy, or pricing sensors, while WeatherFlow battery readings are now percentages.

### New integration sensors and actions (2026.2)

Roborock adds dock water-box sensors; Tibber adds EV-charger, temperature, and grid sensors and more EV settings; VeSync adds PM1 and PM10; Bang & Olufsen adds battery and charging data; and Powerfox, Ruuvi, and ToGrill add gas-meter, IAQS, and ambient-temperature sensors respectively. Portainer adds a prune-images button and state sensor, while ntfy supports sequence IDs for updating notifications plus dismiss and delete actions.

### New integrations (2025.12)

New integrations add Airobot thermostats, Anglian Water meters, Backblaze B2 backup storage, EnergyID synchronization, Essent tariffs, Google Air Quality, Google Weather, Hanna pool controllers, bridge-free Philips Hue BLE lights, Saunum sauna controls, and Victron BLE monitoring. Cosori and VÁGNER POOL also become discoverable as virtual integrations handled by VeSync and SEKO PoolDose.

### New integrations (2025.4)

Bosch Alarm controls and monitors Bosch intrusion panels, Remote calendar imports remote calendar URLs, and Pterodactyl controls and monitors Pterodactyl game-server panels.

### New integrations (2025.9)

New integrations add Genie Aladdin Connect garage-door control, SEKO PoolDose pool and spa monitoring, Sleep as Android alarm and sleep-cycle events, and ToGrill Bluetooth thermometer support.

### New integrations (2026.4)

New integrations add Autoskope and LoJack cloud vehicle tracking, Casper Glow Bluetooth lights, Chess.com and Lichess statistics, Fresh-r ventilation monitoring, OpenDisplay image delivery to BLE e-paper displays, local Modbus TCP monitoring for Qube heat pumps, local Solarman energy monitoring and control, TRMNL battery and sleep controls, local UniFi Access doors and locks, and Zeroconf-discovered WiiM media players.

### New integrations (2026.8.0)

New local and device integrations cover Dyson and generic LED infrared control, Harbor Sleep monitors, Harman Luxury Audio and Lyngdorf players, Midea appliances, NeoPool controllers, and ScorpionTrack public vehicle shares. Data and service integrations add Fuelprices.dk, Gatus, GeoSphere Austria warnings, Google Health and Fitbit data, Karakeep, and LiteLLM or llama.cpp conversation agents.

### New integrations and integration lifecycle (2025.5)

AWS S3 can serve as a backup location, while new integrations add Imeon inverters, Miele appliances, ntfy notifications, and Rehlko generators. STIEBEL ELTRON can now be set up from the UI, and Oncue by Kohler is removed because its app was discontinued.

### New integrations and UI setup (2025.10)

New integration coverage includes Compit, Cync, Droplet, ekey bionyx, IRM KMI, Libre Hardware Monitor, Portainer, Smart Meter B Route, SFTP Storage, Usage Prediction, and Victron Remote Monitoring; SFTP Storage provides SFTP/SSH remote backup storage. Nederlandse Spoorwegen and Satel Integra can now be configured from the UI.

### New integrations and UI setup (2025.2)

New integrations cover Homee, igloohome devices, LetPot gardens, Overseerr requests, and Qbus Control; Decorquip Dream is discoverable through the Motionblinds integration. NMBS and Filter can now be configured from the UI.

### New integrations and UI setup (2025.8)

New integrations add OpenRouter, Ubiquiti UISP airOS, Uptime Kuma, and Volvo; Bauknecht is discoverable through Whirlpool Appliances and Z-Box Hub through Fibaro. Datadog can now be configured from the UI.

### New integrations and UI setup (2026.1)

New integrations add AirPatrol air-conditioning control, eGauge energy monitoring, Fluss+ buttons, Fish Audio text-to-speech, Fressnapf pet tracking, HomeLink vehicle controls, Watts Vision + heating zones, and internal WebRTC camera streaming; Levoit is also discoverable through VeSync. Hikvision and VIVOTEK can now be configured from the UI.

### New integrations and UI setup (2026.2)

New integrations add Cloudflare R2 backup storage, Green Planet Energy hourly pricing, HDFury video-device control, local NRGkick Gen2 charger monitoring, Prana ventilation control, and uHoo air-quality monitoring. Namecheap DynamicDNS, OpenEVSE, Proxmox VE, and WaterFurnace can now be configured from the UI.

### New integrations and virtual entries (2026.7)

New integrations add Aqvify well and tank sensors, Bluetooth Chef iQ probes, Dropbox backup storage, Edifier infrared control, local energieleser and Envertech monitoring, MQTT Greencell chargers, local Helty ventilation, KlikAanKlikUit RF control, and MELCloud Home; Dropbox uses Cloud Account Linking but needs neither a Cloud subscription nor custom application credentials. New virtual entries route Avosdim through Motionblinds, BWT through SEKO PoolDose, Gitter through Matrix, and Nexen through Hypontech Cloud.

### Other new integrations and UI setup (2026.3)

New integrations cover Ghost publication metrics, MTA New York City Transit arrivals, Redgtech switches, local System Nexa 2 devices, and Teltonika RutOS routers; Ubisys is discoverable as a virtual integration handled by ZHA. InfluxDB, Ness Alarm, and Splunk can now be configured from the UI.

## Protocols, proxies, and connectivity

### 2025.6.2 Z-Wave defaults (2025.6)

As of 2025.6.2, Z-Wave Indicator Command Class entities and the idle-notification button are disabled by default.

### Bluetooth connection visualization (2025.6)

The Bluetooth integration now visualizes devices connected directly or through Bluetooth proxies. It shows both active connections and in-range devices not yet known to Home Assistant.

### Bluetooth diagnostics panel (2025.2)

The Bluetooth integration's **Configure** page now exposes its options, connection-slot allocation, and an advertisement monitor showing raw advertisements and the local adapter or Bluetooth proxy carrying each connection.

### Bluetooth scanning defaults (2026.6)

The Bluetooth integration now defaults to **Auto**, switching between active and passive scanning as needed. Existing ESPHome and Shelly Bluetooth scanners set to Active are migrated to Auto, while ESPHome scanners explicitly set to Passive remain so; adapters that regress can be changed back to Active in their integration or device options.

### ESPHome action responses (2026.1)

Home Assistant can now receive structured JSON responses from actions implemented by ESPHome 2025.12 devices. Automations can use those returned values for on-demand configuration, sensor, or diagnostic queries instead of treating device actions as one-way calls.

### ESPHome network serial proxies (2026.5)

An ESPHome `serial_proxy` can expose a wired UART over the network, and Home Assistant's live serial selector now lists remote proxies beside local USB ports. Denon RS-232 and Russound RIO support proxies initially; Home Assistant also replaces `pyserial` with the async `serialx` driver, requiring serial-based custom integrations to migrate.

### ESPHome sub-devices (2025.7)

One ESPHome device can now represent multiple logical Home Assistant devices, useful for RF bridges and Modbus gateways. This requires ESPHome 2025.7.

### ESPHome updates and Shelly device hierarchy (2025.6)

ESPHome can now update devices that are in deep sleep. Shelly represents channels of multi-channel hardware as sub-devices, which can change the device structure used for targeting and organization.

### Infrared and radio-frequency settings panels (2026.7)

Settings gains dedicated Infrared and Radio frequency panels listing configured proxies and transmitters; each panel appears only when corresponding devices exist.

### Infrared receiver events (2026.6)

The Infrared platform now supports receiver event entities, allowing automations to react to commands heard from original remotes. ESPHome is the first supported receiver source and LG Infrared the first device integration to expose the received commands.

### KNX scene state updates (2025.9)

KNX scene entities now update their state when a scene is activated externally from the bus, not only when Home Assistant activates it. Automations observing scene state may therefore receive changes from external controllers.

### Matter lock credentials (2026.4)

Matter lock device pages now provide **Manage lock** for adding, editing, and removing users and PINs with full or one-time access; a one-time PIN is deleted by the lock after use. Automation actions can create or remove users, set or clear PIN and RFID credentials, and query lock capabilities.

### Matter pump devices (2025.6)

The Matter integration now supports the pump device type.

### Matter setup and sirens (2026.6)

Adding a Matter device now immediately asks for its name and area, and contact sensors and covers can be classified by what they are attached to; the prefilled iOS fields require a companion-app update. Matter sirens are exposed as regular siren entities that can be controlled from dashboards and automations.

### Matter, SmartThings, and Roborock additions (2026.1)

Matter gains thermostat remote-sensing diagnostic binary sensors and volume-slider entities for speakers. SmartThings adds PM1, PM2.5, PM10, hood-filter, refrigerator-temperature, and range-hood fan controls, while Roborock Q7 devices gain basic read-only battery, status, and cleaning-data support.

### MQTT and Matter platforms (2026.5)

MQTT gains time, datetime, and date entity platforms, while Matter adds native radon-sensor support.

### MQTT configuration flow (2025.2)

Selecting **Configure** for MQTT now opens an MQTT settings page with subscribe and publish tools, while options replace the old **Re-configure MQTT** button. Broker reconfiguration is available only from the integration entry's context menu.

### MQTT publish action fields (2025.2)

`mqtt.publish` no longer accepts `topic_template` or `payload_template`; put templates directly in `topic` and `payload`. Since 2025.2.1, `payload` may be omitted to publish an empty payload.

```yaml
actions:
  - action: mqtt.publish
    data:
      topic: "home/example/state"
      payload: "{{ states('sensor.example') }}"
```

### Native infrared proxies (2026.4)

The new Infrared entity platform lets appliance integrations send commands through ESPHome-powered IR transmitters; an appliance-specific integration still has to implement the device protocol. LG Infrared is the first implementation, exposing assumed-state media-player controls and remote-function buttons because IR communication is one-way.

### Native radio-frequency proxies (2026.5)

The new Radio frequency entity platform mirrors the infrared platform: device integrations select a transmitter rather than configuring RF directly. ESPHome transmitters can cover the common 315, 433, 868, and 915 MHz bands, while Broadlink support is limited to the 433 MHz RM4 Pro; Honeywell String Lights and Novy Cooker Hood are the first consumer integrations.

### Network, infrared, and KNX capabilities (2026.8.0)

Shelly supports firmware 2.0 Enhanced Security on generation 2 and newer devices plus circuit breakers, MQTT gains an infrared platform, and SMLIGHT Ultima devices can act as Bluetooth proxies and infrared receivers. KNX button and notify entities can be configured in the UI, its panel adds telegram sending, a DPT reference, and project-device views, and all KNX entities restore state after reload or restart.

### SwitchBot, VeSync, and KNX controls (2026.3)

SwitchBot can program Keypad Vision passwords and set a slow curtain mode, and VeSync humidifiers gain an auto-drying switch. KNX can configure number entities and send the current time from the UI, and its expose feature can periodically resend entity states to the bus.

### Z-Wave JS advanced access control (2026.8.0)

Z-Wave JS app 1.6.0 adds an **Access Control** tab in Z-Wave JS UI, separate from Home Assistant's Z-Wave panel. It supports several PIN or fingerprint credentials per user, on-lock enrollment, audit history, admin-code management, moving credentials, and bulk deletion when the lock provides those capabilities.

### Z-Wave lock credentials (2026.6)

Z-Wave lock device pages now offer **Manage access** for adding, editing, and removing users and credentials, including duplicate-PIN warnings and both numeric PINs and alphanumeric passwords when supported. The underlying actions are also available to automations for issuing, rotating, and revoking access without a vendor cloud.

### Z-Wave Smart Start and Long Range (2025.5)

The companion apps can scan Smart Start QR codes natively; a scanned device appears before it is powered and joins automatically when powered or rebooted. Long Range-capable devices can be added either to the normal mesh or as a direct Long Range connection.

## Sensors, entities, and measurement

### Energy sensor formats and measurement units (2026.2)

Energy configuration can now use one signed power sensor for grid or battery flow, or two positive sensors for import/export or charge/discharge, without a template sensor. Parts per billion (`ppb`) is accepted for sulfur-dioxide sensors and number entities.

### Expanded device and entity support (2025.4)

SmartThings adds firmware updates, event entities, PM0.1 sensors, washer rinse-cycle settings, and broader TV and media-player support. Roborock adds dryer controls and routine-start buttons, Reolink adds smart-AI and day/night sensors, HomeKit can power TVs on and off, and lawn mowers can be exposed through Google Assistant and HomeKit.

### New sensor and response-action capabilities (2025.3)

Sensors gain a wind-direction device class. `media_player.browse_media` can now be called as an action with a response, and `schedule.get_schedule` returns a schedule helper's configuration.

### Patch-release entity and validation changes (2025.4)

As of 2025.4.1, the built-in Music Assistant player no longer creates a Home Assistant media-player entity, and SmartThings climate entities gain preset mode. Version 2025.4.2 permits equal minimum and maximum values in MQTT number configuration; 2025.4.4 creates Home Connect active- and selected-program entities only when the appliance exposes programs.

### Reolink Wi-Fi signal units (2025.8)

Reolink Wi-Fi signal strength changes from a 0–4 bar indicator to any dBm value from `-85` through `-30`. Rough old-to-new correspondences are `0`→`-85`, `1`→`-75`, `2`→`-65`, `3`→`-55`, and `4`→`-45` dBm.

### Restored entity and device customizations (2025.7)

When a deleted entity or device is re-added, Home Assistant now restores its user-defined names and settings.

### Sensor classes and units (2025.6)

Sensors gain a reactive-energy device class and units, the `Wh/km` energy-distance unit, `mg/m³` concentration, and liters as a gas-sensor unit.

### Sensor units (2026.5)

Frequency sensors accept automatically convertible units from millihertz through gigahertz, and electric-current sensors accept microamperes.

### Sensor-group unavailable and unknown states (2026.2)

A sensor group is now `unavailable` when every member is unavailable or absent from the state machine. Otherwise, with the default `ignore_non_numeric: false`, it is calculated only when every member exists and is numeric; a missing or nonnumeric member makes the group `unknown`.

### Smaller energy and power units (2025.1)

Energy sensors now accept `mWh`, and power sensors now accept `mW`, as units of measurement.

### SolarEdge battery sensors (2026.5)

SolarEdge adds aggregate and per-battery daily charge/discharge energy, state-of-charge, and power sensors. They are disabled by default and must be enabled selectively.
