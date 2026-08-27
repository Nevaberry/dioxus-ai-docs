# Email and Feeds

## Treat attachments and alternatives as named records

`EmailMultiAlternatives.alternatives` exposes named tuples, so use `.content` and `.mimetype`
instead of tuple indexes (5.2-guide). `EmailMessage.attachments` and
`EmailMultiAlternatives.attachments` likewise expose named tuples (since 5.2).

Add alternatives only through `attach_alternative()`. Directly constructing or appending an
unnamed alternative tuple is not a supported compatibility path. `body_contains()` searches the
primary body plus every attached `text/*` alternative.

```python
message.attach_alternative(html_body, "text/html")
html = message.alternatives[0].content
```

## Use the modern email object model

`EmailMessage.message(policy=...)` defaults to `email.policy.default` and returns the
standard-library `email.message.EmailMessage` (since 6.0). Review subclasses that override
internal underscore methods, because the old Django safe-MIME implementation details no longer
define the result.

`encoding` no longer accepts `email.charset.Charset`, and undocumented subtype properties are
gone. Legacy `MIMEBase` attachment support, `BadHeaderError`, `SafeMIMEText`,
`SafeMIMEMultipart`, `forbid_multi_line_headers()`, and `sanitize_address()` are deprecated.
Build messages with the standard-library API and handle invalid headers as `ValueError`.

## Attach inline MIME parts

The 6.0-guide allows `EmailMessage.attach()` to accept `email.message.MIMEPart`. Create a part with
an inline disposition and content ID, attach it, and reference that ID from an HTML alternative.

```python
from email.message import MIMEPart

part = MIMEPart()
part.set_content(
    data,
    maintype="image",
    subtype="jpeg",
    disposition="inline",
    cid=cid,
)
message.attach(part)
```

Do not use a legacy `MIMEBase` object for new code; it becomes rejected at the 7.0 boundary.

## Pass optional parameters by keyword

Optional arguments beginning with `fail_silently` are deprecated positionally for
`get_connection()`, `mail_admins()`, `mail_managers()`, `send_mail()`, and `send_mass_mail()`.
For `EmailMessage` and `EmailMultiAlternatives`, only `subject`, `body`, `from_email`, and `to`
remain positional. Pass every later constructor argument by keyword (6.0-guide).

The positional compatibility forms become hard errors at the 7.0 email boundary, alongside
removal of the deprecated safe-MIME and address-sanitizing APIs.

## Configure multiple mail backends

The 6.1 development API introduces `MAILERS`, a mapping of named email backends and options.
Sending helpers select an alias with `using`, and application code can retrieve a mailer by alias.
`EMAIL_BACKEND` and its related legacy settings continue to work during the transition but are
deprecated ahead of 7.0.

Keep alias selection explicit in reusable code, and avoid assuming that all aliases share the
same delivery behavior or connection options.

## Format administrator addresses

Tuple-form `(name, address)` entries in `ADMINS` and `MANAGERS` are deprecated. Use one address
string and embed the display name when necessary (since 6.0):

```python
ADMINS = ['"Operations" <ops@example.com>']
```

Tuple-form entries are removed at the 7.0 boundary.

## Add feed stylesheets

`SyndicationFeed` classes accept a `stylesheets` list and emit one `<?xml-stylesheet?>`
processing instruction for each entry (since 5.2). Preserve stylesheet order when consumers
depend on cascade order, and verify the emitted XML rather than only the Python configuration.

## Migration checklist

- Update custom message subclasses for the standard-library return type and modern policy.
- Convert positional optional mail calls to keywords.
- Replace legacy attachment objects with `MIMEPart`.
- Catch `ValueError` for invalid headers instead of `BadHeaderError`.
- Normalize alternatives and attachments around their named fields.
- Convert administrator tuples to RFC-style address strings.
- Test each named mailer alias independently when adopting `MAILERS`.
