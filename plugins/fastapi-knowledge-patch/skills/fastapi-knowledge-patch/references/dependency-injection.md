# Dependency Injection Updates (FastAPI 0.112-0.135.3)

## Dependency Scopes (0.121.0)

New `scope="request"` for yield dependencies -- exit code runs **before** the response is sent (useful when you need cleanup before streaming begins):

```python
from typing import Annotated
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db: Annotated[Session, Depends(get_db, scope="request")]):
    ...
```

### Default Behavior (No Scope)

Without `scope="request"` (default), yield dependency exit code runs **after** the response is fully sent (changed in 0.118.0). This is the correct behavior for `StreamingResponse` -- the dependency stays alive during streaming.

## functools.partial() and functools.wraps() Support (0.123.5)

Dependencies now fully support `functools.partial()` and `functools.wraps()`:

```python
from functools import partial
from fastapi import Depends

def get_db(engine: Engine, read_only: bool = False):
    session = Session(engine, read_only=read_only)
    try:
        yield session
    finally:
        session.close()

get_prod_db = partial(get_db, engine=prod_engine)
get_readonly_db = partial(get_db, engine=prod_engine, read_only=True)

@app.get("/items")
async def read_items(db=Depends(get_prod_db)):
    ...

@app.get("/reports")
async def read_reports(db=Depends(get_readonly_db)):
    ...
```

Wrapped functions with `functools.wraps()` also work correctly with forward references in type annotations.

## Response as Dependency Annotation (0.128.2)

`Response` can be used directly as a dependency annotation for setting headers/cookies:

```python
from fastapi import Response

async def set_custom_header(response: Response):
    response.headers["X-Custom"] = "value"

@app.get("/items", dependencies=[Depends(set_custom_header)])
async def read_items():
    ...
```

## PEP 695 TypeAliasType Support (0.128.2)

Python 3.12+ `type` statement syntax works in path operation type annotations:

```python
# Python 3.12+ syntax
type ItemList = list[Item]

@app.get("/items")
async def read_items() -> ItemList:
    ...
```
