# Networking and security

## TLS and sockets

### TLS pre-shared keys (`3.13.0`)

The `ssl` module supports TLS-PSK connections authenticated by pre-shared keys
instead of certificates.

### HTTPS serving and chain inspection (`3.14.0`)

`http.server.HTTPSServer` provides built-in TLS serving. The CLI exposes
`--tls-cert`, `--tls-key`, and `--tls-password-file` through
`python -m http.server`. TLS clients can inspect
raw chains with `SSLSocket.get_verified_chain()` and
`get_unverified_chain()`.

### Fine-grained TLS negotiation (`whatsnew-3.15`)

`SSLContext.set_groups()` configures classical, fixed-field, or post-quantum
key-agreement groups; `get_groups()` and `SSLSocket.group()` inspect supported
and negotiated groups. Configure TLS 1.3 ciphers with `set_ciphersuites()`.
Signature-algorithm setters and inspectors separately control client and
server authentication; some inspectors require OpenSSL 3.2 through 3.5.

### Listen-queue default (`3.15.0b3`)

`socketserver.TCPServer` defaults its request queue size to
`socket.SOMAXCONN`.

## HTTP and URLs

### Query-string bytes and false values (`3.13.0`, `whatsnew-3.14`)

`urllib.parse.parse_qs()` and `parse_qsl()` accept raw or percent-encoded
non-ASCII bytes. Python 3.13 accepts `None` and other false values but rejects
nonzero integers and nonempty sequences with `TypeError`. Later guidance deprecates false
values other than empty strings, bytes-like values, or `None`; normalize inputs
before calling.

### Preserved HEAD redirects (`3.13.0`)

`urllib` retains `HEAD` rather than changing it to `GET` while following a
redirect.

### Standards-aware file URLs (`whatsnew-3.14`)

`url2pathname()` can require a scheme, can resolve local authorities, and
discards query and fragment components. `pathname2url(add_scheme=True)` emits a
complete URL. Windows drive-letter case is preserved.

### HTTP limits and handler customization (`whatsnew-3.15`)

`HTTPConnection` and `HTTPSConnection` accept `max_response_headers`.
`SimpleHTTPRequestHandler` adds `default_content_type` and
`extra_response_headers`; the HTTP-server CLI exposes them as
`--content-type` and `-H/--header` through `python -m http.server`.

### Lossless URL components (`whatsnew-3.15`)

`urlsplit()`, `urlparse()`, and `urldefrag()` accept `missing_as_none`;
`urlunsplit()` and `urlunparse()` accept `keep_empty`. These preserve the
difference between an absent component and a present-but-empty one.

### Robots rules fail closed (`3.15.0b3`)

`urllib.robotparser` implements RFC 9309, distinguishes raw reserved characters
from percent-encoded forms, and no longer ignores a trailing `?`. If the
`robots.txt` is unreachable because of server or network failure, access is
denied.

### Bounded response metadata (`3.15.0b3`)

The `http.client` response-header limit also bounds chunked trailer lines.
Clients process at most 100 interim 1xx responses, preventing an endless
interim-response stream despite socket timeouts.

## Email and application protocols

### Strict email generation (`3.14.0`, `whatsnew-3.15`)

Assigning a `Message` header validates its field name and raises `ValueError`
for invalid characters. Generators quote embedded newlines and reject unsafe
folding or delimiters under `verify_generated_headers`. They also fail rather
than flattening a non-ASCII mailbox inaccurately unless an EAI-capable UTF-8
policy is used.

### Structured email threading (`3.15.0b3`)

The email header registry parses `References` and `In-Reply-To` as lists of
message-ID tokens, avoiding incorrect folding.

### RFC-aware IMAP commands (`3.15.0b3`)

`imaplib` quotes command arguments according to RFC 3501, refreshes capabilities
after authentication, and uses capabilities from the greeting. Commands reject
only NUL, CR, and LF; other control characters valid in quoted strings remain
allowed. Login errors carry `str`, not `bytes`.

## Parser and transport hardening

### Protocol-field validation (`3.15.0b3`)

Control characters are rejected in `data:` URL media types, POP3 commands,
cookie names and values, WSGI headers and status strings, and HTTP tunnel
headers. FTP proxy-copy operations no longer trust a server-supplied PASV IPv4
address by default.

### Safer browser launches (`3.15.0b3`)

`webbrowser.open()` rejects leading-dash URLs. The macOS backend invokes
`/usr/bin/open` directly.
