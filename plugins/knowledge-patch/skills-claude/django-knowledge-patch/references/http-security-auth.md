# HTTP, Security, and Authentication

Load this reference for request handling, authentication, sessions, security
headers, redirects, URL construction, and Django REST framework integration.

## Use asynchronous authentication and sessions

`login_required()`, `permission_required()`, and `user_passes_test()` can wrap
async views. Every built-in session engine provides `a`-prefixed async methods,
including `aget()`, `akeys()`, and `acycle_key()`. (`5.1`)

Async interfaces cover user creation, natural-key lookup, permission checks, and
the built-in model and remote-user authentication backends. Auth functions use a
backend's native async method when it exists. `method_decorator()` can wrap async
view methods directly. (`5.2`)

Pass a real user explicitly to `login()` and `alogin()`. The compatibility path
for `user=None` is deprecated in 5.2 and removed in 6.1.
(`5.2`, `deprecation-roadmap`)

Async-capable `RemoteUserMiddleware` subclasses must implement
`aprocess_request()` as well as `process_request()`; the synchronous-only
compatibility path ends in 6.1. (`5.2`, `deprecation-roadmap`)

## Negotiate response content

`HttpRequest.get_preferred_type()` compares the request's `Accept` header with
the media types a view can produce. Supply candidates in server-preference order
and handle `None` when no type is acceptable. (`5.2-guide`)

```python
media_type = request.get_preferred_type(["text/html", "application/json"])
```

`HttpRequest.accepted_types` is ordered by client preference. (`5.2`)

## Construct URLs and redirects

`reverse()` and `reverse_lazy()` accept `query` and `fragment`. A mapping
passed as `query` is URL-encoded, and the fragment follows the generated query
string. (`5.2-guide`)

```python
reverse("nebulae", query={"q": "crab neb"}, fragment="facts")
# "/nebulae/?q=crab+neb#facts"
```

`HttpResponseRedirect`, `HttpResponsePermanentRedirect`, and `redirect()`
accept `preserve_request=True`. This selects 307 instead of 302, or 308 instead
of 301, so the user agent retains the method and body. (`5.2`)

```python
return redirect("target", preserve_request=True)
```

## Configure Content Security Policy

### Install policy middleware (`6.0-guide`)

Add `ContentSecurityPolicyMiddleware` and define enforced and/or report-only
directive mappings in `SECURE_CSP` and `SECURE_CSP_REPORT_ONLY`.
`django.utils.csp.CSP` provides correctly quoted source constants.

```python
from django.utils.csp import CSP

MIDDLEWARE += ["django.middleware.csp.ContentSecurityPolicyMiddleware"]
SECURE_CSP_REPORT_ONLY = {
    "script-src": [CSP.SELF, CSP.NONCE, CSP.STRICT_DYNAMIC],
    "report-uri": "/csp-reports/",
}
```

Report-only mode does not collect reports by itself. Include a reporting directive
and operate a receiver; Django does not provide one.

### Use nonces without defeating them (`6.0-guide`)

Place `CSP.NONCE` in `script-src` or `style-src` and enable
`django.template.context_processors.csp` to expose the lazily generated
`csp_nonce`. Render it as `nonce="{{ csp_nonce }}"`.

Do not full-page-cache nonce-bearing responses, because reuse defeats the
per-request guarantee. `csp_override()` and `csp_report_only_override()` replace,
rather than merge with, the global policy for a view. An empty mapping disables
the corresponding header for that view.

## Update URL and request parsing behavior

`forms.URLField` assumes HTTPS for schemeless input, and
`FORMS_URLFIELD_ASSUME_HTTPS` is removed. `urlize` and `urlizetrunc` still
assume HTTP in 6.0; `URLIZE_ASSUME_HTTPS=True` opts into their future HTTPS
behavior, although that transitional setting is deprecated. (`6.0`)

ASGI accepts multiple `Cookie` headers on HTTP/2 requests. (`6.0`)

Multipart parser classes are customizable. `BinaryField` form input uses strict
Base64 validation, so values accepted only by permissive decoding are invalid.
(`6.1`)

## Validate language and signing inputs

`check_for_language()` rejects language codes longer than 500 characters before
its cached lookup. This includes values flowing through the optional
`set_language()` view. (`5.2.17`)

Signed cookies use an unambiguous salt derivation by default, changing default
signing behavior. Include cookie compatibility and rotation in the 6.1 upgrade
plan. (`6.1`)

## Integrate Django REST framework

DRF 3.16 supports Django 5.1 and 5.2 and Python 3.13. Its minimum versions are
Django 4.2 and Python 3.9. (`5.2-guide`)

`LoginRequiredMiddleware` can coexist with DRF 3.16 but intentionally does not
govern API views. Configure the equivalent access policy through DRF
authentication and permission settings. (`5.2-guide`)

DRF 3.16 improves generated validators for `UniqueConstraint`, including
nullable fields and conditional constraints. Re-test serializer validation when
upgrading. (`5.2-guide`)
