# Extensions, System APIs, and Builds

## Deprecated entry points and overloads

Source batch: `8.4-migration`.

- Replace the ISO-string `DatePeriod` constructor with
  `DatePeriod::createFromISO8601String()`.
- Replace multi-argument Intl calendar setters and constructors with
  `setDate()`, `setDateTime()`, `createFromDate()`, or
  `createFromDateTime()`.
- Replace multi-argument `ldap_connect()` and `ldap_exop()` with
  `ldap_connect_wallet()` and `ldap_exop_sync()`.
- Replace the two-argument `stream_context_set_option()` with
  `stream_context_set_options()`.
- Replace `lcg_value()` with `Random\Randomizer::getFloat()`.

Passing `SOAP_FUNCTIONS_ALL` or another integer to
`SoapServer::addFunction()` is deprecated. Pass an array of function names,
such as a flattened `get_defined_functions()` result.

The following extension APIs and constants are also deprecated:

- `CURLOPT_BINARYTRANSFER`.
- `SUNFUNCS_RET_*` constants.
- `DOM_PHP_ERR`.
- Obsolete DOM encoding and configuration properties.

The XML-specific `xml_set_object()` and handler-string deprecations are covered
in [XML, SOAP, Text, and Media](xml-soap-text-and-media.md).

## Extension cleanup

### Automatically freed objects

Source batch: `8.5-migration`.

`curl_close()`, `curl_share_close()`, `finfo_close()`, `imagedestroy()`, and
`xml_parser_free()` are deprecated because their handle objects are freed
automatically.

### Deprecated constants, arguments, and settings

Source batch: `8.5-migration`.

- The RFC 7231 Date constants are deprecated.
- The ignored `context` argument of `finfo_buffer()` is deprecated.
- The `MHASH_*` constants are deprecated.
- `intl.error_level` is deprecated; use manual Intl error checks or
  `intl.use_exceptions`.
- Oracle-wallet LDAP calls and constants are deprecated.
- `mysqli_execute()` is deprecated; use `mysqli_stmt_execute()`.
- `socket_set_timeout()` is deprecated; use `stream_set_timeout()` where
  applicable.

The `disable_classes` INI setting has been removed. The `report_memleaks` INI
directive is deprecated.

## Argument validation and failure behavior

### Caller validation replacing fallback behavior

Source batch: `8.4-migration`.

Passing invalid options to hash functions is deprecated. Validate options in
the caller instead of relying on the previous fallback behavior.

Invalid ranges now raise `ValueError` in APIs including:

- `curl_multi_select()`.
- GD quality, speed, scale, and filter operations.
- Empty gettext domains.
- Invalid Intl locales or `ResourceBundle` offsets.
- Malformed mbstring maps or encodings.

Code that previously expected warnings or permissive coercion must validate
arguments or catch the exception.

An invalid `round()` mode throws `ValueError` instead of silently acting as
`PHP_ROUND_HALF_UP`. CSV delimiter, enclosure, and escape widths,
`php_uname()` modes, and the `allowed_classes` option of `unserialize()` are
also validated.

XMLReader, XMLWriter, and XSL operations throw for invalid encodings, null
bytes, incompatible objects, or failed PHP callbacks where applicable.

### PCNTL validation and failures

Source batch: `8.4-migration`.

Signal-mask and signal-wait APIs reject empty or non-integer signal lists,
invalid signal numbers or mask modes, and invalid timed-wait durations with
`TypeError` or `ValueError`. On runtime failure, they consistently return
`false`, never `-1`.

### Extension-specific strict validation

Source batch: `8.5-migration`.

- `bzcompress()` validates block size from 1 through 9 and work factor from 0
  through 250.
- Intl timezone and locale operations reject their documented invalid states
  with exceptions.
- LDAP options reject their documented invalid states with exceptions.
- `pcntl_exec()` arguments and environment reject their documented invalid
  states with exceptions.
- POSIX limits reject their documented invalid states with exceptions.
- SNMP validates host, port, timeout, and retry values.
- Sockets validate ports, hints, and multicast contexts.
- Tidy validates configuration key types and rejects invalid or read-only
  settings.

## OPcache and JIT

### JIT activation and limits

Source batch: `8.4-migration`.

The defaults are `opcache.jit=disable` and
`opcache.jit_buffer_size=64M`. A nonzero buffer alone no longer enables JIT;
configure a JIT mode explicitly.

```ini
opcache.jit=tracing
opcache.jit_buffer_size=64M
```

When JIT is enabled, failure to initialize the compiler is fatal at startup.
On 64-bit systems, the maximum value of
`opcache.interned_strings_buffer` is `32767`.

### Built-in OPcache

Source batch: `8.5-migration`.

OPcache is always built into and loaded with PHP. Its configure flags and
separate module files are gone. Legacy `zend_extension=opcache.so` or
`php_opcache.dll` entries warn, although `opcache.enable` and
`opcache.enable_cli` still work.

## Native dependencies and build combinations

Source batch: `8.5-migration`.

Intl requires ICU 57.1 or newer. ODBC assumes ODBC 3.5 and removes
driver-specific build flags except for DB2, favoring a driver manager on
non-Windows systems.

Building PDO_FIREBIRD requires a C++ compiler and fbclient 3.0 or newer (source
batch `8.4-migration`).

SOAP optionally depends on the session extension. A build without session but
with `--enable-rtld-now` can fail at startup when SOAP is loaded. Avoid that
flag combination or load the session extension (source batch
`8.4-migration`).

## Streams, files, and directory APIs

### Stream buckets and construction failures

Source batch: `8.4-migration`.

`stream_bucket_make_writeable()` and `stream_bucket_new()` return
`StreamBucket` rather than `stdClass`. A failed `Tidy` construction throws
instead of leaving a broken object after a warning.

### Explicit directory handles

Source batch: `8.5-migration`.

Pass an explicit directory handle to `readdir()`, `rewinddir()`, and
`closedir()` instead of `null`.

Restrict `chr()` to integers from 0 through 255 and `ord()` to one-byte
strings.

### Zlib stream locking

`flock()` supports zlib streams instead of always failing to lock them (source
batch `8.5.0`).

## Formatting and locale

Source batch: `8.5-migration`.

A `printf`-family formatter without an explicit precision treats that
precision as zero instead of resetting it.

Passing integer `0` as the locales argument to `setlocale()` is no longer
supported and throws `TypeError`.
