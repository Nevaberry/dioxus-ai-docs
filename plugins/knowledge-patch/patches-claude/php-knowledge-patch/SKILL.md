---
name: php-knowledge-patch
description: PHP
version: "8.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# PHP Knowledge Patch

Use this skill when writing, reviewing, debugging, or migrating PHP code whose
behavior may depend on recent language, runtime, extension, or security changes.

## How to use this patch

1. Determine the application's PHP version from `composer.json`, platform
   configuration, the runtime, or the deployment image.
2. Read the reference file for the subsystem being changed.
3. Apply only guidance relevant to the application's version and enabled
   extensions.
4. Prefer explicit validation and exception handling where formerly permissive
   APIs now reject inputs.
5. Run the project's tests under every PHP version it supports, with production
   extensions and INI settings represented.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and runtime](references/language-and-runtime.md) | Syntax, types, closures, attributes, constants, cloning, errors, comparisons, and lifecycle behavior |
| [Configuration, filesystem, and SPL](references/configuration-filesystem-and-spl.md) | INI changes, OPcache, streams, directories, serialization, SPL objects, and deployment patch levels |
| [Databases and PDO](references/databases-and-pdo.md) | PDO, MySQLi, PostgreSQL, Firebird, SQLite, DBA, and ODBC |
| [Networking, crypto, and processes](references/networking-crypto-and-processes.md) | cURL, OpenSSL, LDAP, PCNTL, sockets, SNMP, mail, and process-facing APIs |
| [Text, internationalization, and media](references/text-intl-and-media.md) | PCRE, mbstring, Intl, CSV, filters, hashing, compression, GD, EXIF, and formatting |
| [XML, SOAP, and XSL](references/xml-soap-and-xsl.md) | XML handlers, DOM/XPath, SimpleXML, SOAP, XSLT, and libxml-backed behavior |

## Migration priorities

### Replace deprecated syntax and core idioms

- Replace `(boolean)`, `(integer)`, `(double)`, and `(binary)` with canonical
  casts.
- End `case` labels with `:` and replace backtick execution with an explicit
  process API.
- Replace non-numeric string `++` with `str_increment()`.
- Do not use `null` as an array offset or `array_key_exists()` key; use the
  empty string explicitly only when that is the intended key.
- Replace `trigger_error(..., E_USER_ERROR)` with an exception or `exit()`.
- Avoid deriving non-CLI `argc` and `argv` from a query string.

### Modernize object lifecycle hooks

- Implement `__serialize()` and `__unserialize()` instead of `__sleep()` and
  `__wakeup()` in new or migrated code.
- Make `__debugInfo()` return an array.
- Let object handles clean themselves up instead of calling deprecated close or
  destroy functions for cURL, fileinfo, GD, or XML parser objects.
- Do not take an indirect reference to a readonly property during cloning.

### Remove deprecated configuration assumptions

- Remove `disable_classes`; it no longer has an effect.
- Remove obsolete separate OPcache module loading directives.
- Select an explicit JIT mode; a nonzero buffer alone does not enable JIT.
- Stop changing deprecated session ID, cookie, and trans-SID directives.
- Give directory functions explicit handles and CSV functions explicit escape
  arguments.

### Update extension entry points

- Prefer named factory or operation methods over legacy overloaded signatures
  in DatePeriod, Intl calendars, LDAP, Reflection, and stream contexts.
- Move PDO driver constants and methods to their driver-specific classes.
- Replace legacy SPL aliases with the corresponding `offset*()` methods.
- Pass real callables to XML, DOM XPath, and XSL APIs.
- Replace resource checks for migrated handles with object-aware failure checks.

## Behavior changes to audit

### Exceptions and validation

Many extension APIs now throw `TypeError` or `ValueError` for malformed ranges,
encodings, locales, ports, signal data, configuration keys, and option values.
Validate untrusted input before the call and catch exceptions only where the
application can recover.

Particularly review:

- GD quality, scale, filter, and speed arguments;
- Intl locales, time zones, resource offsets, and calendars;
- mbstring encodings and conversion maps;
- PCNTL signal masks, waits, executable arguments, and environments;
- SNMP hosts, ports, timeouts, and retries;
- socket ports, address hints, and multicast contexts;
- Tidy configuration keys and read-only settings;
- XML, XSL, CSV, hash, and serialization option validation.

### Comparisons, casts, and fetch state

- Recursive value comparisons throw `Error` and can be caught.
- Loose object/boolean comparisons consistently use the object's boolean cast.
- Unrepresentable float-to-integer conversions warn, including `NAN`.
- PDO fetch-mode mutation during a fetch throws; use only valid flag
  combinations and supported fetch methods.
- SimpleXML XPath expressions that do not return node sets warn and return
  `false`.

### Build and runtime assumptions

- OPcache is part of the runtime rather than a separately loaded module.
- Intl and ODBC have newer native dependency assumptions.
- SOAP/session and runtime-linker combinations can affect extension startup.
- Internal extension constants may now expose declared types.
- Upload and temporary filenames are longer than older assumptions allowed.

## High-value additions

### Constant expressions and attributes

Closures, first-class callables, and casts can be used in constant expressions,
including attributes and property or parameter defaults. Attributes can also
decorate compile-time non-class constants, and `#[\Deprecated]` can mark them.

```php
const LENGTH = strlen(...);

#[\Deprecated]
const LEGACY_MODE = 1;
```

### Properties and cloning

Properties can use `#[\Override]`; static properties can use asymmetric
visibility; promoted properties can be final. Function-style `clone` can
replace properties, including readonly properties, while copying an object.

```php
$copy = clone($original, ['id' => $newId]);
```

### Safer failure handling

`FILTER_THROW_ON_FAILURE` turns validation failure into an exception. It is
mutually exclusive with `FILTER_NULL_ON_FAILURE`.

```php
$id = filter_var($input, FILTER_VALIDATE_INT, FILTER_THROW_ON_FAILURE);
```

Fatal errors now carry backtraces, and sendmail transport failures are visible
through warnings and a `false` return from `mail()`.

### HTTP and transport controls

- Use cURL's feature list for direct capability detection.
- Install prerequisite and debug callbacks where request instrumentation needs
  them, respecting incompatible cURL options.
- Choose a redirect mode instead of treating follow-location as only boolean.
- Use persistent cURL share handles for safe cross-request connection reuse.
- Use the large infile-size option where the legacy option is 32-bit limited.

### Database-specific connections

Use `PDO::connect()` or a driver-specific PDO subclass when concrete driver
functionality matters. Driver-aware SQL parsing reduces placeholder mistakes in
quoted identifiers and comments. SQLite can select the transaction mode used by
subsequent `beginTransaction()` calls.

### Internationalization and media

- `IntlListFormatter` formats localized conjunction, disjunction, and unit
  lists when the required ICU support is present.
- Image inspection recognizes HEIF/HEIC and, with libxml, SVG, while reporting
  dimension units that are not always pixels.
- PCRE adds variable-length lookbehind, longer named captures, and restricted
  caseless matching, but also changes parsing of some older patterns.

### Cookies, SOAP, and XSL

- Cookie APIs accept the `partitioned` option.
- SOAP supports namespaced class maps, date/time serialization, schema enum
  cases, reason-text languages, and selectable URI parser backends.
- XSL accepts native callbacks, quote-safe parameters, namespaced parameters,
  and configurable evaluation limits.

## Review checklist

- Search deprecation logs rather than suppressing them.
- Exercise both successful and invalid-input paths.
- Check return types where resources became objects or integers became
  booleans.
- Review extension-specific constants, methods, constructor overloads, and
  default arguments.
- Audit regexes under the bundled PCRE behavior.
- Verify INI files and native-library prerequisites in deployment images.
- Confirm database behavior with the actual driver and server versions.
- Pin a currently secured patch release on every supported PHP branch.

