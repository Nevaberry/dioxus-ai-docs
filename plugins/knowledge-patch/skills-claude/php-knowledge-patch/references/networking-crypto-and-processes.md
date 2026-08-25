# Networking, Crypto, and Processes

## cURL

### Deprecated options and automatic cleanup (8.4-migration, 8.5-migration)

`CURLOPT_BINARYTRANSFER` is deprecated. `curl_close()` and
`curl_share_close()` are also deprecated because their handle objects are
freed automatically.

### Range validation (8.4-migration)

Invalid ranges passed to `curl_multi_select()` raise `ValueError` rather than
following older warning or coercion behavior. Validate caller-provided ranges
or catch the exception where recovery is meaningful.

### Feature discovery (8.4.0)

`curl_version()` includes a `feature_list` associative array for every known
cURL feature, with a boolean showing whether each is supported. Use it for
direct runtime capability checks instead of decoding only the legacy bitmask.

### Pre-request hook (8.4.0)

`CURLOPT_PREREQFUNCTION` installs a callable that runs after connection but
before the request is sent. It must return `CURL_PREREQFUNC_OK` to proceed or
`CURL_PREREQFUNC_ABORT` to cancel.

### Debug callback (8.4.0)

`CURLOPT_DEBUGFUNCTION` receives the `CurlHandle`, a `CURLINFO_*` message type,
and the message string throughout a request. It cannot be combined with
`CURLINFO_HEADER_OUT`, because both use the same libcurl facility.

### Persistent shares and large uploads (8.5.0)

cURL share handles may persist across PHP requests for safe connection reuse.
Use `CURLOPT_INFILESIZE_LARGE` instead of `CURLOPT_INFILESIZE` when the latter
is limited to a signed 32-bit size even on a 64-bit system.

### Redirect modes (8.5.0)

`CURLOPT_FOLLOWLOCATION` accepts `CURLFOLLOW_OBEYCODE` for stricter
redirect-code handling, `CURLFOLLOW_FIRSTONLY` to stop after the first
redirect, and `CURLFOLLOW_ALL` as the equivalent of `true`.

```php
curl_setopt($handle, CURLOPT_FOLLOWLOCATION, CURLFOLLOW_FIRSTONLY);
```

## OpenSSL and password hashing

### Modern key types (8.4.0)

OpenSSL supports x25519, ed25519, x448, and ed448 keys for key creation and
details, signing, and verification.

### OpenSSL-backed Argon2 (8.4.0)

`PASSWORD_ARGON2` hashing is available when PHP uses OpenSSL 3.2 or later in an
NTS build.

### Key derivation length (8.5-migration)

The `key_length` argument of `openssl_pkey_derive()` is deprecated. It is
either ignored or truncates the derived key, which can be unsafe.

## LDAP, signals, sockets, and system calls

### Named LDAP entry points (8.4-migration)

Replace multi-argument `ldap_connect()` and `ldap_exop()` with
`ldap_connect_wallet()` and `ldap_exop_sync()` respectively.

### PCNTL validation and failure values (8.4-migration)

Signal-mask and signal-wait APIs reject empty or non-integer signal lists,
invalid signal numbers or mask modes, and invalid timed-wait durations with
`TypeError` or `ValueError`. Runtime failures consistently return `false`,
never `-1`.

### Deprecated extension entry points (8.5-migration)

Oracle-wallet LDAP calls and constants are deprecated. `socket_set_timeout()`
is deprecated; use `stream_set_timeout()`.

### Stricter process and network validation (8.5-migration)

LDAP options, `pcntl_exec()` arguments and environment, and POSIX limits now
reject documented invalid states with exceptions. SNMP validates hosts, ports,
timeouts, and retries. Socket APIs validate ports, hints, and multicast
contexts.

## Mail transport

### Observable sendmail failures (8.5.0)

With the sendmail transport, `mail()` reports the actual sendmail error, emits
a warning, and returns `false` when sending fails or the process exits
unexpectedly.

