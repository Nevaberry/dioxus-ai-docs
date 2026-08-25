# API and SDK Contracts

## Node public-client PKCE

Browser, mobile, and CLI applications can construct `WorkOS` with only a client
ID. `getAuthorizationUrlWithPKCE` returns the authorization URL and verifier.
Keep the verifier in secure platform storage so it survives process restarts,
then submit it to `authenticateWithCode` after the redirect.

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

Confidential clients may use the same PKCE methods with an API key. The code
exchange then sends both the client secret and code verifier.

## Python asynchronous client

`AsyncWorkOSClient` supplies asyncio support for a subset of SDK methods. It
uses the same API key and client ID as the synchronous client.

```python
from workos import AsyncWorkOSClient

workos_client = AsyncWorkOSClient(
    api_key="sk_1234", client_id="client_1234"
)
```

## Go v6 packages

The Go SDK uses focused packages under `github.com/workos/workos-go/v6/pkg`,
including `sso`, `directorysync`, `usermanagement`, `auditlogs`,
`organizations`, and `webhooks`. Each offers package-level functions backed by
a default client and a `Client` type for custom configuration.

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

## OpenAPI contract

The published API contract is an OpenAPI 3.1.1 YAML document at
`spec/open-api-spec.yaml` in the `workos/openapi-spec` repository. Its
`scripts/postman` tooling generates Postman collections from the specification.
