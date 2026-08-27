# Plugins, projects, and migration

Use this reference when declaring QGIS 4 compatibility, porting plugins to Qt
6, extending application chrome, handling embedded project code, translating
metadata, or migrating user profiles.

## Plugin-delivered application themes (since 4.0)

Plugins can ship themes and custom application styles. Installing a plugin can
therefore change the QGIS application theme without a matching core theme.

## User-defined menus and toolbars (since 4.0)

Users can create menus and toolbars instead of being limited to customization
of built-in ones. Plugins and Processing actions can integrate with these
user-defined UI containers.

## Project trust for embedded Python (since 4.0)

Projects carry granular trust for macros, expression functions, actions, and
attribute-form initialization code. The trust dialog can preview code. Global
policy can allow or deny execution by project or path; do not treat trust in
one embedded-code category as blanket authorization for the others.

## Localized project and layer metadata (since 4.0)

Key project and layer metadata participates in project translation. Translated
values can feed layout labels, map decorations, and other metadata consumers.

## Isolated QGIS 4 settings (since 4.2)

QGIS 4 stores settings separately from QGIS 3. On first startup it performs a
one-time, lossless copy of the loaded QGIS 3 user profile. Subsequent changes
do not synchronize. Installation, profile-management, backup, and enterprise
deployment scripts must target the new QGIS 4 location.

## Advertise QGIS 4 compatibility with a version range

Plugin compatibility is derived from `qgisMinimumVersion` and optional
`qgisMaximumVersion`. Without a maximum, support is assumed only through the
end of the minimum version's major line. To retain QGIS 3.22 support while
joining the QGIS 4 Ready list, declare:

```ini
[general]
qgisMinimumVersion=3.22
qgisMaximumVersion=4.99
```

The Ready list includes a plugin when either bound is at least 4.0.

## Remove the obsolete Qt 6 flag

`supportsQt6=True` has been removed from QGIS core and is no longer recognized.
It cannot advertise QGIS 4 compatibility; remove it and use the version range.

## Check the Qt 6 migration before widening compatibility

QGIS 4 plugins must replace Qt 5-only APIs and direct `PyQt5` imports with Qt 6
equivalents, preferably through `qgis.PyQt`, and must be tested on QGIS 4
before changing metadata. Repository uploads run `pyqgis4-checker`; its Qt6
Check tab identifies affected files and lines, but findings do not block upload
or approval. Treat a clean report as migration evidence, not a substitute for
runtime tests.
