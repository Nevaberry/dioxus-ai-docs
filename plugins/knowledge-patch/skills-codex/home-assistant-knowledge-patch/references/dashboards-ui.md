# Dashboards and User Interface

Use this reference for dashboards, cards, pickers, Activity, search, editors, navigation, and entity organization. Entries are grouped by task; the parenthetical batch ID identifies when the guidance entered this patch.

## Dashboards, cards, views, and layout

### Areas dashboard additions (2025.6)

The experimental Areas dashboard adds an **Actions** section for scripts, automations, and scenes. Number and button entities and helpers, counters, and timer helpers now appear under **Others**, while **Entertainment** is renamed **Media players**.

### Areas dashboard overview (2025.7)

The experimental Areas dashboard now uses the redesigned Area cards as a room-by-room control and navigation overview. It remains experimental and subject to change.

### Built-in dashboard migration (2025.12)

The Home dashboard is now a built-in dashboard listed under dashboard settings, though it remains hidden by default. New Areas dashboards can no longer be created because that design evolved into Home; existing Areas dashboards keep working, while existing Home favorites may need to be re-added after migration.

### Card auto height and section spacing (2026.4)

The visual layout editor can enable content-driven **Auto height** for cards; entities and vertical-stack cards already use it, and heading cards now default to it. The default inter-section row gap increases from 8 to 24 pixels; themes can restore the old spacing with `ha-view-sections-row-gap: 8px`.

### Clock card (2025.4)

The new Clock card displays the current time and can configure its size, time zone, seconds display, and 12- or 24-hour format.

### Contextual dashboard entity names (2025.11)

Cards can derive displayed names from an entity, device, area, floor, or a combination of them, while still permitting a custom name. Derived names follow later entity and device renames automatically.

### Custom dashboard strategies (2026.5)

Custom integrations and frontend modules can now register dashboard strategies that generate complete dashboards dynamically.

### Dashboard and table controls (2026.6)

Statistics Graph and History Graph cards now support a custom color per entity in both the visual editor and YAML. Helpers, automations, scenes, and scripts can be filtered by label, and the Devices table offers a hidden-by-default firmware column.

### Dashboard background controls (2025.1)

Dashboard backgrounds now support tiling, transparency, sizing, alignment, and fixed-versus-scrolling behavior.

### Dashboard card controls (2026.2)

Heading cards gain icon/text button badges with colors, visibility conditions, and tap, hold, or double-tap actions; Entity cards gain the same interaction actions. Area cards can target individual control entities and configure card or image tap actions, while calendar cards can display configured per-calendar colors, with Google Calendar already supporting them.

### Dashboard favorites (2026.4)

Saved light colors and color temperatures can appear as one-tap Tile and Light card features, while covers and valves can save and expose favorite positions. Favorites can also be copied to other entities that support the same modes.

### Dashboard ordering and history (2025.12)

**Settings > Areas, labels & zones > Reorder floors and areas** can set the order used by all built-in dashboards. The dashboard editor also gains undo and redo for up to 75 changes.

### Dashboard section backgrounds (2026.4)

Sections can enable a background using a predefined or custom hex color and an opacity setting. Adjacent sections without backgrounds align automatically with those that have one.

### Dashboard view headers (2025.3)

Dashboard views can now have a header containing a title, Markdown- or template-based welcome text, and badges. Headers support responsive, left, or centered alignment; badges appear below the text by default but can be placed above it.

### Distribution card (2026.2)

The new Distribution card renders multiple entity values as a proportional horizontal bar with an interactive legend and more-info links. Combined entities must share a domain and device class, but compatible units such as watts and kilowatts are converted automatically.

### Downstream water meters and dashboard tabs (2025.12)

Downstream water meters can break total water consumption into uses such as irrigation, softening, or pools, including a water Sankey visualization. Configuring water, gas, or power splits the Energy dashboard into resource-specific tabs; energy-only setups retain the existing layout.

### Experimental Areas dashboard (2025.4)

The experimental Areas dashboard automatically builds an overview and a dedicated page for each configured area using sections and tile cards, grouping entities by domain. Areas and entities can be reordered or hidden, and each area's settings control the temperature and humidity badges shown on its page.

### Experimental Home dashboard (2025.9)

The new optional Home dashboard provides light, climate, security, and media summaries, area browsing, entity favorites, and initial weather and energy cards. It has limited configuration and must be added manually from the dashboard settings.

### Graph legends and zooming (2025.3)

Graph legends now appear below the graph and move excess entries behind an ellipsis; dashboard cards can opt to keep the full legend visible. Double-click zooms a graph, while Ctrl/Cmd plus range selection provides controlled zooming.

### Home dashboard organization (2025.11)

The Home dashboard merges suggested entities and favorites into one smart section and groups areas by floor. Lights, Climate, and Security move to separate built-in dashboards under **Settings > Dashboards**, where they also include devices without an assigned area.

### Maintenance and Security dashboards (2026.5)

The new built-in Maintenance dashboard automatically groups battery entities by area and highlights low batteries. On wide screens, the Security dashboard gains a live 24-hour Activity sidebar for security-related entities when Logbook is enabled.

### Map marker clustering (2025.3)

Map cards now cluster nearby tracked entities; expanding a cluster spiders its markers out with lines back to their original positions. Clustering can be temporarily disabled with a toggle.

### Overview becomes the default Home dashboard (2026.2)

The Home dashboard is renamed **Overview** and becomes the default for new installations; long-time users whose default view was never customized are prompted to opt in. The former customizable Overview remains available as the **Overview (legacy)** dashboard template, while the new Overview surfaces discovered devices, prompts for assigning unassigned devices to areas, and links area edits to primary-sensor configuration.

### Profile-synced sidebar (2025.6)

Sidebar ordering and visibility are now edited in a drag-and-drop dialog and stored in the user profile, so the layout follows that user across devices.

### Redesigned Area card (2025.7)

The Area card now has compact and detailed layouts suitable for Sections dashboards, configurable and reorderable controls, optional camera feeds, and cover controls. Existing Area cards must have their controls reconfigured after upgrading.

### Suggested dashboard controls (2025.10)

The Home dashboard can suggest commonly used entities by hour, and the same prediction controls can be placed in a manual Sections dashboard with section-level strategy YAML:

```yaml
strategy:
  type: common-controls
  title: Common controls
```

### System-wide and personal default dashboards (2025.12)

The selected system default dashboard now takes effect immediately for every user and moves to the top of the sidebar. A user can override it in their profile, but that preference follows the user across devices; use separate users when a wall panel and phone need different defaults.

### Theme and typography token migration (2025.5)

Legacy Polymer components and their `paper-*` CSS variables are removed, so custom cards and themes must migrate to the new `--ha-font-*` and `--ha-line-height-*` typography tokens. Notable mappings include `--code-font-family` to `--ha-font-family-code`, the old font-smoothing variables to `--ha-font-smoothing`, and `--paper-item-icon-color` to `--state-icon-color`.

### Tile-card and clock features (2025.9)

Tile cards gain a 24-hour entity trend chart, media-player and volume controls, a percentage-sensor bar gauge, fan direction and oscillation controls, configurable buttons for automation, script, and button entities, valve open/close and position controls, and date controls for date, datetime, and input-datetime entities. The Clock card can now use a customizable analog style.

### Tile-card interaction cues (2025.3)

An icon that directly performs an action now has a circular background, while an icon that opens more information does not. Tile cards also support keyboard navigation with Tab and Shift+Tab.

### Tile-card media volume (2025.1)

A Tile card for a media-player entity can add a volume-slider feature for direct volume control.

### Tile-card placement and controls (2025.3)

A Tile card's features can now appear below the card or inline to the right of its icon; only the first feature can be inline, and later features are hidden in that layout. New features add a direct switch toggle and counter increase, decrease, and reset controls.

## Editors, pickers, search, and navigation

### Android entity shortcuts (2025.12)

With Android Companion app 2025.11 or newer, an entity's more-info dialog has an **Add to** menu for compatible home-screen widgets and Android Auto favorites.

### Context-rich target picker (2025.11)

The automation target picker now shows the device and area for entities, the number of entities affected by floor and area targets, and expandable details for floors, areas, and devices. This makes broad targets auditable while preserving their ability to adapt when devices are added or removed.

### Dashboard visibility and integration search (2026.5)

Card state and numeric-state visibility conditions can target the card's own entity and can evaluate an entity attribute. Integration detail pages gain a search across entries, devices, names, manufacturers, models, and areas.

### Discovery diagnostics and shortcuts (2025.5)

DHCP, mDNS/ZeroConf, and UPnP/SSDP discovery browsers are available under **Settings > System > Network**. Pressing `?` anywhere in the UI opens the keyboard-shortcut list.

### Entity-first card picker (2026.6)

The add-card dialog now opens on **By entity**, with a floor, area, device, and entity tree plus live previews of compatible cards; **Unassigned**, search, **Browse all cards**, and the unchanged **By card** view cover the remaining paths. Custom cards can contribute suggestions under **Community** by adding `getEntitySuggestion` to their `window.customCards` entry.

### Entity-ID generation preferences (2026.8.0)

Entity-ID generation now exposes ordering control in the entity editor, letting users choose how ID components are arranged instead of adopting a single area-oriented pattern.

### Entity-ID restoration (2025.6)

An entity configuration dialog can reset a renamed entity ID to its original value. A device page's **Recreate entity IDs** command resets all of that device's entity IDs at once.

### Entity-picker context and IDs (2025.5)

Entity pickers now search and display device and area context. Entity IDs are hidden by default but can be restored with **Display entity IDs in picker** in the user's profile settings.

### Full-screen code editors (2025.7)

Every UI YAML and template editor now has a maximize control for full-screen editing; the same control returns it to the embedded view.

### Home dashboard mobile navigation and unassigned devices (2026.1)

On mobile, summary cards for lights, climate, security, media players, weather, and energy now appear above favorites and areas, replacing the tab-based layout; desktop remains unchanged. A new **Devices** page exposes devices that are not assigned to an area.

### Interactive cards and network editors (2026.4)

Markdown cards now support tap, hold, and double-tap actions. The Map card visual editor exposes all card and entity options, and ZHA, Z-Wave, and Bluetooth network graphs gain device search.

### MQTT entity-ID configuration (2026.4)

The deprecated MQTT `object_id` option is removed from YAML and ignored in discovery payloads. Use `default_entity_id` when suggesting an entity ID.

### Picker search expansion (2025.6)

The improved entity-picker search now also applies to area, category, floor, label, user, and device pickers. The redesigned device picker adds manufacturer logos and styling consistent with the entity picker.

### Protocol dashboard navigation (2026.1)

Protocol dashboards now appear in a dedicated section directly after the core items on **Settings**. A protocol entry is shown only when its corresponding integration is configured.

### Redesigned Quick search (2026.2)

`Cmd+K` on macOS or `Ctrl+K` on Windows and Linux opens a unified search across navigation, commands, entities, devices, and areas; arrow keys, Enter, and Escape provide full keyboard control, and mobile can assign it to a gesture. Existing `e`, `d`, and `c` shortcuts open their corresponding Quick search filters, while `a` still opens Assist and `m` creates a My link.

### Related-object navigation and creation (2026.6)

Device and area pages gain consolidated links to related objects, while label navigation expands to scenes and scripts. With the purpose-specific Labs preview enabled, an entity, device, or area page can create an automation or script with that object already inserted as a trigger, condition, or action target.

### Shortcut card and badge (2026.5)

The new Shortcut card and matching badge can navigate to a dashboard, view, area, or device, open a URL, launch Assist, or perform an action. Navigation and Assist targets supply sensible defaults, while labels, descriptions, icons, colors, and horizontal or vertical layout remain customizable.

### Tools and Cloud navigation (2026.8.0)

**Developer Tools** is renamed **Tools**, and its template editor gains a remembered, resizable side-by-side or stacked editor/result layout. Home Assistant Cloud settings are split into per-feature pages with an overview and a resumable guided setup.

### YAML editor linting (2026.6)

UI YAML editors now report syntax and indentation problems inline as text is entered, complementing the autocomplete and hover assistance introduced in 2026.5.

## Energy, Activity, and operational views

### Activity and entity interfaces (2025.10)

The Logbook is renamed **Activity** in the UI. Add-ons now expose switch entities, the thermostat card accepts water-heater entities, history-panel charts synchronize their zoom ranges, and YAML/template editor toolbars provide undo, redo, and copy controls.

### Activity timeline (2026.7)

Activity now presents Logbook data as a day-grouped timeline with state-colored entity icons, backend-provided state text, and cause indicators for people, automations, and integrations. Compact views let the timestamp switch between absolute and relative time, while entity, device, and area contexts omit redundant names.

### Dashboard, search, and Activity controls (2026.8.0)

The card picker's **By Card** view supports favorites, Quick search can launch Assist, the Clock card can show a date, and Activity can export CSV or clear and reset its data. Entity filters add manufacturer, model, and model-ID criteria, while related-object results expand to scenes, scripts, groups, backing person records, and objects sharing a label or area.

### Energy dashboard configuration (2026.6)

The Energy dashboard can associate a battery state-of-charge sensor so the percentage appears on the distribution node and a battery badge. Grid, solar, battery, gas, and water sources can also have custom names that propagate to energy cards, charts, and statistics.

### Energy dashboard live-flow view (2026.3)

The **Now** view adds badges for current power consumption, gas flow, and water flow. The second dashboard tab is renamed from **Energy** to **Electricity**, energy configuration is split into **Electricity**, **Gas**, and **Water**, and bar-chart tooltips now include the weekday.

### Energy dashboard pie charts and totals (2025.11)

The devices energy graph can switch between bar and pie layouts. Energy cards now also show the selected period's total in their top-right corner.

### Logbook card targets (2025.1)

The Logbook card can select events by entity, device, area, floor, or label.
