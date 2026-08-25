# Networking, Crypto, Patterns, and I/O

## cURL capability discovery and callbacks

### Feature discovery

Source batch: `8.4.0`.

`curl_version()` includes a `feature_list` associative array covering every
known cURL feature. Each value is a boolean indicating whether the feature is
supported, enabling direct runtime capability checks without decoding only the
legacy bitmask.

### Pre-request hook

Source batch: `8.4.0`.

`CURLOPT_PREREQFUNCTION` installs a callable that runs after a connection is
established but before the request is sent. It must return
`CURL_PREREQFUNC_OK` to proceed or `CURL_PREREQFUNC_ABORT` to cancel.

### Debug callback

Source batch: `8.4.0`.

`CURLOPT_DEBUGFUNCTION` receives the `CurlHandle`, a `CURLINFO_*`
debug-message type, and the message string throughout a request. It cannot be
used with `CURLINFO_HEADER_OUT`, because both rely on the same libcurl
facility.

## cURL redirects, shares, and input sizes

Source batch: `8.5.0`.

cURL share handles may persist across PHP requests for safe connection reuse.

Use `CURLOPT_INFILESIZE_LARGE` instead of `CURLOPT_INFILESIZE` when the latter
is limited to a signed 32-bit size even on a 64-bit system.

`CURLOPT_FOLLOWLOCATION` accepts these redirect modes:

- `CURLFOLLOW_OBEYCODE` for stricter redirect-code handling.
- `CURLFOLLOW_FIRSTONLY` to stop after the first redirect.
- `CURLFOLLOW_ALL` as the equivalent of `true`.

```php
curl_setopt($handle, CURLOPT_FOLLOWLOCATION, CURLFOLLOW_FIRSTONLY);
```

`CURLOPT_BINARYTRANSFER` is deprecated (source batch `8.4-migration`).

## OpenSSL keys, hashing, and derivation

### Modern key types

Source batch: `8.4.0`.

The OpenSSL extension supports x25519, ed25519, x448, and ed448 keys in key
creation and details, signing, and verification.

### Argon2 through OpenSSL

Source batch: `8.4.0`.

`PASSWORD_ARGON2` hashing is available when PHP uses OpenSSL 3.2 or later in
an NTS build.

### Key derivation length

Source batch: `8.5-migration`.

The `key_length` argument of `openssl_pkey_derive()` is deprecated because it
is either ignored or truncates the derived key, which can be unsafe.

## PCRE2 compatibility and syntax

### Pattern compatibility

Source batch: `8.4-migration`.

Bundled PCRE2 10.44 recognizes `{,3}` as a quantifier rather than literal text.
Some character classes also have changed meaning in UCP mode. Audit patterns
that relied on either behavior.

PHP is built without `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK` (source batch
`8.5-migration`). Patterns relying on that extension must be revised.

### Added PCRE2 syntax

Source batch: `8.4.0`.

Bundled PCRE2 supports variable-length lookbehind assertions, permits spaces
between braces in Perl-compatible items, and raises the named-capture limit
from 32 to 128 characters.

The `r` / `(?r)` modifier, when combined with `i`, prevents ASCII and
non-ASCII characters from mixing in caseless matches.

## CSV escaping and argument widths

Source batch: `8.4-migration`.

Relying on the default `escape` argument is deprecated for `fgetcsv()`,
`fputcsv()`, `str_getcsv()`, and their `SplFileObject` equivalents. Pass it
explicitly unless an `SplFileObject` already received an explicit value
through `setCsvControl()`.

```php
$row = fgetcsv($stream, null, ',', '"', '\\');
```

CSV delimiter, enclosure, and escape widths are now validated.

## Exception-based filtering

Source batch: `8.5.0`.

`FILTER_THROW_ON_FAILURE` makes filter validation failures throw instead of
returning a failure value. It cannot be combined with
`FILTER_NULL_ON_FAILURE`; that combination throws `ValueError`.

```php
$id = filter_var($input, FILTER_VALIDATE_INT, FILTER_THROW_ON_FAILURE);
```

## Readline history and HTTP response headers

The `PHP_HISTFILE` environment variable changes the path used for
`.php_history` (source batch `8.4.0`).

```sh
PHP_HISTFILE=/path/to/.php_history
```

The local `$http_response_header` variable is deprecated; use
`http_get_last_response_headers()` (source batch `8.5-migration`).

## Sendmail failures

Source batch: `8.5.0`.

With the sendmail transport, `mail()` reports the actual sendmail error, warns,
and returns `false` when sending fails or the process terminates unexpectedly.
