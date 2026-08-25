# Upgrading and Compatibility

## Choose a release target deliberately

The `release-and-upgrade-catalog` snapshot identifies 6.0 as the newest finalized series and
lists 6.1 and 6.2 as development series; patch notes are present through 6.0.8. Do not infer that
a development series is a released deployment target merely because its feature notes exist.

The 5.2 line is LTS. Its runtime range, as of 5.2.8, is Python 3.10 through 3.14 (5.2). Django
6.0 supports Python 3.12 through 3.14 (6.0). The 6.1 development notes also specify Python 3.12
through 3.14 and expect mainstream support through April 2027 and extended support through
December 2027 (6.1).

## Check database and dependency floors

- For 5.1, use SQLite 3.31.0+, `asgiref` 3.8.1+, MariaDB newer than 10.4, PostgreSQL newer than
  12, PostGIS newer than 2.5, PROJ 6+, and GDAL newer than 2.4 (5.1).
- For 5.2, use PostgreSQL 14+, `gettext` 0.19+, and `oracledb` 2.3+; PostGIS 3.0 and GDAL 3.0
  are no longer supported (5.2).
- For 6.0, use MariaDB 10.6+ and `asgiref` 3.9.1+; `cx_Oracle` is no longer supported (6.0).
- The 6.1 development floor is PostgreSQL 15, MySQL 8.4, MariaDB 10.11, and SQLite 3.37 (6.1).

For Python 3.12 with 6.0, the documented optional-dependency floors are `aiosmtpd` 1.4.5,
`argon2-cffi` 23.1.0, `bcrypt` 4.1.1, `docutils` 0.22, `geoip2` 4.8.0, Pillow 10.1.0,
`mysqlclient` 2.2.1, NumPy 1.26.0, PyYAML 6.0.2, `psycopg` 3.1.12, `psycopg2` 2.9.9,
`redis-py` 5.1.0, Selenium 4.23.0, `sqlparse` 0.5.0, and `tblib` 3.0.0. Compatibility with
`sqlparse` 0.5.5 specifically requires Django 6.0.8 or newer (6.0.8).

## Remove obsolete 5.1-era APIs

The following compatibility paths are already removed in 5.1:

- `BaseUserManager.make_random_password()`, `Meta.index_together`, and the `length_is` lookup.
- Legacy SHA1 and unsalted password hashers.
- PostgreSQL `CICharField`, `CIEmailField`, `CITextField`, and `CIText`; historical migrations may
  continue to reference the field classes.
- `assertFormsetError()` and `assertQuerysetEqual()`.
- Encoded JSON string literals for `JSONField`.
- Positional arguments to `Signer` and `TimestampSigner`.
- `DEFAULT_FILE_STORAGE`, `STATICFILES_STORAGE`, and `get_storage_class()`; use `STORAGES` and
  storage aliases.

Also migrate code deprecated in 5.1:

- Pass `Model.save()` and `Model.asave()` arguments by keyword.
- Do not replace an existing URL converter with `register_converter()`.
- Replace admin `log_deletion()` and `log_action()` with `log_deletions()` and `log_actions()`.
- Replace `GeoIP2.coords()` with `lon_lat()`, `GeoIP2.open()` with construction, and assignment to
  `OGRGeometry.coord_dim` with `set_3d()`.

## Remove obsolete 6.0-era customization APIs

On 6.0, account for these hard removals:

- `BaseConstraint` positional arguments, `CheckConstraint(check=...)`, and `ChoicesMeta`.
- `ModelAdmin.lookup_allowed()` overrides without `request`.
- Calling `format_html()` without arguments or keyword arguments.
- `DjangoDivFormRenderer`, `Jinja2DivFormRenderer`, and `django.utils.itercompat`.
- Joining-column fallbacks and the related `ForeignObject`/`ForeignObjectRel` joining-column
  methods.
- `Prefetch.get_current_queryset()`, singular `get_prefetch_queryset()`, and the fallback to that
  singular prefetch hook.
- `FileSystemStorage.OS_OPEN_FLAGS` and `FieldCacheMixin.get_cache_name()`.
- `BaseDatabaseOperations.field_cast_sql()` and `fetch_returned_insert_columns()`.
- `FORMS_URLFIELD_ASSUME_HTTPS`; `URLField` now assumes HTTPS directly.

## Prepare for the 6.1 removal boundary

The `deprecation-roadmap` says 6.1 removes the 5.2 compatibility forms below:

- `django.contrib.staticfiles.finders.find(..., all=...)`; use `find_all`.
- Calling `login()` or `alogin()` with `user=None`; pass the user explicitly.
- `ordering` on PostgreSQL `ArrayAgg`, `JSONBAgg`, and `StringAgg`; use `order_by`.
- Async-capable `RemoteUserMiddleware` subclasses implementing only synchronous
  `process_request()`; add `aprocess_request()`.

## Prepare for the 7.0 database and configuration boundary

Before 7.0:

- Stop passing `serialize` to `BaseDatabaseCreation.create_test_db()`; use
  `serialize_db_to_string()` for serialization.
- Import the cross-backend `StringAgg` and stop using PostgreSQL `OrderableAggMixin`.
- Convert `(name, address)` values in `ADMINS` and `MANAGERS` to address strings containing any
  display name.
- Keep paginator `orphans` below `per_page`.
- Remove `%` from column aliases and annotation names; it becomes an immediate `ValueError`.
- Pass a field name to `values_list(..., flat=True)`.
- Use `JSONNull()` to query a top-level JSON `null`; in 7.0, plain `None` means SQL `NULL`.
- Replace the `Field.get_placeholder_sql` compatibility path for `get_placeholder` and remove
  dependencies on `SQLCompiler.quote_name_unless_alias()`.

```python
from django.db.models import JSONNull

Entry.objects.values_list("id", flat=True)
Entry.objects.filter(payload=JSONNull())
```

## Prepare mail code for the 7.0 boundary

Optional core-mail parameters become strictly keyword-only. Legacy `MIMEBase` attachments are
rejected, and `BadHeaderError`, `SafeMIMEText`, `SafeMIMEMultipart`,
`forbid_multi_line_headers()`, and `sanitize_address()` disappear. Move to the standard-library
email API and handle invalid headers as `ValueError`; see
[email-and-feeds.md](email-and-feeds.md) for the complete mail transition.

## Upgrade verification

1. Run system checks with all optional contrib applications installed as in production.
2. Run migration checks against real database versions, especially for backend extensions.
3. Exercise custom async middleware and authentication implementations through async tests.
4. Search extension code for removed method names and positional call forms.
5. Verify password-hasher ordering and rehash behavior after iteration-count changes.
6. Pin Django 6.0.8 or later when resolving `sqlparse` 0.5.5.
