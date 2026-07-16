# Upgrading and Compatibility

Batch attribution: `5.1`, `5.2`, `6.0`.

## Contents

- [Release target](#release-target)
- [Runtime, database, and dependency floors](#runtime-database-and-dependency-floors)
- [Removed before the current series](#removed-before-the-current-series)
- [Removed in the current series](#removed-in-the-current-series)
- [Active deprecations](#active-deprecations)
- [Future removal boundaries](#future-removal-boundaries)
- [Behavior changes worth regression-testing](#behavior-changes-worth-regression-testing)

## Release target

Treat 6.0 as the newest finalized Django series in the supplied release catalog. Patch-release
notes exist through 6.0.8. The catalog lists 6.1 and 6.2 as development series, so do not select
either one as a released upgrade target.

## Runtime, database, and dependency floors

### Current finalized series

Django 6.0 supports Python 3.12 through 3.14 and MariaDB 10.6 or newer. It requires `asgiref`
3.9.1 or newer and no longer supports `cx_Oracle`.

For Python 3.12, the documented optional-dependency floors are:

| Dependency | Minimum |
| --- | --- |
| `aiosmtpd` | 1.4.5 |
| `argon2-cffi` | 23.1.0 |
| `bcrypt` | 4.1.1 |
| `docutils` | 0.22 |
| `geoip2` | 4.8.0 |
| Pillow | 10.1.0 |
| `mysqlclient` | 2.2.1 |
| NumPy | 1.26.0 |
| PyYAML | 6.0.2 |
| `psycopg` | 3.1.12 |
| `psycopg2` | 2.9.9 |
| `redis-py` | 5.1.0 |
| Selenium | 4.23.0 |
| `sqlparse` | 0.5.0 |
| `tblib` | 3.0.0 |

### Earlier floors that can affect staged upgrades

- Django 5.2 is an LTS release. As of 5.2.8 it supports Python 3.10 through 3.14 and requires
  PostgreSQL 14+, `gettext` 0.19+, and `oracledb` 2.3+. It drops PostGIS 3.0 and GDAL 3.0.
- Django 5.1 drops MariaDB 10.4, PostgreSQL 12, PostGIS 2.5, PROJ below 6, and GDAL 2.4.
  It requires SQLite 3.31.0+ and `asgiref` 3.8.1+.

## Removed before the current series

Django 5.1 removes all of the following:

- `BaseUserManager.make_random_password()`.
- `Meta.index_together`; use `Meta.indexes`.
- The `length_is` lookup.
- Legacy SHA1 and unsalted password hashers.
- PostgreSQL `CICharField`, `CIEmailField`, `CITextField`, and `CIText`. The fields remain
  importable in historical migrations only.
- `assertFormsetError()` and `assertQuerysetEqual()`.
- Encoded JSON string literals for `JSONField`.
- Positional arguments to `Signer` and `TimestampSigner`.
- `DEFAULT_FILE_STORAGE`, `STATICFILES_STORAGE`, and `get_storage_class()`; use `STORAGES`
  and configured storage aliases.

## Removed in the current series

Django 6.0 removes or hardens these extension points and transitional APIs:

- `BaseConstraint` positional arguments.
- The old `ModelAdmin.lookup_allowed()` override signature without `request`.
- Calling `format_html()` with no arguments or keyword arguments.
- `DjangoDivFormRenderer`, `Jinja2DivFormRenderer`, and `ChoicesMeta`.
- The `CheckConstraint.check` keyword; use `condition`.
- `django.utils.itercompat`.
- ORM joining-column fallback through `get_joining_columns()` and the corresponding
  `ForeignObject` and `ForeignObjectRel` methods.
- `Prefetch.get_current_queryset()`, singular `get_prefetch_queryset()`, and the prefetch
  machinery's fallback to that singular extension hook.
- `FileSystemStorage.OS_OPEN_FLAGS`.
- `FieldCacheMixin.get_cache_name()`.
- `BaseDatabaseOperations.field_cast_sql()`.
- `fetch_returned_insert_columns()` in third-party database backends.
- The `FORMS_URLFIELD_ASSUME_HTTPS` transitional setting; `URLField` now assumes HTTPS.

## Active deprecations

### Application, admin, auth, and static files

- Pass keyword arguments to `Model.save()` and `Model.asave()` rather than positional arguments.
- Do not replace an existing URL converter with `register_converter()`.
- Replace admin `log_deletion()` and `log_action()` extensions with `log_deletions()` and
  `log_actions()`.
- Replace `GeoIP2.coords()` with `lon_lat()`, `GeoIP2.open()` with construction of a `GeoIP2`
  instance, and assignment to `OGRGeometry.coord_dim` with `set_3d()`.
- Pass `find_all` instead of `all` to `django.contrib.staticfiles.finders.find()`.
- Pass a non-`None` user explicitly to `login()` and `alogin()`.
- An async-capable `RemoteUserMiddleware` subclass must override `aprocess_request()` as well as
  `process_request()`.

### ORM, pagination, and database extensions

- Use `order_by` rather than `ordering` with PostgreSQL `ArrayAgg`, `JSONBAgg`, and `StringAgg`.
- Replace PostgreSQL's `OrderableAggMixin`; aggregate classes now opt in through
  `Aggregate.allow_order_by`.
- Keep `Paginator.orphans` and `AsyncPaginator.orphans` below `per_page`.
- Remove `%` from column aliases and annotation names.
- Replace `BaseDatabaseCreation.create_test_db(serialize)` usage with
  `serialize_db_to_string()`.
- Migrate custom backends from `return_insert_columns()` and `fetch_returned_insert_rows()` to
  `returning_columns()` and `fetch_returned_rows()`. The latter accepts `cursor` and
  `returning_params`.

### Email and configuration

- Pass optional arguments beginning with `fail_silently` by keyword to `get_connection()`,
  `mail_admins()`, `mail_managers()`, `send_mail()`, and `send_mass_mail()`.
- Pass only `subject`, `body`, `from_email`, and `to` positionally to `EmailMessage` and
  `EmailMultiAlternatives`; pass later constructor arguments by keyword.
- Replace legacy `MIMEBase` attachments and Django safe-MIME internals with the modern Python
  email API.
- Replace `BadHeaderError` handling with the modern email API's `ValueError` behavior.
- Stop importing `SafeMIMEText`, `SafeMIMEMultipart`, `forbid_multi_line_headers()`, and
  `sanitize_address()`.
- Store `ADMINS` and `MANAGERS` as address strings, embedding a display name if needed:

  ```python
  ADMINS = ['"Operations" <ops@example.com>']
  ```

- `URLIZE_ASSUME_HTTPS = True` opts into the future HTTPS behavior of `urlize` and
  `urlizetrunc` during 6.x, but that transition setting is itself deprecated.

## Future removal boundaries

### Django 6.1

Django 6.1 removes the compatibility paths for:

- `find(..., all=...)` in static-file finders.
- `login()` or `alogin()` receiving `user=None` and inferring the request user.
- `ordering` on PostgreSQL `ArrayAgg`, `JSONBAgg`, and `StringAgg`.
- `RemoteUserMiddleware` subclasses that override only synchronous `process_request()`.

### Django 7.0

Django 7.0 removes or changes:

- The `serialize` argument to `BaseDatabaseCreation.create_test_db()`.
- The PostgreSQL-specific `StringAgg` import and `OrderableAggMixin`; import cross-backend
  `StringAgg` from `django.db.models` and use `order_by` support on aggregates.
- Tuple-form `ADMINS` and `MANAGERS`.
- Support for `orphans >= per_page`.
- The tolerance for `%` in a column alias or annotation; it becomes an immediate `ValueError`.
- Positional optional core-mail parameters, all legacy mail objects listed above, and
  `MIMEBase` attachment acceptance.
- `values_list(flat=True)` without an explicit field name; it raises `TypeError`.
- Top-level `JSONField` filtering with `None` as a way to target JSON `null`. It becomes SQL
  `IS NULL`; use `JSONNull()` to target a JSON null value.
- The `Field.get_placeholder_sql` shim for `get_placeholder`.
- `SQLCompiler.quote_name_unless_alias()`.

```python
from django.db.models import JSONNull

Entry.objects.values_list("id", flat=True)
Entry.objects.filter(payload=JSONNull())
```

## Behavior changes worth regression-testing

- Saving a `FileField` value without a name raises `FieldError`.
- Saving an `ImageField` no longer forces a dimension refresh. A storage backend that resizes
  the image can therefore leave `width_field` and `height_field` stale.
- The admin's `delete_selected` action creates multiple `LogEntry` objects with `bulk_create()`;
  those log entries do not emit `pre_save` or `post_save`.
- `SafeString.__add__()` returns `NotImplemented` for a non-string right operand.
- Single-argument built-in aggregates raise `TypeError` when given the wrong arity.
- Newly generated project settings omit the `debug()` context processor.
- `DEFAULT_AUTO_FIELD` and `AppConfig.default_auto_field` now actually default to
  `django.db.models.BigAutoField`, so projects that explicitly select it can remove that setting.
