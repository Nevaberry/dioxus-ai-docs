# HTTP, Security, and Authentication

## Negotiate response content

`HttpRequest.get_preferred_type()` compares the request's `Accept` header with the media types a
view can produce (5.2-guide). Supply candidates in server-preference order and handle `None` when
the header permits none of them.

```python
media_type = request.get_preferred_type([
    "text/html",
    "application/json",
])
if media_type is None:
    ...  # Return an appropriate not-acceptable response.
```

`HttpRequest.accepted_types` is ordered by client preference (since 5.2). Keep the distinction
clear: `accepted_types` represents client ordering, while the argument order passed to
`get_preferred_type()` expresses server preference.

## Build URLs and redirects

`reverse()` and `reverse_lazy()` accept `query` and `fragment` (5.2-guide). Mappings supplied to
`query` are URL-encoded, and the fragment follows the query string.

```python
reverse("nebulae", query={"q": "crab neb"}, fragment="facts")
# "/nebulae/?q=crab+neb#facts"
```

`HttpResponseRedirect`, `HttpResponsePermanentRedirect`, and `redirect()` accept
`preserve_request=True` (since 5.2). This selects 307 instead of 302, or 308 instead of 301, so a
user agent reuses the request method and body.

`forms.URLField` assumes HTTPS for a schemeless value (since 6.0), and the transitional
`FORMS_URLFIELD_ASSUME_HTTPS` setting is removed. `urlize` and `urlizetrunc` still assume HTTP in
6.0; set `URLIZE_ASSUME_HTTPS = True` to opt into their later behavior, while recognizing that
this transition setting is itself deprecated before the 7.0 switch.

## Configure Content Security Policy

The 6.0-guide adds built-in CSP support. Install `ContentSecurityPolicyMiddleware` and configure
an enforced mapping in `SECURE_CSP`, a report-only mapping in `SECURE_CSP_REPORT_ONLY`, or both.
Use `django.utils.csp.CSP` constants for source values requiring correct quoting.

```python
from django.utils.csp import CSP

MIDDLEWARE += ["django.middleware.csp.ContentSecurityPolicyMiddleware"]
SECURE_CSP_REPORT_ONLY = {
    "script-src": [CSP.SELF, CSP.NONCE, CSP.STRICT_DYNAMIC],
    "report-uri": "/csp-reports/",
}
```

Report-only mode does not collect reports by itself. Include a reporting directive and implement
a receiver; Django does not supply one.

## Use CSP nonces safely

Include `CSP.NONCE` in `script-src` or `style-src` and enable
`django.template.context_processors.csp` to expose the lazily generated `csp_nonce`. Render it as
`nonce="{{ csp_nonce }}"`.

- Do not full-page-cache a nonce-bearing response; reuse breaks its per-request guarantee.
- `csp_override()` and `csp_report_only_override()` replace the global policy instead of merging.
- Passing an empty mapping to an override disables that header for the view.

## Use async authentication and sessions

Since 5.1, `login_required()`, `permission_required()`, and `user_passes_test()` can wrap async
views. All built-in session engines expose `a`-prefixed async methods such as `aget()`, `akeys()`,
and `acycle_key()`.

Since 5.2, native async APIs also cover user creation, natural-key lookup, user permission checks,
and built-in model and remote-user authentication backends. Async auth helpers use a backend's
native async implementation when present, and `method_decorator()` can wrap async view methods.

Async-capable `RemoteUserMiddleware` subclasses must implement `aprocess_request()` as well as
`process_request()` before the 6.1 removal boundary. Pass a non-`None` user explicitly to
`login()` and `alogin()`.

## Update password administration and hashing

`AdminUserCreationForm` supports creating an account with an unusable password, as does
`AdminPasswordChangeForm` (since 5.1). `AdminSite.password_change_form` can select a custom form
for the site's password-change view (since 6.0).

PBKDF2's default iteration count progresses from 720,000 to 870,000 in 5.1, to 1,000,000 in 5.2,
and to 1,200,000 in 6.0. `ScryptPasswordHasher.parallelism` rises from 1 to 5 in 5.1. Preserve a
valid hasher order so successful authentication can upgrade older hashes.

Exception reporting treats setting names containing `AUTH` as sensitive (since 5.2).

## Integrate Django REST framework 3.16

DRF 3.16 supports Django 5.1 and 5.2 and Python 3.13; its minimums are Django 4.2 and Python 3.9
(5.2-guide). It improves generated validation for `UniqueConstraint`, including nullable fields
and conditional constraints.

`LoginRequiredMiddleware` intentionally does not enforce login on DRF API views. Configure the
equivalent requirement through DRF's authentication and permission policy.

## Construct test requests

`RequestFactory`, `AsyncRequestFactory`, `Client`, and `AsyncClient` accept `query_params` for any
HTTP method (since 5.1):

```python
self.client.post("/items/1", query_params={"action": "delete"})
```

Use this parameter instead of manually appending an encoded query string, especially for methods
whose request body is independent of the URL query.

## Validate language codes and admin URLs

As of 5.2.17, `check_for_language()` rejects language codes longer than 500 characters before its
cached lookup. This includes codes passed through the optional `set_language()` view. Validate or
bound user-controlled language values before relying on the view.

Admin changelists and read-only fields validate `URLField` values with `URLValidator` before
rendering them as links (5.2.17). Invalid values render as plain text.

## Account for protocol and signing changes

ASGI accepts multiple `Cookie` headers in HTTP/2 requests (since 6.0). Do not write middleware
that assumes an HTTP/2 request arrived with only one physical cookie header.

The 6.1 development behavior derives signed-cookie salts unambiguously by default, changing the
framework's default signing behavior. Test existing signed-cookie workflows explicitly when
evaluating that series rather than reproducing the former derivation in application code.

Multipart parser classes are customizable in the 6.1 development API. Keep custom parsing behind
the parser extension point and test size, malformed-input, and async request behavior.
