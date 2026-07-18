---
name: django-knowledge-patch
description: Django
license: MIT
version: 6.0.8
metadata:
  author: Nevaberry
---

# Django Knowledge Patch

Use this patch when implementing, reviewing, or upgrading Django applications and extensions.
Start with the breaking-change checks, then load only the topic references needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading.md](references/upgrading.md) | Runtime and database floors, removals, deprecations, compatibility boundaries, release status |
| [orm-and-databases.md](references/orm-and-databases.md) | Composite keys, expressions, queries, migrations, database options, backend extension APIs |
| [http-security-auth.md](references/http-security-auth.md) | CSP, content negotiation, redirects, URL generation, authentication, sessions, passwords, DRF |
| [tasks.md](references/tasks.md) | Task declaration, backends, enqueueing, options, serialization, transactions, context, results |
| [templates-forms-admin.md](references/templates-forms-admin.md) | Template partials and tags, form rendering, accessibility, admin behavior |
| [email-and-feeds.md](references/email-and-feeds.md) | Modern email objects, attachments, keyword-only calls, address settings, feed stylesheets |
| [gis.md](references/gis.md) | Geometry APIs, spatial operations, GeoIP2, widgets, backend support |
| [tooling-testing-serialization.md](references/tooling-testing-serialization.md) | Shell imports, commands, testing, pagination, serializers, scaffolding, static files |

## Check breaking changes first

Before changing application code or dependencies:

1. Read [upgrading.md](references/upgrading.md) for runtime and database support.
2. Search for removed APIs before treating an import or argument error as a local bug.
3. Review deprecations against the application's intended next upgrade boundary.
4. For custom database backends, fields, lookups, constraints, mail classes, middleware, or widgets,
   read the matching extension notes before modifying compatibility shims.

Pay particular attention to these changes:

- Require Python 3.12 or newer for the current finalized series.
- Replace removed storage settings and helpers with `STORAGES` and storage aliases.
- Stop using `Meta.index_together`, legacy password hashers, removed PostgreSQL CI fields,
  old prefetch extension hooks, joining-column fallbacks, and removed field-cache hooks.
- Pass custom ORM SQL parameters as tuples.
- Make custom `Field.pre_save()` implementations idempotent.
- Update custom email subclasses for the standard-library `EmailMessage` result and modern policy.
- Pass optional core-mail parameters by keyword.
- Update custom geometry widget templates that relied on inline JavaScript.
- Give `ModelAdmin.lookup_allowed()` overrides a `request` argument.
- Pass arguments to `format_html()` and keyword arguments to `BaseConstraint`.

## Work with composite primary keys

Declare a virtual primary key whose component order defines tuple semantics:

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

item = OrderLineItem.objects.get(pk=(1, "A755H"))
```

Account for the current limits:

- Do not ask migrations to add, remove, or convert a composite primary key or its components.
  Change the schema separately and synchronize migration state explicitly.
- Do not expect foreign keys, generic relations, or the admin to support a composite-key model.
- Inspect `_meta.pk_fields` in reusable code; component fields do not set `primary_key=True`.
- Expect the virtual `pk` to be absent from `ModelForm`s.
- Use `Count("pk")` only where a database function explicitly supports composite expressions.
- Use tuple values for `pk` assignment and filtering in component declaration order.

Read [orm-and-databases.md](references/orm-and-databases.md) for validation, expression,
introspection, raw-query, subquery, and migration details.

## Queue work with the Tasks API

Declare tasks with `@django.tasks.task`, then enqueue them instead of calling them:

```python
from django.tasks import task

@task(priority=2, queue_name="emails")
def email_users(user_ids):
    ...

result = email_users.enqueue([1, 2])
```

Treat the built-in backends as development and test facilities:

- `ImmediateBackend` executes synchronously.
- `DummyBackend` records enqueue operations without executing them.
- Use a third-party backend and worker for production execution.

Pass JSON-round-trippable values such as identifiers, not model instances, datetimes, or tuples.
When work depends on committed rows, enqueue it from `transaction.on_commit()`.
Use `aenqueue()` in async code and read [tasks.md](references/tasks.md) before relying on
priorities, delayed execution, result lookup, or backend-specific capabilities.

## Configure built-in CSP deliberately

Install `ContentSecurityPolicyMiddleware` and configure `SECURE_CSP`,
`SECURE_CSP_REPORT_ONLY`, or both. Use `django.utils.csp.CSP` constants so quoted source
expressions are correct.

```python
from django.utils.csp import CSP

SECURE_CSP_REPORT_ONLY = {
    "script-src": [CSP.SELF, CSP.NONCE, CSP.STRICT_DYNAMIC],
    "report-uri": "/csp-reports/",
}
```

Remember:

- Report-only policy does not collect reports by itself; configure a reporting directive and receiver.
- Add the CSP context processor before rendering `nonce="{{ csp_nonce }}"`.
- Do not full-page-cache responses containing a per-request nonce.
- View decorators replace the global mapping rather than merging with it.
- An empty override mapping disables that header for the view.

Read [http-security-auth.md](references/http-security-auth.md) for middleware placement,
authentication, password, redirect, negotiation, and URL behavior.

## Render fragments with template partials

Define reusable fragments directly in templates:

```django
{% partialdef filter_controls inline %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}

{% partial filter_controls %}
```

Render only one fragment from a view by appending `#<partial-name>` to the template name.
Use `simple_block_tag()` for paired tags whose implementation only needs rendered block content.
Read [templates-forms-admin.md](references/templates-forms-admin.md) for partial syntax,
custom `BoundField` selection, accessible error markup, form media, and admin changes.

## Use current HTTP helpers

- Call `request.get_preferred_type()` with producible media types in server-preference order;
  handle `None` when the `Accept` header allows none of them.
- Pass `query=` and `fragment=` to `reverse()` or `reverse_lazy()` instead of assembling URLs.
- Pass `preserve_request=True` to redirects that must retain the request method and body.
- Use `query_params=` with test clients and request factories for any HTTP method.
- Expect `URLField` to assume HTTPS for schemeless input.

## Use current ORM capabilities safely

- Expect `values()` and `values_list()` projection order to follow the call-site order.
- Wrap a literal `StringAgg` delimiter in `Value()`; the delimiter is an expression.
- Use `Aggregate.order_by` only on aggregate classes that opt in with `allow_order_by`.
- Use `AnyValue` when grouping rules require an arbitrary non-null representative.
- Treat database expressions and `GeneratedField` values after `save()` according to backend
  returning support; some backends defer the refresh until field access.
- Catch the model-specific `Model.NotUpdated` for a forced update that affects no rows.
- Use `AsyncPaginator` and `AsyncPage` in asynchronous code.

Load [orm-and-databases.md](references/orm-and-databases.md) for backend-specific behavior and
the extension contracts that affect custom expressions, fields, schema editors, and backends.

## Modernize email integrations

Prefer `email.message.MIMEPart` for inline and other structured attachments.
Expect `EmailMessage.message()` to return the standard-library message class under the modern
email policy. Treat attachments and alternatives as named tuples where Django exposes them,
and add alternatives only with `attach_alternative()`.

Read [email-and-feeds.md](references/email-and-feeds.md) before maintaining custom mail classes,
legacy MIME attachment code, header-error handling, or `ADMINS` and `MANAGERS` settings.

## Apply async and testing updates

- Use native async authentication, permission, session, pagination, and task APIs where available.
- Let `method_decorator()` wrap async view methods directly.
- Use a database-enabled test class for database access from threads.
- Expect assertion failures and `test --pdb` to stop at the calling test frame.
- Account for fixture data being available during `TransactionTestCase.setUpClass()`.
- Allow parallel tests under the multiprocessing `forkserver` start method.

Read [tooling-testing-serialization.md](references/tooling-testing-serialization.md) for shell,
management-command, testing, serializer, scaffolding, and static-file behavior.

## Implementation workflow

1. Identify the affected topic and load its reference file.
2. Check removals and future boundaries before selecting a compatibility approach.
3. Distinguish core support from backend-specific support and opt-in capabilities.
4. Preserve async behavior when wrapping views, middleware, authentication, or database work.
5. Run Django system checks and targeted tests after changing extension points.
6. Test migrations against both model state and database state when an operation is state-only.
7. Test generated SQL and parameter types for custom ORM components.
8. Verify security headers, nonce uniqueness, redirects, and content negotiation at HTTP level.
