# Migration Guide

## Version Requirements (6.0)

- **Python 3.10 and 3.11 dropped** — minimum is Python 3.12
- **MariaDB 10.5 dropped** — minimum is MariaDB 10.6

## Breaking Changes

### `as_sql()` Must Return Tuple Params (6.0)

Custom SQL expressions using `as_sql()` must now return params as `tuple`, not `list`.

### `Field.pre_save()` Idempotency (6.0)

`Field.pre_save()` may be called multiple times — implementations must be idempotent.

### `StringAgg` Delimiter Requires `Value()` (6.0)

```python
# Old (breaks in 6.0)
StringAgg("name", delimiter=", ")

# New
from django.db.models import Value
StringAgg("name", delimiter=Value(", "))
```

### MySQL Default Charset Changed (5.2)

MySQL connections now default to `utf8mb4` charset (was `utf8`/`utf8mb3`).

### `DEFAULT_AUTO_FIELD` Default Changed (6.0)

Framework default changed from `AutoField` (32-bit) to `BigAutoField` (64-bit). Projects that already set `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"` explicitly can remove it.

## Key Deprecations (6.0)

### Email API

- `django.core.mail` functions: optional params must be keyword arguments
- `EmailMessage`/`EmailMultiAlternatives`: all args after `subject, body, from_email, to` must be keyword-only
- `SafeMIMEText`, `SafeMIMEMultipart`, `BadHeaderError` deprecated — use modern Python email API
- Passing `MIMEBase` to `EmailMessage.attach()` deprecated — use `MIMEPart`

### PostgreSQL-specific `StringAgg`

Deprecated — use `django.db.models.StringAgg` (cross-database).

### URL Handling

`urlize`/`urlizetrunc` will default to HTTPS in Django 7.0 (set `URLIZE_ASSUME_HTTPS = True` to opt in now).

### `ADMINS`/`MANAGERS` Format

`(name, address)` tuples deprecated — use plain email strings.

## Shell Auto-imports (6.0)

`manage.py shell` now auto-imports: `settings`, `connection`, `models`, `functions`, `timezone`.

## `startproject`/`startapp` (6.0)

Now creates target directory if it doesn't exist.
