# Ecosystem Changes (SQLModel, Uvicorn, FastAPI CLI)

## SQLModel

### Version Compatibility

| Version | Change |
|---------|--------|
| 0.0.30 | Dropped Python 3.8 |
| 0.0.31 | Dropped Pydantic v1 support |
| 0.0.32 | Fixed `Annotated` field support for Pydantic 2.12+ |
| 0.0.35 | Dropped Python 3.9 |
| 0.0.36 | Dropped `sqlmodel-slim` (mirrors FastAPI dropping `fastapi-slim`) |

### session.exec() Overloads (0.0.25)

`session.exec()` now has proper overloads for INSERT, UPDATE, DELETE statements (not just SELECT):

```python
from sqlmodel import insert, update, delete, Session

with Session(engine) as session:
    session.exec(insert(Hero).values(name="Deadpond"))
    session.exec(update(Hero).where(Hero.name == "Deadpond").values(name="Tarantula"))
    session.exec(delete(Hero).where(Hero.name == "Tarantula"))
    session.commit()
```

## Uvicorn

### WatchGod Removed (0.33.0)

`WatchGod` support for `--reload` is removed. Only `watchfiles` is supported. Projects with `watchgod` in dev dependencies must switch to `watchfiles`.

### New CLI Options

- **`--limit-max-requests-jitter`** (0.41.0): Adds jitter to worker restart timing, preventing thundering herd when all workers hit their request limit simultaneously
- **`--timeout-worker-healthcheck`** (0.37.0): Configures timeout for worker health checks

## FastAPI CLI

### fastapi deploy / FastAPI Cloud CLI (0.116.0)

`fastapi[standard]` now includes `fastapi-cloud-cli`. Running `fastapi deploy` deploys to FastAPI Cloud.

To get standard extras without the cloud CLI:

```bash
pip install "fastapi[standard-no-fastapi-cloud-cli]"
```

### external_docs on FastAPI (0.117.0)

New `external_docs` parameter on `FastAPI()` constructor for OpenAPI spec-level external documentation:

```python
app = FastAPI(
    external_docs={"description": "Full API docs", "url": "https://docs.example.com"}
)
```
