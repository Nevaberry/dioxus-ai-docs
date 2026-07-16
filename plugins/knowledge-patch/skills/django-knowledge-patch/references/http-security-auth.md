# HTTP, Security, and Authentication

Batch attribution: `5.1`, `5.2-guide`, `5.2`, `6.0-guide`, `6.0`.

## Contents

- [Content Security Policy](#content-security-policy)
- [Content negotiation and accepted media types](#content-negotiation-and-accepted-media-types)
- [URL generation and redirects](#url-generation-and-redirects)
- [Async authentication and sessions](#async-authentication-and-sessions)
- [Passwords and sensitive settings](#passwords-and-sensitive-settings)
- [Django REST framework compatibility](#django-rest-framework-compatibility)
- [Protocol and URL behavior](#protocol-and-url-behavior)

## Content Security Policy

### Enable enforced or report-only policy

Add `django.middleware.csp.ContentSecurityPolicyMiddleware` and define `SECURE_CSP`,
`SECURE_CSP_REPORT_ONLY`, or both (since `6.0-guide`). Each setting maps CSP directive names to
source lists or other directive values.

Use constants from `django.utils.csp.CSP`; they supply correct CSP quoting:

```python
from django.utils.csp import CSP

MIDDLEWARE += ["django.middleware.csp.ContentSecurityPolicyMiddleware"]
SECURE_CSP_REPORT_ONLY = {
    "script-src": [CSP.SELF, CSP.NONCE, CSP.STRICT_DYNAMIC],
    "report-uri": "/csp-reports/",
}
```

A report-only header does not collect reports by itself. Include `report-uri` or the appropriate
reporting directive and operate a report receiver; Django does not provide one.

### Use per-request nonces safely

Put `CSP.NONCE` in `script-src` or `style-src`, enable
`django.template.context_processors.csp`, and add `nonce="{{ csp_nonce }}"` to the permitted
inline element. The context value is generated lazily.

Do not full-page-cache a nonce-bearing response. Reusing a cached nonce breaks its per-request
security property. If a fragment cache contains nonce-bearing markup, verify that the containing
response still gets a matching fresh header and value.

### Override a view policy

`csp_override()` and `csp_report_only_override()` replace the corresponding global policy for the
decorated view; they do not merge mappings. Passing an empty mapping disables that header for the
view.

## Content negotiation and accepted media types

Use `HttpRequest.get_preferred_type()` to choose among the response media types a view can produce
(since `5.2-guide`):

```python
media_type = request.get_preferred_type(["text/html", "application/json"])
if media_type is None:
    # Return an appropriate not-acceptable response.
    ...
```

List candidates in server-preference order and handle `None` when no candidate is acceptable.
`HttpRequest.accepted_types` is sorted by the client's preference (since `5.2`).

## URL generation and redirects

### Add query strings and fragments during reversing

`reverse()` and `reverse_lazy()` accept `query` and `fragment` (since `5.2-guide`). Mapping values
passed to `query` are URL-encoded. The fragment follows the generated query string:

```python
reverse("nebulae", query={"q": "crab neb"}, fragment="facts")
# "/nebulae/?q=crab+neb#facts"
```

### Preserve request method and body

`HttpResponseRedirect`, `HttpResponsePermanentRedirect`, and `redirect()` accept
`preserve_request` (since `5.2`). When true, a temporary redirect uses status 307 rather than 302,
and a permanent redirect uses 308 rather than 301. The user agent can therefore resend the method
and body:

```python
return redirect("target", preserve_request=True)
```

## Async authentication and sessions

### Decorate async views

`login_required()`, `permission_required()`, and `user_passes_test()` can wrap async views (since
`5.1`). `method_decorator()` can wrap async view methods (since `5.2`). Keep sync and async call
paths intact in custom decorators.

### Use native async auth interfaces

Async auth support covers user creation, natural-key lookup, permission checks, and the built-in
model and remote-user backends (since `5.2`). Auth functions use a backend's native async method
when it provides one, rather than always wrapping its sync method.

An async-capable `RemoteUserMiddleware` subclass must implement `aprocess_request()` as well as
`process_request()`. The sync-only compatibility path is removed in Django 6.1.

### Use async sessions

Every built-in session engine exposes `a`-prefixed async operations (since `5.1`), including
`aget()`, `akeys()`, and `acycle_key()`. Use these methods in an async request path rather than
performing synchronous session I/O there.

## Passwords and sensitive settings

### Admin password forms

`AdminUserCreationForm` was added in `5.1`. It and `AdminPasswordChangeForm` can disable
password-based authentication by saving an unusable password. `AdminSite.password_change_form`
can select a custom form for the admin site's password-change view (since `6.0`).

### Hashing defaults

The default PBKDF2 iteration count changes as follows:

- 870,000 in Django 5.1, up from 720,000.
- 1,000,000 in Django 5.2.
- 1,200,000 in Django 6.0.

`ScryptPasswordHasher.parallelism` rises from 1 to 5 in Django 5.1. Account for CPU and memory
cost when capacity-testing authentication workloads.

Exception reporting treats setting names containing `AUTH` as sensitive (since `5.2`). Do not
depend on exception pages exposing those values.

## Django REST framework compatibility

DRF 3.16 supports Django 5.1 and 5.2 and Python 3.13. It raises its own minimums to Django 4.2 and
Python 3.9.

Django's `LoginRequiredMiddleware` can coexist with DRF 3.16, but DRF intentionally exempts API
views from that middleware's login requirement. Configure equivalent protection through DRF's
authentication and permission policy.

DRF 3.16 improves generated validation for `UniqueConstraint`, including nullable fields and
conditional constraints. Regression-test serializer validation if custom validators duplicated a
former workaround.

## Protocol and URL behavior

- ASGI accepts multiple `Cookie` headers on HTTP/2 requests (since `6.0`). Preserve rather than
  incorrectly collapsing protocol-valid repeated headers in ASGI middleware.
- `forms.URLField` assumes `https` for a schemeless value (since `6.0`); the
  `FORMS_URLFIELD_ASSUME_HTTPS` transition setting is gone.
- `urlize` and `urlizetrunc` still assume HTTP in 6.0. Set `URLIZE_ASSUME_HTTPS = True` to opt into
  the planned HTTPS behavior during 6.x, but remove the setting when upgrading because it is
  transitional and deprecated.
