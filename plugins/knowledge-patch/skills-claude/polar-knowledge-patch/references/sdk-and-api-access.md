# SDK and API access

## Typed 2026-04 preview clients

The typed 2026-04 TypeScript and Python clients are prereleases.

For TypeScript:

```sh
npm install @polar-sh/sdk@next
```

```ts
import { createPolar } from "@polar-sh/sdk/2026-04";

const polar = createPolar({
  accessToken: process.env.POLAR_ACCESS_TOKEN!,
  environment: "sandbox",
});
```

For Python:

```sh
pip install --pre polar-sdk
```

```python
from polar.v2026_04 import Polar
```

Both clients use production unless configured with `environment: "sandbox"`
or `environment="sandbox"`. Sandbox data and credentials are isolated from
production.

## Core API authentication

Authenticate backend Core API calls with an Organization Access Token. Use
`https://api.polar.sh/v1` for production or the sandbox base URL for sandbox
requests.

## Customer Portal authentication

Customer-facing code must create a Customer Access Token through
`/v1/customer-sessions/` and use the restricted `/v1/customer-portal/` API.
The token is scoped to its customer and cannot perform organization-level
operations, including creating products or issuing refunds.

## Pagination

List endpoints use one-based `page` and `limit` parameters. Both have defaults:
`page` defaults to 1 and `limit` defaults to 10. The maximum `limit` is 100.

List responses expose:

- `pagination.total_count`
- `pagination.max_page`

## Rate limits

Production permits 500 requests per minute and sandbox permits 100 requests
per minute, per organization, customer, or OAuth2 client.

Unauthenticated license validation, activation, and deactivation permit three
requests per second. A 429 response includes `Retry-After`.
