---
name: django-knowledge-patch
description: Django
version: 6.0.8
license: MIT
metadata:
  author: Nevaberry
---


# Django Knowledge Patch

Use this patch when implementing, reviewing, testing, or upgrading Django applications and
extensions. Start with the compatibility checks, then open only the topic references needed for
the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading.md](references/upgrading.md) | Runtime and database floors, removals, deprecations, release status, upgrade boundaries |
| [orm-and-databases.md](references/orm-and-databases.md) | Composite keys, expressions, queries, migrations, database options, backend APIs |
| [http-security-auth.md](references/http-security-auth.md) | CSP, content negotiation, redirects, URL handling, authentication, sessions, passwords, DRF |
| [tasks.md](references/tasks.md) | Task declaration, backends, enqueueing, serialization, transactions, context, and results |
| [templates-forms-admin.md](references/templates-forms-admin.md) | Template partials and tags, forms, accessibility, media, and admin behavior |
| [email-and-feeds.md](references/email-and-feeds.md) | Mail backends, modern email objects, attachments, calling conventions, addresses, and feeds |
| [gis.md](references/gis.md) | Geometry APIs, spatial operations, GeoIP2, widgets, validation, and backend support |
| [tooling-testing-serialization.md](references/tooling-testing-serialization.md) | Shell imports, commands, testing, serializers, scaffolding, static files, and protocols |

## Check breaking changes first

Before changing application code or dependencies:

1. Read [upgrading.md](references/upgrading.md) for supported runtimes and database floors.
2. Search for removed APIs before treating an import, signature, or configuration failure as a
   local bug.
3. Check deprecation boundaries against the application's next intended upgrade.
4. For custom database backends, fields, lookups, mail classes, middleware, form renderers, or
   GIS widgets, read the matching extension notes before changing a compatibility shim.

High-risk compatibility changes include:

- Storage configuration must use `STORAGES` and storage aliases; legacy storage settings and
  `get_storage_class()` are gone.
- Removed ORM extension hooks include joining-column fallbacks, singular prefetch-queryset hooks,
  and field-cache naming hooks.
- Custom lookup and expression SQL methods must return parameter tuples, and custom
  `Field.pre_save()` implementations must be idempotent.
- Core mail helpers require optional parameters by keyword on the path to the next removal
  boundary; modern mail objects replace the legacy safe-MIME APIs.
- `ModelAdmin.lookup_allowed()` overrides need `request`; `format_html()` needs arguments; and
  `BaseConstraint` no longer accepts positional arguments.
- URL fields now assume HTTPS, while template `urlize` behavior has a separate transition.

## Work with composite primary keys

Declare a virtual primary key whose component order defines tuple assignment and lookup:

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

item = OrderLineItem.objects.get(pk=(1, "A755H"))
```

Account for these boundaries:

- Migrations cannot add, remove, or convert a composite primary key or its component fields.
  Change the database schema separately and synchronize migration state explicitly.
- Foreign keys, generic relations, and the admin do not support composite-key models.
- Reusable code should inspect `_meta.pk_fields`; component fields do not individually report
  `primary_key=True`.
- The virtual `pk` is omitted from `ModelForm`s, and validation exclusion behavior differs
  between field cleaning and uniqueness validation.
- Most single-expression functions reject composite expressions; `Count("pk")` is supported.
- Raw queries and exact subqueries can work with composite keys in current APIs.

Read [orm-and-databases.md](references/orm-and-databases.md) before writing migrations,
relations, expressions, forms, reusable introspection, or custom database code around them.

## Queue work with the Tasks API

Declare a task and enqueue it instead of invoking the decorated object:

```python
from django.tasks import task

@task(priority=2, queue_name="emails")
def email_users(user_ids):
    ...

result = email_users.enqueue([1, 2])
```

- `ImmediateBackend` executes synchronously; `DummyBackend` only records enqueue operations.
- Production execution requires a third-party backend and worker.
- Pass values that survive a JSON round trip, such as identifiers rather than model instances,
  datetimes, or tuples.
- Use `transaction.on_commit()` when the work depends on newly committed rows.
- Use `aenqueue()` in async code, and verify backend support for priorities, delayed execution,
  and result retrieval.

Read [tasks.md](references/tasks.md) before configuring aliases, overriding options, using task
context, or consuming a `TaskResult`.

## Configure Content Security Policy deliberately

Install `ContentSecurityPolicyMiddleware` and configure `SECURE_CSP`,
`SECURE_CSP_REPORT_ONLY`, or both. Use `django.utils.csp.CSP` constants for quoted source values.

```python
from django.utils.csp import CSP

SECURE_CSP_REPORT_ONLY = {
    "script-src": [CSP.SELF, CSP.NONCE, CSP.STRICT_DYNAMIC],
    "report-uri": "/csp-reports/",
}
```

- Report-only configuration needs a reporting directive and an application-provided receiver.
- Add the CSP context processor before rendering `nonce="{{ csp_nonce }}"`.
- Do not full-page-cache responses containing per-request nonces.
- View decorators replace the global mapping rather than merging it; an empty mapping disables
  that header for the view.

Read [http-security-auth.md](references/http-security-auth.md) for middleware, password,
authentication, session, redirect, negotiation, URL, and cookie behavior.

## Render template fragments

Define and render a named fragment in the template, or append `#<partial-name>` to a template
name to render only that fragment from a view:

```django
{% partialdef filter_controls inline %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}
{% partial filter_controls %}
```

Use `simple_block_tag()` when a paired tag only needs its already-rendered block content. Open
[templates-forms-admin.md](references/templates-forms-admin.md) for custom `BoundField`
selection, error accessibility, script media, parser metadata, and admin extension changes.

## Use current HTTP helpers

- Call `request.get_preferred_type()` with producible media types in server-preference order and
  handle `None` when none are acceptable.
- Pass `query=` and `fragment=` to `reverse()` or `reverse_lazy()`.
- Set `preserve_request=True` on redirects that must preserve the method and body.
- Pass `query_params=` to request factories and test clients for any HTTP method.
- Configure DRF authentication policy explicitly; `LoginRequiredMiddleware` intentionally does
  not enforce login on DRF API views.

## Use current ORM behavior safely

- `values()` and `values_list()` keep the requested projection order.
- The cross-backend `StringAgg` delimiter is an expression; wrap a literal with `Value()`.
- `Aggregate.order_by` is available only on aggregate classes opting in with `allow_order_by`.
- `AnyValue` supplies an arbitrary non-null representative where backend grouping rules need it.
- Database-computed values after `save()` are returned immediately on some backends and become
  deferred until access on MySQL and MariaDB.
- Catch the model-specific `Model.NotUpdated` when a forced update affects no rows.
- Use `AsyncPaginator` and `AsyncPage` in async code.
- Treat `fetch_mode()` and database-level `on_delete` actions as explicit query/schema choices,
  not drop-in changes to existing behavior.

Open [orm-and-databases.md](references/orm-and-databases.md) for detailed backend capabilities,
migration behavior, patch-level fixes, and extension contracts.

## Modernize email integrations

Prefer `email.message.MIMEPart` for structured and inline attachments. Expect
`EmailMessage.message()` to return the standard-library message object with the modern policy.
Treat attachments and alternatives as named tuples where exposed, and add alternatives only with
`attach_alternative()`.

Open [email-and-feeds.md](references/email-and-feeds.md) before maintaining custom mail classes,
multiple backend aliases, legacy MIME attachments, header validation, administrator addresses, or
feed stylesheets.

## Implementation workflow

1. Identify the affected topic and open its reference file.
2. Check both the current behavior and the next removal boundary.
3. Distinguish core support from backend-specific and opt-in capabilities.
4. Preserve async behavior when wrapping views, middleware, authentication, pagination, or tasks.
5. Run Django system checks and focused tests after changing extension points.
6. Test migrations against both model state and database state for state-only operations.
7. Test generated SQL and parameter types for custom ORM components.
8. Verify security headers, nonce uniqueness, redirects, content negotiation, and URL validation
   at the HTTP boundary.
