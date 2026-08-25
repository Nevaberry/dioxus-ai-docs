# Dashboards, Visualizations, and Reporting

Use this reference for dashboard models and APIs, layouts, variables, panels,
transformations, annotations, reporting, rendering, and visualization behavior.

## Dashboard identity, schemas, and APIs

### UID-based analytics APIs (since 11.5.0)

Enterprise Analytics Views deprecates `:dashboardID` endpoints in favor of
`uid/:dashboardUID`. Analytics Summaries similarly deprecates `dashboard_id`
endpoints in favor of `dashboard_uid`.

### Schema validation and series limits (since 12.0.0)

Grafana validates dashboard schemas and can cap the number of series displayed in
a panel. Users can explicitly choose to render all series.

### Home dashboard by UID (since 12.1.0)

Preferences identify the home dashboard by UID rather than numeric dashboard ID.

### Star API removal (since 12.2.0)

Deprecated star APIs based on internal IDs are removed. Clients must stop calling
those endpoints.

### Dashboard and avatar scope checks (since 12.3.0)

From 12.3.2, dashboard API requests enforce previously missing scope checks.
Avatar requests require sign-in and honor their timeout; anonymous avatar
retrieval no longer succeeds.

### UID-only annotation persistence (since 12.3.0)

Annotations saved through a dashboard UID no longer include the internal numeric
dashboard ID. Consumers must not require that internal ID on this path.

### UID-first dashboard routes (since 12.4.0)

Deprecated dashboard endpoints based on internal IDs are removed, and
`/api/dashboards/home` is deprecated. Use UID-based resources and preferences.

### Resource API versions (since 13.0.0)

Dashboard and folder resource APIs graduate to `v1`. A dashboard `v2` API aligns
`TransformationKind` and Dashboard Preferences, and API-server clients can set a
preferred resource version.

### Dashboard and annotation API changes (since 13.1.0)

The Dashboard DTO removes `isStarred`. The mutation API adds annotation CRUD, and
Grafana exposes a panel screenshot API.

### V2 conversion and file home dashboards (since 13.1.0)

V1-to-V2 conversion preserves the timezone user preference and query-variable
sort modes. A file-defined V2 dashboard can be the home dashboard.

## Layout, variables, and dashboard controls

### Custom quick ranges (since 11.6.0)

Dashboard models can define custom quick time ranges, and users can manually add
quick ranges in the time picker.

### Cron-based time regions (since 11.6.0)

Time regions accept cron syntax for schedules beyond the simple recurring-time
controls.

### Scripted dashboards restored (since 11.6.0)

Scripted dashboards are available again after their earlier removal.

### Server quick ranges and compatible exports (since 12.1.0)

Time-picker quick ranges can be configured server-wide. Schema V2 dashboards are
automatically transformed when exported in `V1Resource` mode.

### Library panels and library variables (since 12.1.0)

Library-panel RBAC is generally available and enabled by default, and the
`libraryPanelRBAC` flag is removed. Library elements cannot be set as library
variables.

### Repeated panels and routes (since 12.2.0)

Repeated panels in new layouts support full-screen and embedded solo-panel routes.
Dashboard variables can render beneath a dropdown. Repetition no longer uses
clone keys, and the Inspect drawer can no longer be opened or linked by URL.

### Switch variables (since 12.3.0)

Dashboards add a `Switch` variable type for on/off-style values.

### Controls and panel time settings (since 12.3.0)

Annotations are available from the dashboard controls menu. Time-comparison
windows can be saved, and panel time ranges can be changed in dashboard view mode.

### Non-unique library-panel names (since 12.3.0)

Library-panel names are no longer unique. Use stable identifiers rather than
assuming a name selects one panel.

### Provisioned editing and panel filtering (since 12.4.0)

Dashboard provisioning supports schema V2, and provisioned dashboards can be
edited through their JSON model. Variable regular expressions can transform
display text, and time-series dashboards support per-panel filtering.

### As-code and layout authoring (since 13.0.0)

Dashboards gain an As Code editor with schema validation. Schema-v2 imports can
carry labels. Authors can choose a default layout, add rows and tabs from the side
pane, and define section-level variables.

### Dashboard recovery default (since 13.0.0)

The Restore dashboards feature toggle is enabled by default.

### Scripted dashboards disabled (since 13.2.0)

Scripted dashboards are deprecated and disabled by default. Deployments still
using them must explicitly account for the changed default during upgrades.

### Threshold interpolation and nested layouts (since 13.2.0)

Dashboards support threshold interpolation, nesting to four levels, and tabs
inside nested layouts.

## Transformations and value handling

### Extract fields and RefID filtering (since 11.5.0)

The Extract fields transformation supports Delimiter and RegExp formats.
Transformation filtering can target multiple query RefIDs.

### Variables and rounding (since 11.6.0)

Variables work across all transformations. Unary **Add field from calculation**
adds `round()`.

### State-timeline values (since 12.1.0)

State timelines display `false` and empty strings and support value mappings for
`NaN` and `null`.

### Organize fields and regression (since 12.1.0)

Organize fields adds Auto mode. Regression is generally available. Tempo service
graphs support native histograms, and XY charts accept time values on the x-axis.

### Transpose, trends, and table options (since 12.2.0)

Transpose adds empty-value options. Trend and TimeSeries add value labels, and
Trend supports a logarithmic x-axis. Tables add frozen columns, maximum row
height for variable-height rows, and field-sourced tooltips.

### Expression conversion values (since 13.1.0)

String-to-number conversion preserves null and empty-string values.

### Smoothing (since 12.4.0)

Transformations add smoothing.

## Panels and visualization interaction

### Histogram and OpenTSDB visualization support (since 11.6.0)

Histogram panels handle multiple native histograms. The related OpenTSDB query
support is detailed in the data-source reference.

### Canvas links and confirmations (since 11.6.0)

Canvas elements support one-click links and actions. Visualization actions can
show a confirmation message before execution.

### Standard datetime precision (since 12.0.0)

Standard datetime units are limited to millisecond precision.

### Canvas, pie, and connection behavior (since 12.2.0)

Canvas can disable tooltips on one-click elements and select connection direction
dynamically. Pie charts add ascending, descending, and disabled sorting.

### Pyroscope sampling annotations (since 12.2.0)

Pyroscope can process and display sampling annotations.

### Log field selection and downloads (since 12.3.0)

A field selector integrates with Logs and the Logs table. Downloads honor the
selected fields rather than exporting every field.

### Canvas, time series, and table cells (since 12.3.0)

Canvas background images can come from non-icon fields. Time series panels accept
custom x-axis time units. Tables render array-valued `FieldType.other` fields as
pills, format Pill and JSON cells, and attach links or actions to sparkline cells.

### Geomap MapLibre layers (since 12.3.0)

Geomap accepts a MapLibre style as a base layer, and its previously beta map
layers are generally available.

### Logs visualization default (since 12.4.0)

The new Logs visualization is enabled by default. Logs panels support
transformations with infinite scrolling and unwrapped logs with optional
displayed-field columns. Explore persists log sort order in its URL.

### Panning, heatmaps, and map tiles (since 12.4.0)

Click-and-drag time-range panning is generally available for time series and works
in candlestick, heatmap, and timeline panels. Heatmaps add a linear y-axis.
Geomap XYZ tile layers accept variables and minimum/maximum zoom limits.

### Logs panel controls (since 13.0.0)

Dashboard Logs panels can expose a field selector, persist displayed fields, and
hide the Level field. Plugins can provide a custom log grammar, and OpenTelemetry
log formatting accepts dot-separated label names.

### Gauge visualization contract (since 13.0.0)

The Gauge visualization is generally available, although the `Gauge` React
component is removed from `@grafana/ui`.

### Pyroscope visualizations (since 13.0.0)

Pyroscope adds a Call Tree visualization, accepts `profileIdSelector`, and
includes the complete label set on exemplars.

## Enterprise reporting and rendering

### Report access and addresses (since 11.5.0)

Enterprise reporting adds allowed-email-domain configuration, includes the API
server by default, and deprecates internal IDs.

### Email subjects (since 11.6.0)

Enterprise reporting supports custom report-email subjects.

### Schema V2 reports (since 12.3.0)

Enterprise reporting supports dashboards stored with schema V2.

### Retry and form controls (since 12.4.0)

Reporting retries are productized. The stabilized PDF renderer no longer uses
`newPDFRendering`, and schema-V2 report forms can edit template variables.

### PDF headers, footers, and readiness (since 13.0.0)

Enterprise PDF reporting adds header toggles, configurable footers, and a report
readiness observer.

### Backend URL rendering and recipients (since 13.1.0)

Enterprise reporting supports URL-based rendering in the backend and can limit
report-email recipients to organization members.

### All template-variable types (since 13.2.0)

Enterprise reports no longer restrict template variables through a type
allowlist; templates can use variables regardless of type.

## Deprecated dashboard and visualization surfaces

### Removed dashboard restore experiment (since 12.0.0)

The experimental `dashboardRestore` functionality is removed along with its
feature toggle.

### Datagrid and boot-data deprecations (since 12.4.0)

The Datagrid panel, `GrafanaBootData.config.apps`, and
`GrafanaBootData.config.panels` are deprecated. Library Elements deprecates
`folderFilter` in favor of `folderFilterUIDs`.

### Removed dashboard and logs toggles (since 13.1.0)

`dashboardScene`, `publicDashboardsScene`, and `logsPanelControls` are removed.
