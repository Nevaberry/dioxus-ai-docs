# SDKs & Terraform Provider

## Go SDK (zitadel-go) v3

Current: v3.28.0. Module: `github.com/zitadel/zitadel-go/v3`. Requires Go 1.24+. Tracks Zitadel API v4.13.0. Only v3 supported — v2 and older are EOL.

### Client Creation & Authentication

```go
import (
	"github.com/zitadel/oidc/v3/pkg/oidc"
	"github.com/zitadel/zitadel-go/v3/pkg/client"
	"github.com/zitadel/zitadel-go/v3/pkg/zitadel"
)

// 1. JWT Profile (recommended for production)
authOption := client.DefaultServiceUserAuthentication(
	"path/to/jwt-key.json",
	oidc.ScopeOpenID,
	client.ScopeZitadelAPI(),  // adds urn:zitadel:iam:org:project:id:zitadel:aud
)

// 2. Client Credentials Grant — note: function is named PasswordAuthentication
authOption := client.PasswordAuthentication(
	"clientID", "clientSecret",
	oidc.ScopeOpenID,
	client.ScopeZitadelAPI(),
)

// 3. Personal Access Token
authOption := client.PAT("token-string")

// Create client (all methods use same pattern)
api, err := client.New(ctx, zitadel.New("https://my.zitadel.cloud"), client.WithAuth(authOption))
```

### Accessing API Services

```go
api.ManagementService().GetMyOrg(ctx, &management.GetMyOrgRequest{})
api.SessionService().CreateSession(ctx, &session.CreateSessionRequest{})
```
Import from `github.com/zitadel/zitadel-go/v3/pkg/client/zitadel/{service}`.

### AuthorizationChecker Interface

Extracted interface enables mocking authorization checks in tests without live Zitadel.

### Authentication Middleware

HTTP middleware for OIDC login flows (built on `zitadel/oidc` v3):

```go
// Register auth handler on route prefix (creates /auth/login, /auth/callback, /auth/logout)
router.Handle("/auth/", z.Authentication)

// Require authentication (redirect unauthenticated to login)
mw.RequireAuthentication()(handler)

// Check auth (optional, serve page either way)
mw.CheckAuthentication()(handler)

// Access auth context
authCtx := mw.Context(req.Context())
```

### API Token Introspection Middleware

For APIs with OAuth2 token introspection using JWT private key auth. API must be part of the token's audience.

Examples: `github.com/zitadel/zitadel-go/tree/main/example/app` (web), `example/api` (API).

## .NET SDK: Zitadel.Api

NuGet package `Zitadel.Api` (repo: `github.com/smartive/zitadel-net`):

```csharp
using Zitadel.Api;
using Zitadel.Credentials;

// PAT
var client = Clients.AuthService(new(apiUrl, ITokenProvider.Static(personalAccessToken)));
var result = await client.GetMyUserAsync(new());

// Service Account JWT Profile
var sa = ServiceAccount.LoadFromJsonString(keyJson);
client = Clients.AuthService(new(apiUrl, ITokenProvider.ServiceAccount(sa, apiUrl, "zitadel")));
// Third param adds urn:zitadel:iam:org:project:id:zitadel:aud scope
```

## New Language SDKs (v3.x Ecosystem)

| Language | Repository | Install |
|----------|-----------|---------|
| PHP | `zitadel/client-php` | `composer require zitadel/client:"^4.0.0-beta1"` |
| Java | `zitadel/client-java` | Maven: `io.github.zitadel:client:4.0.0-beta-1` |
| Ruby | `zitadel/client-ruby` | `gem install zitadel-client --pre` |
| Python | `zitadel/client-python` | `pip install --pre zitadel-client` |
| Node.js | `@zitadel/zitadel-node` | `npm install @zitadel/zitadel-node` (GitHub Packages only) |

**Node.js requires `.npmrc`** (not on public npm):
```ini
@zitadel:registry=https://npm.pkg.github.com
```

All SDKs target v2 ConnectRPC APIs. Versioning aligned with Zitadel core (v4.x client for Zitadel v4).

### Consistent Auth Factory Pattern

```python
# Python
from zitadel_client.models import (
    UserServiceAddHumanUserRequest,
    UserServiceSetHumanProfile,
    UserServiceSetHumanEmail,
)

zitadel = Zitadel.with_private_key(
    "https://instance.zitadel.cloud", "path/to/jwt-key.json"
)
# or: Zitadel.with_client_credentials(url, "client-id", "client-secret")
# or: Zitadel.with_access_token(url, "token")

response = zitadel.users.add_human_user(
    UserServiceAddHumanUserRequest(
        username="john.doe",
        profile=UserServiceSetHumanProfile(givenName="John", familyName="Doe"),
        email=UserServiceSetHumanEmail(email="john@doe.com"),
    )
)
```

```typescript
// Node.js
const client = await Zitadel.withPrivateKey(
  'https://instance.zitadel.cloud',
  'path/to/jwt-key.json',
);
const response = await client.users.addHumanUser({
  userServiceAddHumanUserRequest: {
    username: 'john.doe',
    profile: { givenName: 'John', familyName: 'Doe' },
    email: { email: 'john@doe.com' },
  },
});
```

```java
// Java
Zitadel zitadel = Zitadel.withPrivateKey("https://instance.zitadel.cloud", "path/to/jwt-key.json");
UserServiceAddHumanUserResponse response = zitadel.users.userServiceAddHumanUser(
    new UserServiceAddHumanUserRequest()
        .username("john.doe")
        .profile(new UserServiceSetHumanProfile().givenName("John").familyName("Doe"))
        .email(new UserServiceSetHumanEmail().email("john@doe.com"))
);
```

## Recommended OIDC Libraries by Framework

| Framework | Library |
|-----------|---------|
| Angular | `@edgeflare/ngx-oidc` |
| Astro | `@auth/core` + `auth-astro` |
| Django / FastAPI / Flask | Authlib |
| Express.js | `@auth/express` |
| Fastify | `@auth/core` |
| Hono | Auth.js |
| Laravel | Laravel Socialite |
| NestJS | `@auth/core` |
| Next.js | `next-auth` |
| Nuxt.js | `next-auth` |
| Qwik | `@auth/core` |
| SolidStart | `@auth/solid-start` |
| SvelteKit | `@auth/sveltekit` |
| Spring Boot | Spring Security (native OIDC) |
| Symfony | Symfony Security |

## Generating gRPC Clients

Use [buf](https://buf.build) with Zitadel's proto definitions:

```yaml
# buf.gen.yaml
version: v1
plugins:
  - plugin: buf.build/grpc/ruby
    out: gen
  - plugin: buf.build/protocolbuffers/ruby
    out: gen
```

```bash
buf generate https://github.com/zitadel/zitadel#format=git,tag=v4.0.0
```

## OIDC Library (github.com/zitadel/oidc)

Current: v3.45.5 (March 2026). Import: `github.com/zitadel/oidc/v3`. Requires Go 1.25+.

**OTel on by default.** Disable with build tag:
```bash
go build -tags no_otel ./...
```

Feature support: Token Exchange (RFC 8693), Device Authorization (RFC 8628), Back-Channel Logout (OP only), JWT Profile (RFC 7523), Client Credentials — both RP and OP.

Example OP server:
```bash
PORT=9998 REDIRECT_URI="http://localhost:9999/auth/callback" USERS_FILE=./users.json \
  go run github.com/zitadel/oidc/v3/example/server
```

Dynamic issuer mode: `go run github.com/zitadel/oidc/v3/example/server/dynamic`

## Terraform Provider

Current: **v2.11.0** (March 2026). Registry: `zitadel/zitadel`. Apache-2.0. Uses `zitadel-go v3` internally.

### Plugin Framework Migration
Upgraded from SDKv2 to Terraform Plugin Framework 1.x (Feb 2026). Watch for attribute type changes when upgrading.

### New Resources (v2.10–v2.11)
- `zitadel_instance_secret_generator` — Instance-level secret generator config (v2.11.0)
- `zitadel_default_invite_user_message_text` — Default invite email text (v2.10.0)
- `zitadel_action_target` now includes `payload_type` attribute

### Configuration
```hcl
terraform {
  required_providers {
    zitadel = {
      source  = "zitadel/zitadel"
      version = "~> 2.11"
    }
  }
}

provider "zitadel" {
  domain = "your-instance.zitadel.cloud"
  port   = "443"
  token  = var.zitadel_token
}
```

## Guest Account Architecture (Token Exchange + Impersonation)

Shadow Account pattern for anonymous/guest users:

1. **Silent provisioning**: Backend creates temp user, tags with metadata (e.g., `GUEST_26_02_27`)
2. **Token exchange**: Backend trades service account for impersonation token (stored in `httpOnly` cookie)
3. **Upgrade**: On registration, update guest profile, remove `GUEST` tag
4. **Cart merging**: On `sub` mismatch, merge data, `DeleteUser` orphaned guest

Requires PKCE, Token Exchange, and Impersonation roles. Reference: `github.com/zitadel/zitadel-guest-accounts`

## Example App Ecosystem

20+ quickstart repos: React, Angular, Vue, Next.js, Nuxt, Astro, SvelteKit, SolidStart, Qwik, Hono, Express, Fastify, NestJS, Django, FastAPI, Flask, Laravel, Spring Boot, Symfony, ASP.NET Core, Go, Flutter.

Naming: `github.com/zitadel/example-auth-{framework}` (exceptions: `zitadel-go`, `zitadel_flutter`, `zitadel-nextjs-b2b`).
