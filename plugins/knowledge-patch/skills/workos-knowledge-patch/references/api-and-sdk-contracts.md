# API and SDK Contracts

## Node.js public-client PKCE

Run the Node SDK without an API key in browser, mobile, and CLI clients by
constructing `WorkOS` with only a client ID.
`getAuthorizationUrlWithPKCE` returns both the authorization URL and verifier.
Persist the verifier in secure platform storage so it survives application
restarts, then supply it during the code exchange:

```ts
import { WorkOS } from '@workos-inc/node';

const workos = new WorkOS({ clientId: 'client_...' });
const { url, codeVerifier } =
  await workos.userManagement.getAuthorizationUrlWithPKCE({
    provider: 'authkit',
    redirectUri: 'myapp://callback',
    clientId: 'client_...',
  });

const tokens = await workos.userManagement.authenticateWithCode({
  code: authorizationCode,
  codeVerifier,
  clientId: 'client_...',
});
```

Confidential clients can use the same PKCE methods after constructing `WorkOS`
with an API key. The code exchange then sends both the client secret and code
verifier.

## Python async client

Use `AsyncWorkOSClient` for the subset of Python SDK methods that supports
`asyncio`. Configure it with the same API key and client ID as the synchronous
client:

```python
from workos import AsyncWorkOSClient

workos_client = AsyncWorkOSClient(
    api_key="sk_1234",
    client_id="client_1234",
)
```

Do not assume every synchronous SDK method has an asynchronous counterpart.

## Go v6 package layout

Import focused packages below `github.com/workos/workos-go/v6/pkg`, including:

- `sso`;
- `directorysync`;
- `usermanagement`;
- `auditlogs`;
- `organizations`; and
- `webhooks`.

Each package exposes package-level functions backed by a default client and a
`Client` type for custom configuration.

```go
package main

import (
    "github.com/workos/workos-go/v6/pkg/directorysync"
    "github.com/workos/workos-go/v6/pkg/sso"
)

func main() {
    sso.Configure("<WORKOS_API_KEY>", "<CLIENT_ID>")
    directorysync.SetAPIKey("<WORKOS_API_KEY>")
}
```

## Published OpenAPI contract

Use the OpenAPI 3.1.1 YAML contract at `spec/open-api-spec.yaml` in the
`workos/openapi-spec` repository when generating clients or validating raw API
requests. The repository's `scripts/postman` tooling generates Postman
collections from that specification.
