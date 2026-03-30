# Python SDK

## Package Name and Client Initialization

The official Python backend SDK is `clerk-backend-api` (not `clerk-python` or `clerk-sdk-python`):

```python
from clerk_backend_api import Clerk

with Clerk(bearer_auth="sk_live_xxx") as clerk:
    user = clerk.users.get(user_id="user_123")
```

Uses context manager pattern for resource management. All resources are accessed as attributes: `clerk.users`, `clerk.organizations`, `clerk.billing`, `clerk.machines`, `clerk.m2m`, etc.

## Async Methods Use `_async` Suffix

Unlike most Python async SDKs, Clerk uses an `_async` suffix on method names (not just `await`):

```python
import asyncio
from clerk_backend_api import Clerk

async def main():
    async with Clerk(bearer_auth="sk_live_xxx") as clerk:
        # NOT: await clerk.users.get(...)
        # YES: await clerk.users.get_async(...)
        user = await clerk.users.get_async(user_id="user_123")
        orgs = await clerk.organizations.list_async()

asyncio.run(main())
```

## Request Authentication (Session + Machine Tokens)

Verify requests from Clerk frontends using `authenticate_request`:

```python
from clerk_backend_api import Clerk
from clerk_backend_api.security import authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions

sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

# Session token verification
request_state = sdk.authenticate_request(
    request,  # httpx.Request object
    AuthenticateRequestOptions(authorized_parties=["https://example.com"]),
)
request_state.is_signed_in  # bool
request_state.payload  # token claims (if authenticated)
request_state.reason  # failure reason (if not)

# Machine token verification (API keys, OAuth tokens, M2M)
request_state = sdk.authenticate_request(
    request,
    AuthenticateRequestOptions(
        accepts_token=["oauth_token"]  # 'api_key' | 'oauth_token' | 'm2m_token'
    ),
)
```
