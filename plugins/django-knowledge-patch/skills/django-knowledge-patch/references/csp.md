# Content Security Policy (CSP)

*Since 6.0 (December 2025)*

Built-in CSP via middleware, settings, and constants.

## Setup

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    ...
]

TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.csp",
            ...
        ],
    },
}]

from django.utils.csp import CSP

SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, CSP.NONCE],
    "style-src": [CSP.SELF, CSP.NONCE],
    "img-src": [CSP.SELF, "https:"],
}

# Report-only mode (non-blocking)
SECURE_CSP_REPORT_ONLY = {
    "default-src": [CSP.SELF],
    "report-uri": "/csp-report/",
}
```

## Template Nonces

Use `{{ csp_nonce }}` for inline scripts/styles:

```html
<script nonce="{{ csp_nonce }}">doStuff();</script>
```

## Per-view Overrides

```python
from django.views.decorators.csp import csp_override, csp_report_only_override

@csp_override({"default-src": [CSP.SELF], "img-src": [CSP.SELF, "data:"]})
def my_view(request): ...

@csp_override({})  # Disable CSP for this view
def legacy_view(request): ...
```

## CSP Constants

`CSP.SELF`, `CSP.NONE`, `CSP.NONCE`, `CSP.UNSAFE_INLINE`, `CSP.UNSAFE_EVAL`, `CSP.STRICT_DYNAMIC`, `CSP.WASM_UNSAFE_EVAL`, `CSP.UNSAFE_HASHES`, `CSP.REPORT_SAMPLE`.
