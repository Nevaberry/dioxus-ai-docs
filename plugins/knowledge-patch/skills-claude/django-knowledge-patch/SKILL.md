---
name: django-knowledge-patch
description: Django
version: 6.0.8
license: MIT
metadata:
  author: Nevaberry
---


# Django Knowledge Patch

Use this patch when implementing, reviewing, or upgrading Django applications and
extensions. Start with compatibility boundaries, then load only the references for
the affected subsystem.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading.md](references/upgrading.md) | Runtime and database floors, release status, removals, deprecations, upgrade boundaries |
| [orm-and-databases.md](references/orm-and-databases.md) | Composite keys, queries, expressions, migrations, backend options and extension APIs |
| [http-security-auth.md](references/http-security-auth.md) | CSP, authentication, sessions, redirects, negotiation, URL handling, DRF |
| [tasks.md](references/tasks.md) | Task declaration, backends, enqueueing, serialization, transactions, context and results |
| [templates-forms-admin.md](references/templates-forms-admin.md) | Template partials and tags, form rendering, accessibility and admin behavior |
| [email-and-feeds.md](references/email-and-feeds.md) | Modern mail objects, attachments, keyword-only calls, mail backends and feed stylesheets |
| [gis.md](references/gis.md) | Geometry APIs, spatial operations, GeoIP2, widgets and input limits |
| [tooling-testing-serialization.md](references/tooling-testing-serialization.md) | Shell imports, commands, testing, pagination, serializers, scaffolding and static files |

## Check compatibility before changing code

Read [upgrading.md](references/upgrading.md) before modifying dependencies or
compatibility shims. In particular:

- Match Python, database, GIS library and `asgiref` versions to the target Django
  series.
- Confirm whether a development series is actually finalized before choosing it as
  an upgrade target.
- Search for removed APIs before treating import, argument or extension-hook errors
  as local bugs.
- Review deprecations against the application's next intended upgrade boundary.
- Test third-party database, field, constraint, mail, middleware, admin, prefetch and
  widget extensions against their changed contracts.

High-impact removals and transitions include:

- Replace `DEFAULT_FILE_STORAGE`, `STATICFILES_STORAGE` and
  `get_storage_class()` with `STORAGES` and storage aliases.
- Replace `Meta.index_together` and removed PostgreSQL case-insensitive field APIs.
- Remove legacy SHA1 and unsalted password hashers from configured hasher lists.
- Give `ModelAdmin.lookup_allowed()` overrides a `request` argument.
- Pass arguments to `format_html()` and keyword arguments to `BaseConstraint`.
- Replace removed joining-column, singular prefetch and field-cache extension hooks.
- Return ORM SQL parameters as tuples and make custom `Field.pre_save()` methods
  idempotent.
- Update custom mail classes for the standard-library message object and modern
  email policy; pass optional core-mail parameters by keyword.

## Work with composite primary keys

Declare a virtual primary key whose component order defines tuple semantics:

```python
class OrderLineItem(models.Model):
    pk = models.CompositePrimaryKey("product_id", "order_id")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

item = OrderLineItem.objects.get(pk=(1, "A755H"))
```

Account for these boundaries:

- Do not ask migrations to add, remove or convert a composite primary key or its
  component fields. Change the schema separately and synchronize migration state.
- Foreign keys, generic relations and the admin do not support composite-key models.
- The virtual `pk` is omitted from `ModelForm`; inspect `_meta.pk_fields` in
  reusable code because component fields do not set `primary_key=True`.
- Most single-expression database functions reject a composite expression;
  `Count("pk")` is supported.
- Use tuple values for assignment and filtering in component declaration order.
- Raw queries and composite-key subqueries have additional version-dependent
  support; consult [orm-and-databases.md](references/orm-and-databases.md).

## Queue work with the Tasks API

Declare tasks with `@django.tasks.task`, then enqueue them:

```python
from django.tasks import task

@task(priority=2, queue_name="emails")
def email_users(user_ids):
    ...

result = email_users.enqueue([1, 2])
```

The built-in backends are development and testing facilities:

- `ImmediateBackend` executes synchronously.
- `DummyBackend` records enqueue operations without executing them.
- Production execution requires a third-party backend and worker.

Pass JSON-round-trippable identifiers rather than model instances, datetimes or
tuples. Enqueue database-dependent work from `transaction.on_commit()`. Use
`aenqueue()` from async code. Read [tasks.md](references/tasks.md) before relying
on delayed execution, priorities, result lookup or backend-specific capabilities.

## Configure Content Security Policy deliberately

Install `ContentSecurityPolicyMiddleware` and define `SECURE_CSP`,
`SECURE_CSP_REPORT_ONLY` or both. Use `django.utils.csp.CSP` constants so quoted
source expressions are correct.

```python
from django.utils.csp import CSP

SECURE_CSP_REPORT_ONLY = {
    "script-src": [CSP.SELF, CSP.NONCE, CSP.STRICT_DYNAMIC],
    "report-uri": "/csp-reports/",
}
```

Remember:

- Report-only policy needs a reporting directive and receiver; Django supplies no
  receiver.
- Add the CSP context processor before rendering `nonce="{{ csp_nonce }}"`.
- Do not full-page-cache responses containing a per-request nonce.
- View decorators replace the global mapping rather than merging with it.
- An empty override mapping disables that header for the view.

See [http-security-auth.md](references/http-security-auth.md) for middleware,
authentication, sessions, redirects, negotiation and URL behavior.

## Use current HTTP helpers

- Call `request.get_preferred_type()` with producible media types in
  server-preference order and handle `None`.
- Pass `query=` and `fragment=` to `reverse()` or `reverse_lazy()`.
- Use `preserve_request=True` when a redirect must retain method and body.
- Pass `query_params=` to test clients and request factories for any HTTP method.
- Expect `URLField` to assume HTTPS for schemeless input.
- Configure API authentication in DRF itself; `LoginRequiredMiddleware`
  intentionally does not govern DRF API views.

## Render reusable template fragments

Define and render a named partial in a template:

```django
{% partialdef filter_controls inline %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}

{% partial filter_controls %}
```

Append `#<partial-name>` to a template name to render only that fragment from a
view. Use `simple_block_tag()` for paired tags whose implementation only needs the
rendered block content. See
[templates-forms-admin.md](references/templates-forms-admin.md) for custom
`BoundField` selection, accessible error markup, form media and admin changes.

## Use current ORM capabilities safely

- Expect `values()` and `values_list()` projections to follow call-site order.
- Wrap a literal `StringAgg` delimiter in `Value()` because the delimiter is an
  expression.
- Supply `Aggregate.order_by` only to aggregate classes that opt in with
  `allow_order_by`.
- Use `AnyValue` when grouping rules require an arbitrary non-null representative.
- Treat expression and `GeneratedField` values after `save()` according to backend
  returning support; some backends defer refresh until access.
- Catch the model-specific `Model.NotUpdated` after a forced update affects no rows.
- Use `AsyncPaginator` and `AsyncPage` in asynchronous code.
- Validate fetch policy and database-level foreign-key behavior before adopting
  their newer APIs.

Load [orm-and-databases.md](references/orm-and-databases.md) for backend-specific
behavior and extension contracts.

## Modernize email integrations

Prefer `email.message.MIMEPart` for structured and inline attachments. Expect
`EmailMessage.message()` to return the standard-library message class under the
modern policy. Treat attachments and alternatives as named tuples where Django
exposes them, and add alternatives only with `attach_alternative()`.

Read [email-and-feeds.md](references/email-and-feeds.md) before maintaining custom
mail classes, legacy MIME attachment code, multiple backend configurations,
header-error handling, or `ADMINS` and `MANAGERS` settings.

## Apply async and testing updates

- Use native async authentication, permission, session, pagination and task APIs
  where available.
- Let `method_decorator()` wrap async view methods directly.
- Use a database-enabled test class for database access from threads.
- Expect assertion failures and `test --pdb` to stop at the calling test frame.
- Account for fixture data being available during
  `TransactionTestCase.setUpClass()`.
- Parallel tests can run under the multiprocessing `forkserver` start method.

## Implementation workflow

1. Identify the affected topic and load its reference file.
2. Check removals and future boundaries before selecting a compatibility approach.
3. Distinguish core support from backend-specific support and opt-in capabilities.
4. Preserve async behavior when wrapping views, middleware, authentication or
   database work.
5. Run Django system checks and targeted tests after changing extension points.
6. Test migrations against both model state and database state when an operation
   is state-only.
7. Test generated SQL and parameter types for custom ORM components.
8. Verify security headers, nonce uniqueness, redirects and content negotiation at
   the HTTP level.
