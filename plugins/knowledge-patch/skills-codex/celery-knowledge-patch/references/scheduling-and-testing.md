# Scheduling and Testing

## Named months in crontab schedules

`celery.schedules.crontab` accepts month names (`5.5.0`):

```python
from celery.schedules import crontab

january_mornings = crontab(month_of_year="jan", hour=9, minute=0)
```

This permits readable month configuration without first translating it to a
number.

## Parsing five-field crontab expressions

Use `crontab.from_string()` to parse a standard five-field crontab expression
(`5.5.0`):

```python
from celery.schedules import crontab

daily_mornings = crontab.from_string("0 9 * * *")
```

Validate user-controlled strings at the configuration boundary so malformed
schedules fail before the scheduler starts.

## Custom test-worker hostnames

Workers started through `celery.contrib.pytest` or
`celery.contrib.testing.worker` accept a custom hostname (`5.5.0`). With the
pytest fixture integration:

```python
import pytest

@pytest.fixture
def celery_worker_parameters():
    return {"hostname": "test-worker@localhost"}
```

Use distinct hostnames when assertions, routing, events, or logs need to
identify a particular test worker.

