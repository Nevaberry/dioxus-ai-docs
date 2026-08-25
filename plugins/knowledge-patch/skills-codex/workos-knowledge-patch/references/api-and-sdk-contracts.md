# API and SDK Contracts

Use this reference for public-client PKCE, the Python asynchronous client, Go
package organization, and the published API specification.

## Node.js public-client PKCE

Browser, mobile, and CLI clients can initialize `WorkOS` with only a client ID;
they do not need to embed an API key. `getAuthorizationUrlWithPKCE` returns the
authorization URL and verifier together. Store the verifier in secure
platform-specific storage that survives restarts and provide it when exchanging
the returned code.

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

Confidential clients may use the same methods after initializing WorkOS with an
API key. Their code exchange sends both the client secret and verifier.

## Python asynchronous client

`AsyncWorkOSClient` provides asyncio support for a subset of Python SDK
methods. Configure it with the same API key and client ID used by the
synchronous client.

```python
from workos import AsyncWorkOSClient

workos_client = AsyncWorkOSClient(
    api_key="sk_1234", client_id="client_1234"
)
```

## Go v6 packages

The Go SDK is divided into focused packages beneath
`github.com/workos/workos-go/v6/pkg`, including `sso`, `directorysync`,
`usermanagement`, `auditlogs`, `organizations`, and `webhooks`. Each package
offers package-level functions backed by a default client and a `Client` type
for custom configuration.

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

The API contract is an OpenAPI 3.1.1 YAML document at
`spec/open-api-spec.yaml` in the `workos/openapi-spec` repository. That
repository also provides `scripts/postman` tooling to generate Postman
collections from the specification.
