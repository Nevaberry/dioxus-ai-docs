# Configuration, Filesystem, and SPL

## Configuration and builds

### Session configuration cleanup (8.4-migration)

Calls to `session_set_save_handler()` with more than two arguments are
deprecated. Stop changing `session.sid_length` and
`session.sid_bits_per_character`, and make session storage accept 32-character
hexadecimal IDs. Stop changing the deprecated settings
`session.use_only_cookies`, `session.use_trans_sid`, `session.trans_sid_tags`,
`session.trans_sid_hosts`, and `session.referer_check`; `SID` is deprecated too.

### Configuration validation (8.4-migration)

Session configuration warns for a non-positive `session.gc_divisor` or a
negative `session.gc_probability`. `odbc_fetch_row()` similarly warns and
returns `false` for a row number at or below zero.

### Session payload and option validation (8.5-migration)

Serializing `$_SESSION` with a key containing `|` warns instead of failing
silently. `session_start()` requires its options to be a hashmap and requires
`read_and_close` to have a type compatible with `int`.

### Partitioned cookies (8.5.0)

`session_set_cookie_params()`, `session_get_cookie_params()`, `session_start()`,
`setcookie()`, and `setrawcookie()` recognize the `partitioned` cookie option.

```php
setcookie('sid', $value, ['partitioned' => true]);
```

### OPcache JIT activation (8.4-migration)

The defaults are `opcache.jit=disable` and `opcache.jit_buffer_size=64M`.
Setting only a nonzero buffer no longer enables JIT; select a mode explicitly.
If compiler initialization fails while JIT is enabled, startup is fatal. On
64-bit systems, the maximum `opcache.interned_strings_buffer` is `32767`.

```ini
opcache.jit=tracing
opcache.jit_buffer_size=64M
```

### Built-in OPcache and native dependencies (8.5-migration)

OPcache is always built into and loaded with PHP. Its configure flags and
separate module files are gone. Legacy `zend_extension=opcache.so` and
`php_opcache.dll` entries warn, while `opcache.enable` and
`opcache.enable_cli` still work.

Intl requires ICU 57.1 or newer. ODBC assumes ODBC 3.5 and removes
driver-specific build flags except DB2; use a driver manager on non-Windows
systems.

### Readline history location (8.4.0)

`PHP_HISTFILE` changes the path used for `.php_history`.

```sh
PHP_HISTFILE=/path/to/.php_history
```

## Files, streams, and response metadata

### Stream context options (8.4-migration)

Replace the two-argument `stream_context_set_option()` overload with
`stream_context_set_options()`.

### Stream buckets and failed construction (8.4-migration)

`stream_bucket_make_writeable()` and `stream_bucket_new()` return
`StreamBucket` rather than `stdClass`. A failed `Tidy` construction throws
instead of leaving a broken object after a warning.

Tidy also validates configuration key types and rejects invalid or read-only
settings (8.5-migration).

### Explicit directory handles and HTTP response headers (8.5-migration)

Pass an explicit directory handle to `readdir()`, `rewinddir()`, and
`closedir()` rather than `null`. Replace the local `$http_response_header`
variable with `http_get_last_response_headers()`.

### Zlib stream locking (8.5.0)

`flock()` supports zlib streams instead of always failing to lock them.

## Serialization and SPL

### Serialization lifecycle (8.4-migration)

`SplFixedArray::__wakeup()` is deprecated. Custom subclasses should implement
`__serialize()` and `__unserialize()`. The nonstandard uppercase `S` tag in
serialized strings is deprecated.

### SPL legacy APIs (8.5-migration)

To unregister all autoloaders, iterate over `spl_autoload_functions()` rather
than passing `spl_autoload_call` to `spl_autoload_unregister()`. Prefer
`SplObjectStorage::offsetExists()`, `offsetSet()`, and `offsetUnset()` over
`contains()`, `attach()`, and `detach()`. Stop constructing `ArrayObject` or
`ArrayIterator` over objects.

### SPL objects and files (8.5-migration)

`ArrayObject` no longer accepts enums. `SplFileObject::fwrite()` has a nullable
`length` parameter whose default is `null` rather than `0`.

## Deployment security

### Security patch releases (8.2.33-8.5.9-security)

Deployments on the maintained PHP 8.2, 8.3, 8.4, and 8.5 branches should be at
least PHP 8.2.33, 8.3.33, 8.4.24, and 8.5.9 respectively. PHP 8.5.9 fixes the
BCMath out-of-bounds write vulnerability GHSA-x692-q9x7-8c3f /
CVE-2026-17544.
