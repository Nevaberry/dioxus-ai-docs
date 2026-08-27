# Custom Integration and Frontend Development

Use this reference for custom-integration APIs, entity models, config flows, frontend interfaces, selectors, and developer migrations. Entries are grouped by task; the parenthetical batch ID identifies when the guidance entered this patch.

## Configuration, discovery, and flows

### Custom-integration discovery and units (2025.2)

Developer-facing changes add energy-by-distance units and relocate the DHCP, SSDP, USB, and zeroconf `ServiceInfo` models, requiring custom integrations that use those discovery models to update their imports.

### Custom-integration flow results (2025.8)

The `result` attribute has been removed from the `FlowResult` typed dictionary; custom integrations must stop reading it.

## Entity models, helpers, services, and runtime APIs

### Advanced mode and developer interfaces (2026.6)

The profile-level Advanced mode toggle is removed and its formerly gated features are available to everyone; advanced-mode checks in data-entry flows are correspondingly deprecated. Developer changes also require a domain on `BrowseMediaSource`, deprecate combining config-entry listeners with reload methods, and add an entity-name formatting helper.

### Custom-integration API changes (2025.1)

Developer-facing changes include a `WaterHeaterEntityDescription` rename and migration toward Pydantic v2, plus independent horizontal swing for climate entities, a new vacuum state property, Kelvin as the preferred color-temperature unit, and an area device class for squared units.

### Custom-integration API changes (2025.12)

MQTT subscriptions gain a status callback, data update coordinators support Retry After, service-action translation descriptions support placeholders, and device-identification buttons are classified as diagnostic. Worker-thread serialization for `Store` data is now opt-in, and `CalculatedState.capability_attributes` is removed.

### Custom-integration API changes (2025.3)

Developer-facing changes introduce backup agents and config subentries, change `BackupAgent` APIs and config-entry state transitions, and add checks for config-flow unique IDs.

### Custom-integration deprecations (2026.5)

Developer-facing changes deprecate the legacy device-tracker platform API and entity IDs whose domains do not match their platforms, migrate App builds to Docker BuildKit, and standardize doorbell event types. Frontend components and context APIs also change in this release.

### Custom-integration development tooling (2026.2)

Home Assistant's custom-integration development workflow is replacing `pre-commit` with `prek`.

### Custom-integration device areas (2025.9)

`DeviceEntry.suggested_area` is deprecated and will be removed; custom integrations must stop relying on that attribute.

### Custom-integration interface changes (2025.11)

Target selectors no longer support the device filter, and service translations are no longer returned by WebSocket `get_services` or REST `/api/services`. `TemperatureConverter.convert_interval` is deprecated, while update coordinators now support retriggering.

### Custom-integration interfaces (2026.3)

Developer-facing changes deprecate Labs `async_listen`, change OAuth 2.0 helper error handling, allow custom integrations to provide brand images, and add reconfiguration support to the webhook helper. Deprecated light features have also been removed.

### Custom-integration interfaces (2026.7)

Developer-facing changes revise device-tracker entity models and frontend components, introduce new unit enumerators, and deprecate the `home_assistant_start` flag of `async_initialize_triggers`.

### Custom-integration service APIs (2025.10)

The `hass` argument in service helpers is deprecated, and platform entity services have a revised registration API; custom integrations using either interface need migration.

### Immutable UnitSystem (2025.4)

For custom integrations, the `UnitSystem` dataclass is now frozen and must be treated as immutable.

## Frontend, selectors, and presentation

### Custom-integration display metadata (2025.6)

Icon translations can now define ranges, and sensor device classes now provide default display precision.

### Custom-panel safe-area handling (2026.8.0)

As of 2026.8.2, `panel_custom` offers a `handle_safe_area` opt-out for panels that manage safe-area handling themselves.
