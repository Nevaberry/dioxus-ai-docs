---
name: django-knowledge-patch
description: "Django changes since training cutoff (latest: 6.0) — composite primary keys, CSP middleware, template partials, background tasks, async paginator. Load before working with Django."
license: MIT
version: "1.0.0"
metadata:
  author: Nevaberry
---

# Django Knowledge Patch (5.2 – 6.0)

Claude knows Django through 5.1. This skill covers Django 5.2 LTS (April 2025) and Django 6.0 (December 2025).

## Index

| Topic | Reference | Key features |
|-------|-----------|--------------|
| Models & ORM | [references/models-and-orm.md](references/models-and-orm.md) | Composite PKs, StringAgg cross-db, AnyValue, auto-refresh expressions, NotUpdated |
| Templates | [references/templates.md](references/templates.md) | Partials (`#partial_name`), `simple_block_tag`, `forloop.length` |
| Content Security Policy | [references/csp.md](references/csp.md) | Built-in CSP middleware, nonce support, per-view overrides |
| Background Tasks | [references/background-tasks.md](references/background-tasks.md) | `@task` decorator, enqueue/result API, built-in backends |
| Views & HTTP | [references/views-and-http.md](references/views-and-http.md) | `reverse()` query/fragment, `preserve_request`, `AsyncPaginator`, content negotiation |
| Migration Guide | [references/migration-guide.md](references/migration-guide.md) | Breaking changes, deprecations, version requirements |

## Quick Reference

### Composite Primary Keys (5.2)

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
```

`item.pk` returns a tuple. Filter with `filter(pk=(1, "A755H"))`. Cannot use `ForeignKey` to target composite PK models — use `ForeignObject`. Not supported in admin. See [references/models-and-orm.md](references/models-and-orm.md).

### Template Partials (6.0)

```html
{% partialdef view_count inline %}
  <span id="view-count">{{ video.views }}</span>
{% endpartialdef %}
```

Render in isolation: `render(request, "video.html#view_count", context)` — ideal for htmx. `inline` renders in place; without it, definition is silent. See [references/templates.md](references/templates.md).

### Content Security Policy (6.0)

```python
# settings.py
from django.utils.csp import CSP

MIDDLEWARE = ["django.middleware.csp.ContentSecurityPolicyMiddleware", ...]
TEMPLATES = [{"OPTIONS": {"context_processors": ["django.template.context_processors.csp", ...]}}]

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

Use `{{ csp_nonce }}` in templates for inline scripts/styles. Per-view: `@csp_override({...})` or `@csp_override({})` to disable. Constants: `CSP.SELF`, `CSP.NONE`, `CSP.NONCE`, `CSP.UNSAFE_INLINE`, `CSP.UNSAFE_EVAL`, `CSP.STRICT_DYNAMIC`. See [references/csp.md](references/csp.md).

### Background Tasks (6.0)

```python
from django.tasks import task

@task
def send_email(user_id): ...

result = send_email.enqueue(user_id=42)
result.status  # READY / RUNNING / SUCCESSFUL / FAILED
```

Configure in settings:

```python
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",  # dev/test only
    }
}
```

Built-in backends are dev/test only (`ImmediateBackend`, `DummyBackend`). Production needs third-party backend. Decorator options: `@task(priority=2, queue_name="emails", backend="default")`. Modify before enqueue: `send_email.using(priority=10, run_after=timedelta(minutes=5)).enqueue(...)`. All args must be JSON-serializable. See [references/background-tasks.md](references/background-tasks.md).

### `reverse()` with Query & Fragment (5.2)

```python
reverse("search", query={"q": "django", "page": "2"})  # "/search/?q=django&page=2"
reverse("docs", fragment="section-3")                    # "/docs/#section-3"
```

### `preserve_request` on Redirects (5.2)

```python
redirect("/new/", preserve_request=True)             # 307 instead of 302
redirect("/new/", permanent=True, preserve_request=True)  # 308 instead of 301
```

### New Aggregates (6.0)

| Aggregate | Import | Usage |
|-----------|--------|-------|
| `StringAgg` | `django.db.models.aggregates` | Cross-db. **Breaking:** `delimiter` requires `Value()` |
| `AnyValue` | `django.db.models` | Arbitrary non-null value from group (PG 16+, SQLite, MySQL, Oracle) |

### Key Changes at a Glance

| Change | Version | Impact |
|--------|---------|--------|
| `DEFAULT_AUTO_FIELD` → `BigAutoField` | 6.0 | Remove explicit setting if already set |
| Python 3.10–3.11 dropped | 6.0 | Minimum Python 3.12 |
| `as_sql()` must return tuple params | 6.0 | Custom expressions need update |
| `Field.pre_save()` called multiple times | 6.0 | Must be idempotent |
| MySQL default charset → `utf8mb4` | 5.2 | Automatic, may affect column sizes |
| MariaDB 10.5 dropped | 6.0 | Minimum MariaDB 10.6 |

### Content Negotiation & Response Helpers (5.2)

```python
# Content negotiation
def my_view(request):
    preferred = request.get_preferred_type(["text/html", "application/json"])
    if preferred == "application/json":
        return JsonResponse(data)
    return render(request, "page.html", context)

# String access to response (cached, charset-aware)
response = self.client.get("/")
response.text  # str, instead of response.content.decode()
```

### `simple_block_tag` (5.2)

```python
@register.simple_block_tag
def my_card(nodelist, title):
    return f'<div class="card"><h2>{title}</h2>{nodelist}</div>'
```

```html
{% my_card title="Hello" %}
  <p>Card content here</p>
{% endmy_card %}
```

### `AsyncPaginator` (6.0)

```python
from django.core.paginator import AsyncPaginator

paginator = AsyncPaginator(queryset, per_page=25)
page = await paginator.aget_page(page_number)
```

### Auto-refresh Expression Fields (6.0)

`GeneratedField` values and fields assigned expressions (e.g., `obj.updated_at = Now()`) are automatically refreshed from the database after `save()`. No more manual `refresh_from_db()`. On backends with `RETURNING` (SQLite, PostgreSQL, Oracle): single query. On MySQL/MariaDB: fields are marked deferred.

### `Model.NotUpdated` Exception (6.0)

`Model.save()` raises `Model.NotUpdated` (not generic `DatabaseError`) when a forced update (`force_update=True` / `update_fields`) affects zero rows.

### Other New Features

- **`forloop.length`** (6.0): Total item count in `{% for %}` loops — `{{ forloop.length }}`.
- **`JSONArray`** (5.2): Database function returning JSON array from expressions.
- **New form widgets** (5.2): `ColorInput`, `SearchInput`, `TelInput`.
- **Shell auto-imports** (6.0): `settings`, `connection`, `models`, `functions`, `timezone`.
- **`QuerySet.values()`/`values_list()` ordering** (5.2): SELECT matches specified expression order (was unpredictable — affects `.union()`).
- **Oracle connection pools** (5.2): Via `OPTIONS["pool"]` in `DATABASES`.
- **`startproject`/`startapp`** (6.0): Now creates target directory if it doesn't exist.
- **`{% querystring %}`** (6.0): Now always prefixes output with `?`, accepts multiple positional mapping args.

Full deprecation list in [references/migration-guide.md](references/migration-guide.md).
