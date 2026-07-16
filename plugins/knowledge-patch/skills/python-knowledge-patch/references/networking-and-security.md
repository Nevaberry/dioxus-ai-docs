# Networking and security

Use this reference for TLS, HTTP and URLs, email and messaging, sockets, protocol behavior, and parser hardening.

## TLS and cryptography

### Stricter default TLS verification (Python 3.13)
`ssl.create_default_context()` now enables both `VERIFY_X509_PARTIAL_CHAIN` and `VERIFY_X509_STRICT`; strict mode can reject malformed or pre-RFC-5280 certificates previously accepted by OpenSSL. Disabling strictness is possible but discouraged.

```python
ctx = ssl.create_default_context()
ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
```

### TLS certificate chains and pre-shared keys (3.13.0)
`SSLSocket.get_verified_chain()` and `get_unverified_chain()` expose raw TLS certificate chains, and the `ssl` module now supports TLS pre-shared-key mode.

### Nonblocking file-digest failures (3.14.0)
`hashlib.file_digest()` now raises `BlockingIOError` when a nonblocking input has no data available; it no longer silently incorporates spurious null bytes into the digest.

### Fine-grained TLS negotiation controls (Python 3.15 preview)
`SSLContext.set_groups()` selects multiple classical, fixed-field, or post-quantum key-agreement groups, `SSLSocket.group()` reports the negotiated group, and `SSLContext.get_groups()` lists groups compatible with its TLS version bounds. `SSLContext.set_ciphersuites()` configures TLS 1.3 suites separately from pre-1.3 `set_ciphers()`, while new APIs enumerate and constrain client/server signature algorithms and report the selections; some query APIs require OpenSSL 3.2–3.5.

## HTTP, URLs, and web

### Filesystem MIME guesses split from URL guesses (Python 3.13)
Passing filesystem paths to `mimetypes.guess_type()` is soft-deprecated; use the new `mimetypes.guess_file_type(path)` API instead.

### Byte-oriented query-string parsing (3.13.0)
`urllib.parse.parse_qs()` and `parse_qsl()` accept byte strings containing raw or percent-encoded non-ASCII data. They continue to accept `None` and other false values, but reject nonzero integers and nonempty sequences with `TypeError`.

### HTTP response and redirect behavior (3.13.0)
`HTTPConnection.get_proxy_response_headers()` now returns `None`, not `{}`, when no proxy response headers exist. `HTTPResponse.read1()` and `readline()` close the underlying I/O after consuming a known-length body, and redirected `HEAD` requests remain `HEAD` rather than becoming `GET`.

### HTTPS in `http.server` (Python 3.14)
`http.server.HTTPSServer` serves TLS directly, and `python -m http.server` accepts `--tls-cert`, optional `--tls-key`, and optional `--tls-password-file`.

### Standards-aware file URLs (Python 3.14)
`urllib.request.url2pathname()` can require a complete scheme, optionally resolve local authorities, discards query/fragment parts, and rejects nonlocal authorities outside Windows; `pathname2url(add_scheme=True)` can emit a complete URL. Windows drive-letter case is preserved, and colons outside drive prefixes no longer raise `OSError`.

### HTTP limits and response customization (Python 3.15 preview)
`HTTPConnection` and `HTTPSConnection` accept keyword-only `max_response_headers` to override the response-header count limit. `SimpleHTTPRequestHandler` adds `default_content_type` and `extra_response_headers`, while `python -m http.server` exposes matching `--content-type` and `-H`/`--header` controls.

### Lossless URL component parsing (Python 3.15 preview)
`urllib.parse.urlsplit()`, `urlparse()`, and `urldefrag()` accept `missing_as_none`, and the assembly functions accept `keep_empty`, allowing code to distinguish an omitted URI component from an explicitly empty one and preserve that distinction during round trips.

### HTML5 parsing and serialization details (3.15.0b3)
`HTMLParser` recognizes `plaintext`, the `xmp`/`iframe`/`noembed`/`noframes` RAWTEXT elements, and optional RAWTEXT `noscript`, while its tag, comment, CDATA, and whitespace handling is aligned more closely with HTML5. ElementTree's HTML serializer leaves raw-text element content, comments, and processing instructions unescaped, omits a `plaintext` closing tag, and accepts empty attributes represented by `None`.

### RFC 9309 and fail-closed robots rules (3.15.0b3)
`urllib.robotparser` implements RFC 9309 normalization and matching, including distinguishing raw special characters from percent-encoded forms. If `robots.txt` is unreachable because of a server or network error, access is denied rather than allowed.

### Bounded HTTP response metadata (3.15.0b3)
Chunked-response trailers are limited by `HTTPConnection.max_response_headers` (100 by default), and a client skips at most 100 interim 1xx responses, so a peer cannot keep the client busy indefinitely with either stream.

### Safer archive paths and browser launches (3.15.0b3)
On Windows, `shutil.unpack_archive()` skips ZIP members with drive-prefixed paths, and `shutil.move()` resolves symlinks when checking whether a destination lies inside its source. `webbrowser.open()` rejects dash-prefixed URLs, while the new macOS controller invokes `/usr/bin/open` by absolute path.

## Email and messaging

### Hardened email parsing and generation (Python 3.13)
Email generators now quote embedded newlines and refuse to serialize improperly folded or delimited headers unless `Policy.verify_generated_headers` is disabled. `email.utils.getaddresses()` and `parseaddr()` use strict parsing by default and return empty pairs for more invalid inputs; pass `strict=False` for the legacy permissive behavior.

### Hidden Maildir entries (Python 3.13)
`mailbox.Maildir` now ignores files whose names begin with a dot, which can change scans that previously treated such files as messages.

### Maildir metadata operations (3.13.0)
`mailbox.Maildir` adds `get_info()`, `set_info()`, `get_flags()`, `set_flags()`, `add_flag()`, and related methods for manipulating Maildir info and flags without hand-editing message filenames.

### Email field-name validation (3.14.0)
Adding a header with `Message.__setitem__()` or `Message.add_header()` now validates its field name against RFC 5322 and raises `ValueError` for invalid characters.

```python
message = email.message.Message()
message["Bad\nName"] = "value"  # ValueError
```

### Structured email threading headers (3.15.0b3)
Under the modern email policies, `References` and `In-Reply-To` headers are parsed as lists of message-ID tokens rather than unstructured text, preventing incorrect folding. The package also accepts all Python codec aliases and emits registered MIME/IANA charset names.

### RFC-aware IMAP command handling (3.15.0b3)
`imaplib` quotes command arguments such as mailbox names when RFC 3501 requires it, while preserving already quoted arguments. It refreshes capabilities after login or authentication and consumes capabilities advertised in the greeting; only NUL, CR, and LF remain forbidden in command arguments.

## Network addresses and sockets

### IPv4-mapped IPv6 classification (3.14.0)
For an IPv4-mapped `ipaddress.IPv6Address`, `is_multicast`, `is_reserved`, `is_link_local`, `is_global`, and `is_unspecified` are now decided from the mapped IPv4 address.

```python
address = ipaddress.IPv6Address("::ffff:192.0.2.1")
assert address.is_global == address.ipv4_mapped.is_global
```

### Larger default TCP listen queues (3.15.0b3)
`socketserver.TCPServer` now defaults its request queue size to `socket.SOMAXCONN` instead of a small fixed backlog, which can change connection-pressure behavior unless a subclass sets `request_queue_size` explicitly.

## Protocol and parser hardening

### Configurable Expat amplification defenses (3.15.0b3)
Expat parser objects expose `SetBillionLaughsAttackProtectionActivationThreshold()` and `SetBillionLaughsAttackProtectionMaximumAmplification()`, plus matching `SetAllocTracker*()` controls for disproportionate parser memory allocation.

### Stricter protocol field validation (3.15.0b3)
Control characters are rejected in `data:` URL media types, POP3 commands, cookie fields and values, and WSGI header fields, values, parameters, and status strings; HTTP tunnel headers reject CR/LF. XML-RPC method names are escaped during serialization, closing a method-name injection path.
