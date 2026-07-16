# Email and Feeds

Batch attribution: `5.2-guide`, `5.2`, `6.0-guide`, `6.0`.

## Contents

- [Named attachments and alternatives](#named-attachments-and-alternatives)
- [Inline attachments with MIMEPart](#inline-attachments-with-mimepart)
- [Modern message objects and policy](#modern-message-objects-and-policy)
- [Keyword-only call conventions](#keyword-only-call-conventions)
- [Legacy mail API migration](#legacy-mail-api-migration)
- [Administrator address settings](#administrator-address-settings)
- [Feed stylesheets](#feed-stylesheets)

## Named attachments and alternatives

`EmailMultiAlternatives.alternatives` contains named tuples (since `5.2-guide`), so use named
attributes instead of tuple indexes:

```python
html = message.alternatives[0].content
mime_type = message.alternatives[0].mimetype
```

Items in `EmailMessage.attachments` and `EmailMultiAlternatives.attachments` are also named tuples
(since `5.2`). Preserve their attributes if filtering or copying attachments.

Add an alternative only through `attach_alternative()`; direct alternative construction through
other paths is no longer supported. `body_contains()` checks the main body and every attached
`text/*` alternative.

## Inline attachments with MIMEPart

Django's mail classes use Python's modern email API, and `EmailMessage.attach()` accepts
`email.message.MIMEPart` (since `6.0-guide`). Build an inline part, assign a content ID, attach it,
and reference the ID from an HTML alternative:

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

Ensure `cid` and the HTML `cid:` reference use matching forms.

## Modern message objects and policy

`EmailMessage.message(policy=...)` defaults to `email.policy.default` and returns the
standard-library `email.message.EmailMessage` (since `6.0`), not Django's deprecated safe-MIME
classes.

Review a custom `EmailMessage` subclass if it overrides internal underscore-prefixed construction
methods; those hooks belonged to the former implementation. Also remove assumptions about the
undocumented subtype properties, which are gone. The `encoding` property no longer accepts an
`email.charset.Charset` instance.

Use an explicit modern email policy only when transport or serialization genuinely requires it.
Test headers, multipart structure, and byte serialization after migrating a subclass.

## Keyword-only call conventions

Optional arguments beginning with `fail_silently` are deprecated when passed positionally to
(since `6.0-guide`):

- `get_connection()`
- `mail_admins()`
- `mail_managers()`
- `send_mail()`
- `send_mass_mail()`

For `EmailMessage` and `EmailMultiAlternatives`, only `subject`, `body`, `from_email`, and `to`
remain positional. Pass every later constructor argument by keyword. These positional compatibility
paths are removed in Django 7.0.

## Legacy mail API migration

The following legacy paths are deprecated in Django 6.0 and removed in Django 7.0:

- Attaching legacy `email.mime.base.MIMEBase` objects. Use `MIMEPart`.
- `BadHeaderError`. Handle the modern email API's `ValueError` instead.
- `SafeMIMEText` and `SafeMIMEMultipart`.
- `forbid_multi_line_headers()`.
- `sanitize_address()`.

Do not preserve a compatibility import beyond the removal boundary unless the package still
supports an older Django series and selects imports by supported version.

## Administrator address settings

Tuple-form `(name, address)` entries in `ADMINS` and `MANAGERS` are deprecated in Django 6.0 and
removed in 7.0. Use a single address string and embed the display name where needed:

```python
ADMINS = ['"Operations" <ops@example.com>']
MANAGERS = ["managers@example.com"]
```

## Feed stylesheets

`SyndicationFeed` subclasses accept a `stylesheets` list (since `5.2`). Django emits an
`<?xml-stylesheet?>` processing instruction for each list item. Use this instead of manually
splicing processing instructions into serialized feed XML.
