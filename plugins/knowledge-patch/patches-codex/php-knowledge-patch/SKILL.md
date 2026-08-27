---
name: php-knowledge-patch
description: PHP
version: "8.5.0"
license: MIT
metadata:
  author: Nevaberry
---


# PHP Knowledge Patch

Use this skill when PHP work touches the deprecations, runtime changes, extension
behavior, build requirements, security releases, or new APIs documented here.
Start with the breaking-change notes below, then open the topic reference that
matches the code under review.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and Runtime](references/language-and-runtime.md) | Syntax, types, constants, properties, cloning, attributes, errors, comparison, SPL, and core behavior |
| [Database, Sessions, and Persistence](references/database-sessions-and-persistence.md) | MySQLi, PDO, PostgreSQL, Firebird, SQLite, DBA, ODBC, sessions, cookies, and security patch releases |
| [Extensions, System APIs, and Builds](references/extensions-system-and-builds.md) | Extension deprecations, validation, PCNTL, OPcache, dependencies, configuration, streams, locale, and files |
| [Networking, Crypto, Patterns, and I/O](references/networking-crypto-patterns-and-io.md) | cURL, OpenSSL, PCRE, filters, CSV, mail, Readline, and response headers |
| [XML, SOAP, Text, and Media](references/xml-soap-text-and-media.md) | DOM, XMLReader/Writer, XSL, SOAP, SimpleXML, mbstring, Intl formatting, EXIF, and image metadata |

## Breaking changes and deprecations

### Replace deprecated core syntax

- Replace `(boolean)`, `(integer)`, `(double)`, and `(binary)` with `(bool)`,
  `(int)`, `(float)`, and `(string)`.
- End `case` labels with `:` rather than `;`.
- Replace backtick execution with `shell_exec()`.
- Replace non-numeric string `++` with `str_increment()`.
- Use an explicit empty-string key instead of a `null` array offset or a `null`
  key passed to `array_key_exists()`.

### Replace deprecated lifecycle and error paths

- Do not produce output inside a user output handler.
- Make `__debugInfo()` return an array.
- Prefer `__serialize()` and `__unserialize()` over `__sleep()` and
  `__wakeup()`; custom `SplFixedArray` subclasses should use the same modern
  hooks instead of `SplFixedArray::__wakeup()`.
- Replace `trigger_error($message, E_USER_ERROR)` with an exception for a
  recoverable failure or `exit()` for an unrecoverable one.
- Use `fpow()` when IEEE 754 behavior is wanted for zero raised to a negative
  power.

### Update renamed entry points

| Deprecated form | Replacement |
| --- | --- |
| ISO-string `DatePeriod` constructor | `DatePeriod::createFromISO8601String()` |
| Multi-argument Intl calendar setters/constructors | `setDate()`, `setDateTime()`, `createFromDate()`, or `createFromDateTime()` |
| Multi-argument `ldap_connect()` / `ldap_exop()` | `ldap_connect_wallet()` / `ldap_exop_sync()` |
| One-argument `ReflectionMethod::__construct()` | `ReflectionMethod::createFromMethodName()` |
| Two-argument `stream_context_set_option()` | `stream_context_set_options()` |
| `lcg_value()` | `Random\Randomizer::getFloat()` |
| `mysqli_execute()` | `mysqli_stmt_execute()` |
| `socket_set_timeout()` | `stream_set_timeout()` |
| Local `$http_response_header` | `http_get_last_response_headers()` |

### Stop explicitly closing object handles

`curl_close()`, `curl_share_close()`, `finfo_close()`, `imagedestroy()`, and
`xml_parser_free()` are deprecated because their handle objects are freed
automatically.

### Revise closure rebinding

Do not bind an instance to a static closure, bind a method to an unrelated
object, unbind `$this`, bind to an internal-class scope, or rebind the scope of
a closure created from a function or method. These operations are deprecated.

### Account for exception-based validation

APIs that previously warned, coerced, or accepted invalid inputs may now throw
`TypeError`, `ValueError`, or another exception. Validate input or catch the
documented failure around numeric ranges, GD controls, gettext domains, Intl,
mbstring, PCNTL, XML, sockets, SNMP, LDAP, POSIX, Tidy, and database edge cases.

Recursive value comparison now throws `Error` instead of ending in an
`E_ERROR` fatal error. Invalid `round()` modes throw `ValueError` rather than
behaving as `PHP_ROUND_HALF_UP`.

### Update resource and member checks

DBA connections, ODBC connections/results, and stream buckets are objects.
Use explicit failure checks such as `=== false` instead of relying on
`is_resource()` for returned handles.

`SoapClient::$httpurl` and `$sdl` are `Soap\Url` and `Soap\Sdl` objects, and
`$typemap` is an array. Use null checks instead of resource checks for those
members.

### Audit readonly and clone behavior

`__clone()` may reinitialize a readonly property but may not take an indirect
reference to it. The function-form `clone($object, $withProperties)` can
replace properties, including readonly properties, during cloning.

### Rework OPcache and JIT configuration

Setting only a nonzero JIT buffer no longer activates JIT. Select a JIT mode
explicitly, for example:

```ini
opcache.jit=tracing
opcache.jit_buffer_size=64M
```

OPcache is always built in and loaded. Remove legacy
`zend_extension=opcache.so` and `php_opcache.dll` entries; `opcache.enable` and
`opcache.enable_cli` remain available.

## Database and session quick reference

### Modernize PDO usage

- Driver-specific constants and prefixed PostgreSQL/SQLite methods move from
  `PDO` to the corresponding `Pdo\*` driver subclasses.
- Do not use the remote `uri:` DSN scheme.
- Treat string keys in `PDO::FETCH_CLASS` constructor arguments as named
  arguments and provide references for by-reference parameters.
- Do not change fetch mode during a fetch, combine `FETCH_PROPS_LATE` with
  anything except `FETCH_CLASS`, or use `FETCH_INTO` with `fetchAll()`.
- Do not hard-code fetch-flag integer values.

PDO drivers may expose concrete subclasses through `PDO::connect()` or direct
construction. Driver-aware parsing recognizes MySQL backtick identifiers and
hash comments, plus SQLite backtick literals and square-bracket identifiers.

### Clean up sessions and cookies

- Do not call `session_set_save_handler()` with more than two arguments.
- Stop changing deprecated session ID, cookie, and trans-SID settings; make
  storage accept 32-character hexadecimal session IDs.
- Ensure `session_start()` receives a hashmap and a `read_and_close` value with
  a type compatible with `int`.
- Treat `|` in a `$_SESSION` key as a warning condition during serialization.
- Use the `partitioned` cookie option where partitioned cookies are needed.

## Frequently used additions

### Constant expressions and declarations

Closures, first-class callables, and casts may appear in constant expressions,
including attribute arguments and property or parameter defaults.

```php
const LENGTH = strlen(...);
const ZERO = (int) 0.3;
```

Attributes may decorate compile-time non-class constants, and
`#[\Deprecated]` may mark them. `#[\Override]` may be applied to properties;
static properties support asymmetric visibility; promoted constructor
properties may be final.

### cURL request controls

Use `CURLOPT_PREREQFUNCTION` for a callback after connection establishment and
before sending; return `CURL_PREREQFUNC_OK` to proceed or
`CURL_PREREQFUNC_ABORT` to cancel. `CURLOPT_DEBUGFUNCTION` receives the handle,
debug-message type, and message, but cannot be combined with
`CURLINFO_HEADER_OUT`.

`CURLOPT_FOLLOWLOCATION` accepts `CURLFOLLOW_OBEYCODE`,
`CURLFOLLOW_FIRSTONLY`, and `CURLFOLLOW_ALL`. Persistent share handles permit
safe connection reuse across requests.

### Safer validation and localized output

`FILTER_THROW_ON_FAILURE` makes filter validation throw, but cannot be combined
with `FILTER_NULL_ON_FAILURE`.

`IntlListFormatter`, when ICU 67 or newer is available, formats localized AND,
OR, or unit lists in wide, short, or narrow forms.

### XML, SOAP, and images

- DOM XPath and XSL PHP registration accept native callables.
- Namespaced DOM XPath callbacks may use native XPath function syntax.
- SOAP class-map keys may use Clark notation, and SOAP now serializes
  `DateTimeInterface` values as date/time values.
- XSL parameters honor namespaces and XSL evaluation limits are configurable.
- EXIF and image-size inspection support HEIF/HEIC; with ext-libxml,
  `getimagesize()` also recognizes SVG and reports dimension units.

## Security update

Deployments on the affected PHP 8.2, 8.3, 8.4, or 8.5 branches should use the
corresponding security patch release documented in the database and persistence
reference. The PHP 8.5 patch specifically fixes the BCMath out-of-bounds write
identified there.
