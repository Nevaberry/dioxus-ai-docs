# Go SDK v2

The Go SDK v2 is a complete rewrite. Import path changed from `github.com/clerkinc/clerk-sdk-go` (v1) to `github.com/clerk/clerk-sdk-go/v2`.

## Package Structure

Each API resource has its own sub-package:

```go
import (
	"github.com/clerk/clerk-sdk-go/v2"
	"github.com/clerk/clerk-sdk-go/v2/domain"
	clerkhttp "github.com/clerk/clerk-sdk-go/v2/http"
	"github.com/clerk/clerk-sdk-go/v2/jwks"
	"github.com/clerk/clerk-sdk-go/v2/jwt"
	"github.com/clerk/clerk-sdk-go/v2/organization"
	"github.com/clerk/clerk-sdk-go/v2/user"
)
```

## Global Key vs Client-based Usage

For single-key apps, set the key globally. For multi-key scenarios, use per-resource clients:

```go
// Global (most common)
clerk.SetKey("sk_live_XXX")
org, err := organization.Create(ctx, &organization.CreateParams{
	Name: clerk.String("Acme Inc"),
})

// Client-based (multi-key)
config := &clerk.ClientConfig{}
config.Key = "sk_live_XXX"
client := organization.NewClient(config)
org, err := client.Create(ctx, &organization.CreateParams{
	Name: clerk.String("Acme Inc"),
})
```

## Pointer Helpers for Params

All param struct fields are pointers. Use helpers: `clerk.String()`, `clerk.Bool()`, `clerk.Int64()`, `clerk.JSONRawMessage()`.

```go
domain.Create(ctx, &domain.CreateParams{
	Name:        clerk.String("clerk.com"),
	IsSatellite: clerk.Bool(true),
})
```

## List Operations

List operations return a struct with `TotalCount` and a typed slice:

```go
params := &user.ListParams{}
params.Limit = clerk.Int64(10)
list, err := user.List(ctx, params)
// list.TotalCount, list.Users
```

## HTTP Middleware

v2 drops cookie-based auth entirely. Two middleware functions authenticate via `Authorization: Bearer <token>` header:

```go
clerk.SetKey("sk_live_XXX")
mux := http.NewServeMux()

// WithHeaderAuthorization — sets claims in context, does NOT reject unauthenticated
mux.Handle("/maybe-auth", clerkhttp.WithHeaderAuthorization()(handler))

// RequireHeaderAuthorization — responds 403 if no valid session
mux.Handle("/protected", clerkhttp.RequireHeaderAuthorization()(handler))

func handler(w http.ResponseWriter, r *http.Request) {
    claims, ok := clerk.SessionClaimsFromContext(r.Context())
    if ok {
        fmt.Fprintf(w, "user: %s", claims.Subject)
    }
}
```

### Middleware Options (Functional Arguments)

- `clerkhttp.AuthorizedPartyMatches("https://example.com")` — allowed azp values
- `clerkhttp.Leeway(5 * time.Second)` — clock skew tolerance
- `clerkhttp.JSONWebKey(key)` — provide JWK directly
- `clerkhttp.Satellite("https://satellite.example.com")` — satellite domain
- `clerkhttp.ProxyURL("https://proxy.example.com")` — proxy URL
- `clerkhttp.CustomClaimsConstructor(func(ctx context.Context) any { return &MyClaims{} })` — custom JWT claims
- `clerkhttp.JWKSClient(jwksClient)` — use specific JWKS client (for multi-key)

## JWT Verification (Manual)

`jwt.Verify` requires an explicit JWK (no auto-caching like v1):

```go
token := "the-clerk-session-jwt"
decoded, err := jwt.Decode(ctx, &jwt.DecodeParams{Token: token})

jwk, err := jwt.GetJSONWebKey(ctx, &jwt.GetJSONWebKeyParams{
	KeyID: decoded.KeyID,
})

claims, err := jwt.Verify(ctx, &jwt.VerifyParams{
	Token: token,
	JWK:   jwk,
})
```

## Error Handling

`clerk.APIErrorResponse` replaces v1's `clerk.ErrorResponse`, adding `TraceID` and raw response access:

```go
_, err := user.List(ctx, &user.ListParams{})
if apiErr, ok := err.(*clerk.APIErrorResponse); ok {
	apiErr.TraceID
	apiErr.Error()
	apiErr.Response.RawJSON
}
```

## Session Reverification (v2.3.0+)

```go
claims, _ := clerk.SessionClaimsFromContext(r.Context())
if claims.NeedsReverification(clerk.SessionReverificationStrict) {
	// prompt user to re-authenticate
}

// Or use middleware
mux.Handle("/sensitive", clerkhttp.RequireHeaderAuthorization(
	clerkhttp.NeedsSessionReverification(),
)(handler))
```

## Testing Patterns

```go
// Option 1: custom HTTP transport
clerk.SetBackend(clerk.NewBackend(&clerk.BackendConfig{
    HTTPClient: &http.Client{Transport: &mockRoundTripper{}},
}))

// Option 2: httptest server
ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    // return mock response
}))
clerk.SetBackend(clerk.NewBackend(&clerk.BackendConfig{
    HTTPClient: ts.Client(),
    URL:        &ts.URL,
}))

// Option 3: implement Backend interface
type customBackend struct{}
func (b *customBackend) Call(ctx context.Context, r *clerk.APIRequest, reader clerk.ResponseReader) error {
    reader.Read(&clerk.APIResponse{})
    return nil
}
clerk.SetBackend(&customBackend{})
```

## v2.3.0 New APIs

- **OAuth Applications**: `oauthapplication` package for managing OAuth apps
- **Waitlist entries**: `waitlistentry.List` and `waitlistentry.Create`
- **Organization with member count**: `organization.GetWithParams`
- **Bulk invitations**: `invitation.BulkCreate` (v2.2.0)
- **Sign-in tokens**: `signintoken` package (v2.1.0)
