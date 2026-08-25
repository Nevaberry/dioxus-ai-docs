# Clients, Authentication, and Operations

## Versioned preview SDKs and environments

The typed 2026-04 clients are prereleases.

For TypeScript, install the prerelease package and import the versioned client:

```bash
npm install @polar-sh/sdk@next
```

```ts
import { createPolar } from "@polar-sh/sdk/2026-04";

const polar = createPolar({
  accessToken: process.env.POLAR_ACCESS_TOKEN!,
  environment: "sandbox",
});
```

For Python, install prereleases and import the versioned client:

```bash
pip install --pre polar-sdk
```

```python
from polar.v2026_04 import Polar
```

Both clients target production unless `environment: "sandbox"` in TypeScript
or `environment="sandbox"` in Python is set. Sandbox data and credentials are
isolated from production.

## Core API and Customer Portal authentication

Backend Core API calls use an Organization Access Token at
`https://api.polar.sh/v1` or the sandbox base URL.

Customer-facing code must create a Customer Access Token through
`/v1/customer-sessions/` and use the restricted `/v1/customer-portal/`
surface. The token is scoped to the customer and cannot perform
organization-level operations such as creating products or issuing refunds.

## Pagination and rate limits

List endpoints use one-based `page` and `limit`. They default to 1 and 10,
respectively, and the maximum `limit` is 100. Responses include
`pagination.total_count` and `pagination.max_page`.

Production permits 500 requests per minute and sandbox permits 100 requests
per minute per organization, customer, or OAuth2 client.

Unauthenticated license validation, activation, and deactivation permit 3
requests per second. A 429 response includes `Retry-After`.

## Webhook delivery behavior

Webhook payloads include a Standard Webhooks timestamp.

By default, an endpoint is automatically disabled after 10 consecutive
failures. Organization members are notified. After fixing the receiver, the
endpoint must be manually re-enabled.

## OAuth2 authorization

An OAuth2 authorization request without a scope receives the client's
configured default scope. Trusted first-party clients save grants without
showing an authorization prompt.

## Organization SSO

Scale organizations can configure and enforce OpenID Connect SSO. Anyone
authenticated by that provider becomes an organization member without an
invitation.

## Ready-made integrations

Polar supplies a TypeScript Better Auth billing plugin.

The Zapier integration currently offers webhook-backed event triggers but no
actions that change Polar resources.
