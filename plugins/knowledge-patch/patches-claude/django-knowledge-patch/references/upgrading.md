# Upgrading and Compatibility

Load this reference before changing Django, Python, database, or optional
dependency versions, and before maintaining compatibility shims.

## Select a supported target

### Release state (`release-and-upgrade-catalog`)

The release catalog snapshot dated 2026-07-14 identifies 6.0 as the newest
finalized series and contains patch notes through 6.0.8. It lists 6.1 and 6.2 as
under development, so do not infer stable-release status from the presence of
development documentation. Later 6.1 guidance in this stream describes its target
support policy; confirm current release status before adopting it.

### Runtime and database floors

| Series | Compatibility requirements |
| --- | --- |
| 5.1 (`5.1`) | Drops MariaDB 10.4, PostgreSQL 12, PostGIS 2.5, PROJ below 6, and GDAL 2.4; requires SQLite 3.31.0+ and `asgiref` 3.8.1+. |
| 5.2 (`5.2`) | LTS; as of 5.2.8 supports Python 3.10–3.14. Requires PostgreSQL 14+, `gettext` 0.19+, and `oracledb` 2.3+; drops PostGIS 3.0 and GDAL 3.0. |
| 6.0 (`6.0`) | Supports Python 3.12–3.14 and MariaDB 10.6+; requires `asgiref` 3.9.1+ and removes `cx_Oracle` support. |
| 6.1 (`6.1`) | Targets Python 3.12–3.14, PostgreSQL 15+, MySQL 8.4+, MariaDB 10.11+, and SQLite 3.37+. Its stated support horizon is April 2027 mainstream and December 2027 extended. |

For Python 3.12 on 6.0, the documented optional-dependency floors are
`aiosmtpd` 1.4.5, `argon2-cffi` 23.1.0, `bcrypt` 4.1.1, `docutils` 0.22,
`geoip2` 4.8.0, Pillow 10.1.0, `mysqlclient` 2.2.1, NumPy 1.26.0, PyYAML
6.0.2, `psycopg` 3.1.12, `psycopg2` 2.9.9, `redis-py` 5.1.0, Selenium
4.23.0, `sqlparse` 0.5.0, and `tblib` 3.0.0. (`6.0`)

### Patch-level compatibility

- Django 6.0.8 fixes a 6.0 regression in which `bulk_create()` could crash on
  databases returning bulk-insert rows when an assigned related object providing
  the primary key was saved only after assignment. (`6.0.8`)
- Django 6.0.8 adds compatibility with `sqlparse` 0.5.5; use this patch level or
  newer when resolving that dependency version. (`6.0.8`)
- Django 5.2.17 adds security-oriented GIS input and collection limits plus
  language-code and admin URL validation changes. Review
  [gis.md](gis.md) and [templates-forms-admin.md](templates-forms-admin.md) when
  upgrading within the 5.2 line. (`5.2.17`)

## Update password behavior

- `AdminUserCreationForm` is available and both it and
  `AdminPasswordChangeForm` can disable password authentication by saving an
  unusable password. (`5.1`)
- The PBKDF2 default increases from 720,000 to 870,000 iterations and
  `ScryptPasswordHasher.parallelism` from 1 to 5 in 5.1. (`5.1`)
- PBKDF2 increases to 1,000,000 iterations in 5.2. (`5.2`)
- PBKDF2 increases to 1,200,000 iterations in 6.0, and
  `AdminSite.password_change_form` can select the admin password-change form.
  (`6.0`)

## Remove APIs already gone

### Model, auth, test, storage, and PostgreSQL removals (`5.1`)

Replace or delete uses of:

- `BaseUserManager.make_random_password()`, `Meta.index_together`, and the
  `length_is` template filter.
- The legacy SHA1 and unsalted password hashers.
- `CICharField`, `CIEmailField`, `CITextField`, and `CIText` from
  `django.contrib.postgres`. Historical migrations may still reference the fields.
- `assertFormsetError()` and `assertQuerysetEqual()`.
- Encoded JSON string literals supplied to `JSONField`.
- Positional arguments to `Signer` and `TimestampSigner`.
- `DEFAULT_FILE_STORAGE`, `STATICFILES_STORAGE`, and `get_storage_class()`;
  configure `STORAGES` and use aliases.

### Customization removals (`6.0`)

- `BaseConstraint` no longer accepts positional arguments.
- `ModelAdmin.lookup_allowed()` overrides must accept `request`.
- `format_html()` must receive arguments or keyword arguments.
- `CheckConstraint` uses `condition=`, not the removed `check=` keyword.
- `DjangoDivFormRenderer`, `Jinja2DivFormRenderer`, `ChoicesMeta`, and
  `django.utils.itercompat` are removed.
- `FileSystemStorage.OS_OPEN_FLAGS` and `FieldCacheMixin.get_cache_name()` are
  removed.

### Relation and prefetch extension removals (`6.0`)

ORM joins no longer fall back to `get_joining_columns()`, and the related
`ForeignObject` and `ForeignObjectRel` joining-column methods are removed.
`Prefetch.get_current_queryset()` and the singular `get_prefetch_queryset()`
extension API are also removed; prefetch machinery does not fall back to the
singular hook.

## Resolve active deprecations

### Application and extension calls (`5.1`)

- Pass `Model.save()` and `Model.asave()` arguments by keyword.
- Do not replace an existing URL converter with `register_converter()`.
- Replace admin `log_deletion()` and `log_action()` with
  `log_deletions()` and `log_actions()`.
- Replace `GeoIP2.coords()` with `lon_lat()`, construct `GeoIP2` instead of
  calling `open()`, and replace assignment to `OGRGeometry.coord_dim` with
  `set_3d()`.

### Calls that cross the 6.1 boundary (`5.2`, `deprecation-roadmap`)

Before upgrading to 6.1:

- Replace `find(..., all=...)` with `find_all`.
- Pass a non-`None` user explicitly to `login()` and `alogin()`.
- Replace `ordering=` with `order_by=` for PostgreSQL `ArrayAgg`,
  `JSONBAgg`, and `StringAgg`.
- Async-capable `RemoteUserMiddleware` subclasses must implement
  `aprocess_request()` as well as `process_request()`.

The corresponding 5.2 compatibility paths are removed at the 6.1 boundary.

### Calls that cross the 7.0 boundary (`6.0`, `deprecation-roadmap`)

Before upgrading to 7.0:

- Stop passing `serialize` to `BaseDatabaseCreation.create_test_db()`; use
  `serialize_db_to_string()`.
- Move from PostgreSQL-specific `StringAgg` to
  `django.db.models.StringAgg` and from `OrderableAggMixin` to aggregate
  classes opting into `allow_order_by`.
- Replace tuple-form `ADMINS` and `MANAGERS` with address strings.
- Keep paginator `orphans` below `per_page`.
- Remove `%` from column aliases and annotation names; 7.0 raises
  `ValueError`.
- Pass optional mail parameters by keyword, replace legacy `MIMEBase`
  attachments, and remove dependencies on `BadHeaderError`, `SafeMIMEText`,
  `SafeMIMEMultipart`, `forbid_multi_line_headers()`, and
  `sanitize_address()`.
- Give `values_list(flat=True)` an explicit field name.
- Use `JSONNull()` to filter a top-level JSON value equal to JSON `null`.
  Filtering a top-level `JSONField` with Python `None` becomes SQL `IS NULL`.
- Replace the `Field.get_placeholder_sql` compatibility path for
  `get_placeholder` and remove uses of
  `SQLCompiler.quote_name_unless_alias()`.

```python
from django.db.models import JSONNull

Entry.objects.values_list("id", flat=True)
Entry.objects.filter(payload=JSONNull())
```

## Check behavior changes that may not raise immediately

- Saving a `FileField` without a name raises `FieldError`. An `ImageField`
  save no longer forces a dimension refresh, so resizing storage backends can leave
  `width_field` and `height_field` stale. (`5.1`)
- Admin bulk deletion records `LogEntry` objects with `bulk_create()`, so those
  log entries no longer emit `pre_save` or `post_save`. (`5.1`)
- Setting names containing `AUTH` are treated as sensitive in exception reports.
  (`5.2`)
- New projects omit the `debug()` context processor. `SafeString.__add__()`
  returns `NotImplemented` for a non-string right operand, and single-argument
  built-in aggregates raise `TypeError` for the wrong arity. (`5.2`)
