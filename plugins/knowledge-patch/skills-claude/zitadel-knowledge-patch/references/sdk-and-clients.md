# SDKs and clients

## Choose an incubating management client

Official server-to-server clients for V2 Management APIs are available for Java, Node.js, PHP, Python, and Ruby. They are not end-user login SDKs, all remain incubating with possible breaking changes, and their major versions track the core server major. Each supports private-key JWT, client credentials, and personal access tokens.

```text
Java 11+:    io.github.zitadel:client:4.0.0-beta-1
Node 20+:    npm install @zitadel/zitadel-node
PHP:         composer require zitadel/client:"^4.0.0-beta1"
Python 3.9+: pip install --pre zitadel-client
Ruby 3.1+:   gem install zitadel-client --pre
```

Java, Node.js, and PHP use the factories `withPrivateKey`, `withClientCredentials`, and `withAccessToken`; Python and Ruby expose equivalent snake-case factories.

## Use the Go SDK v3 contract

Install `github.com/zitadel/zitadel-go/v3`. Only v3 is supported; v2.2.8 and v0.3.5 are the final older-module releases. The SDK support matrix lists Go 1.24 and 1.25. It combines high-level OIDC web login, refresh, userinfo, role, and logout helpers with introspection-based API protection and generated resource-management clients. A Session API helper for custom Login UIs remains a stated future goal.

```go
auth := client.DefaultServiceUserAuthentication(
    keyPath, oidc.ScopeOpenID, client.ScopeZitadelAPI(),
)
api, err := client.New(ctx, zitadel.New(domain), client.WithAuth(auth))
```

For other management authentication modes, use `client.PasswordAuthentication(clientID, clientSecret, scopes...)` or `client.PAT(token)`.

## Use the Go OIDC library by role

`github.com/zitadel/oidc/v3` implements relying-party, resource-server, and OpenID-provider components. Client and provider sides support code flow, client credentials, refresh tokens, discovery, JWT profile, PKCE, token exchange, and device authorization. The client side omits implicit, hybrid, mTLS, and back-channel logout; the provider adds implicit and back-channel logout but still omits hybrid and mTLS.

OpenTelemetry instrumentation is enabled by default and can be compiled out with the `no_otel` build tag. The library's support matrix lists Go 1.25 and 1.26, which differs from the Go SDK matrix.

```sh
go build -tags no_otel ./...
```

## Generate a missing management client

For a language without a maintained client, generate gRPC stubs from a pinned repository tag with Buf. Configure both the RPC and message plugins required by the target language. For Ruby:

```yaml
version: v1
plugins:
  - plugin: buf.build/grpc/ruby
    out: gen
  - plugin: buf.build/protocolbuffers/ruby
    out: gen
```

```sh
buf generate https://github.com/zitadel/zitadel#format=git,tag=v2.23.1
```

Replace the example tag with the server version the generated client must target.

## Prefer standards-based PKCE integrations

Framework references use a ZITADEL Web application with authorization code plus PKCE and standards-based libraries rather than a product-specific login SDK. Current pairings include Angular with `@edgeflare/ngx-oidc`; React and Vue with `oidc-client-ts` context wrappers; Django, FastAPI, and Flask with Authlib; ASP.NET Core and Spring Boot with native OIDC security stacks; and Laravel or Symfony with custom providers in their native security frameworks.

The Auth.js family is covered through `auth-astro`, `@auth/express`, `@mridang/fastify-auth`, `@hono/auth-js`, `@mridang/nestjs-auth`, `next-auth`, `@sidebase/nuxt-auth`, `@auth/qwik`, `@auth/solid-start`, and `@auth/sveltekit`. These examples still configure `ZITADEL_CLIENT_SECRET` for adapter internals even though public-client PKCE does not need a real secret; depending on the adapter, the documented value is empty or randomly generated.
