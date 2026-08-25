# Networking and security

## TLS and serving

### TLS pre-shared keys

The `ssl` module supports TLS-PSK connections authenticated by pre-shared keys
instead of certificates.

### HTTPS servers and certificate chains

`http.server.HTTPSServer` provides built-in TLS serving. The command-line
server exposes `--tls-cert`, `--tls-key`, and `--tls-password-file`. TLS clients
can inspect raw chains with `SSLSocket.get_verified_chain()` and
`get_unverified_chain()`.

### Fine-grained TLS negotiation

Python 3.15 `SSLContext.set_groups()` configures multiple classical,
fixed-field, or post-quantum key-agreement groups; `get_groups()` and
`SSLSocket.group()` inspect availability and the negotiated group. Configure
TLS 1.3 cipher suites with `set_ciphersuites()`. Signature-algorithm setters and
inspectors separately control client and server authentication; some inspectors
require OpenSSL 3.2 through 3.5.

## URLs and HTTP clients

### Query-string byte handling

`urllib.parse.parse_qs()` and `parse_qsl()` accept raw or percent-encoded
non-ASCII bytes. They continue to accept `None` and other false values but
reject nonzero integers and nonempty sequences with `TypeError`. Later
deprecations narrow accepted false values to empty strings, bytes-like objects,
or `None`.

### Preserved `HEAD` redirects

`urllib` preserves the `HEAD` method while following redirects instead of
upgrading it to `GET`, so redirected probes retain no-body semantics.

### Standards-aware file URLs

`url2pathname()` can require a scheme, optionally resolve local authorities,
and discards query and fragment components. `pathname2url(add_scheme=True)` can
emit a complete URL. Windows drive-letter case is preserved.

### Lossless URL components

Python 3.15 `urlsplit()`, `urlparse()`, and `urldefrag()` accept
`missing_as_none`; `urlunsplit()` and `urlunparse()` accept `keep_empty`. These
options preserve the distinction between absent components and components that
are present but empty.

### Response limits and customization

`HTTPConnection` and `HTTPSConnection` accept `max_response_headers`.
`SimpleHTTPRequestHandler` adds `default_content_type` and
`extra_response_headers`; `python -m http.server` exposes them as
`--content-type` and `-H` or `--header`.

In Python 3.15.0b3, the response-header limit also bounds chunked trailer lines,
and clients skip at most 100 interim 1xx responses. This prevents an endless
response stream despite socket timeouts.

### Larger TCP listen queues

`socketserver.TCPServer` defaults its request queue size to
`socket.SOMAXCONN` in Python 3.15.0b3.

## Email and application protocols

### Strict email generation

Assigning or adding a `Message` header validates the field name and raises
`ValueError` for invalid characters. Generators quote embedded newlines and,
under `verify_generated_headers`, reject unsafe folds or delimiters.

Python 3.15 generators also fail rather than inaccurately flattening a
non-ASCII mailbox unless an EAI-capable UTF-8 policy is used.

### Structured threading headers

In Python 3.15.0b3, the email header registry parses `References` and
`In-Reply-To` as lists of message-ID tokens, preventing incorrect folding.

### RFC-aware IMAP handling

`imaplib` again quotes arguments according to RFC 3501, refreshes capabilities
after authentication, and uses capabilities from the greeting. Commands reject
only NUL, CR, and LF; other control characters valid in quoted strings remain
accepted. Login errors carry `str`, not `bytes`.

### RFC 9309 robots rules

`urllib.robotparser` implements RFC 9309, distinguishes raw reserved characters
from percent-encoded ones, and no longer ignores a trailing `?`. A server or
network failure that makes `robots.txt` unreachable denies all access.

### Strict protocol fields

Python 3.15.0b3 rejects control characters in `data:` URL media types, POP3
commands, cookie fields and values, WSGI headers and status strings, and HTTP
tunnel headers. FTP proxy-copy operations do not trust a server-provided PASV
IPv4 address by default.

## Parsers, archives, and defensive behavior

### XML parser controls and cleanup

For Expat 2.6 reparse deferral, ElementTree and SAX parsers provide `flush()`,
while raw expat parsers expose `GetReparseDeferralEnabled()` and
`SetReparseDeferralEnabled()`. The iterator from `ElementTree.iterparse()` has
`close()` for explicit cleanup.

### XML validation and amplification defenses

Python 3.15 adds `xml.is_valid_name()` and `xml.is_valid_text()` for XML names
and document text. Expat parser objects add controls for allocation
amplification and billion-laughs protections.

### HTML5 parser behavior

In Python 3.15.0b3, `HTMLParser` follows HTML5 rules for tag whitespace,
repeated `=`, comments, CDATA, raw-text elements, and abruptly terminated
constructs. ElementTree's HTML serializer leaves raw-text contents unescaped,
omits a closing `plaintext` tag, and supports empty attributes represented by
`None`.

### Hardened tar extraction

Tar extraction normalizes symbolic-link targets, reapplies filters when links
fall back to copied members and during directory fixups, and never extracts a
rejected member merely because `errorlevel` is zero. Link substitution failures
can raise `LinkFallbackError`.

### Safer archives and browser launches

On Windows, `shutil.unpack_archive()` skips ZIP members with drive prefixes.
`shutil.move()` resolves symlinks before testing whether a destination is
inside its source. `webbrowser.open()` rejects leading-dash URLs, and the macOS
backend invokes `/usr/bin/open` directly.
