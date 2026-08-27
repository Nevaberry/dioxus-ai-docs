# Email and Feeds

Load this reference for email message construction, attachments, connection
selection, custom mail subclasses, administrator addresses, and syndication feeds.

## Treat alternatives and attachments as named records

`EmailMultiAlternatives.alternatives` contains named tuples, so access fields such
as `content` rather than relying on tuple positions. (`5.2-guide`)

```python
html = message.alternatives[0].content
```

`EmailMessage.attachments` and `EmailMultiAlternatives.attachments` also expose
named tuples. Add alternatives only with `attach_alternative()`.
`body_contains()` searches the main body and every attached `text/*`
alternative. (`5.2`)

## Build inline attachments with the modern email API (`6.0-guide`)

Django's mail classes build messages with Python's modern email API.
`EmailMessage.attach()` accepts `email.message.MIMEPart`, including inline
parts whose content ID is referenced by an HTML alternative.

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

## Pass optional arguments by keyword (`6.0-guide`)

For `get_connection()`, `mail_admins()`, `mail_managers()`, `send_mail()`,
and `send_mass_mail()`, arguments from `fail_silently` onward are deprecated
positionally.

For `EmailMessage` and `EmailMultiAlternatives`, only `subject`, `body`,
`from_email`, and `to` remain positional. Pass all later constructor arguments
by keyword. These compatibility paths become hard errors at the Django 7.0
boundary. (`deprecation-roadmap`)

## Update custom message classes (`6.0`)

`EmailMessage.message(policy=...)` defaults to `email.policy.default` and returns
the standard-library `email.message.EmailMessage` rather than Django's deprecated
safe MIME classes. Review subclasses that override private underscore methods.

The undocumented subtype properties are removed, and `encoding` no longer accepts
`email.charset.Charset`. Legacy `MIMEBase` attachments, `BadHeaderError`,
`SafeMIMEText`, `SafeMIMEMultipart`, `forbid_multi_line_headers()`, and
`sanitize_address()` are deprecated. Use the modern email API and handle its
`ValueError` behavior.

Django 7.0 rejects legacy `MIMEBase` attachments and removes these deprecated
helpers and classes. (`deprecation-roadmap`)

## Configure multiple mail backends (`6.1`)

`MAILERS` configures named email backends and their options. Email-sending
functions select a mailer with `using=`, and configured mailers can be retrieved
by alias.

`EMAIL_BACKEND` and its related legacy settings continue to work in 6.1 but are
deprecated ahead of Django 7.0. Plan an explicit alias migration instead of
mixing old and new configuration indefinitely.

## Format administrator addresses (`6.0`)

Tuple-form `ADMINS` and `MANAGERS` entries are deprecated. Use address strings
and embed a display name when needed:

```python
ADMINS = ['"Operations" <ops@example.com>']
```

The tuple compatibility form is removed at the Django 7.0 boundary.
(`deprecation-roadmap`)

## Add feed stylesheets (`5.2`)

`SyndicationFeed` classes accept a `stylesheets` list and emit one
`<?xml-stylesheet?>` processing instruction for each entry.
