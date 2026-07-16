# Security

## Contents

- [Security DSL and authorization migration](#security-dsl-and-authorization-migration)
- [OAuth 2.0 and authorization server](#oauth-20-and-authorization-server)
- [JWT resource servers](#jwt-resource-servers)
- [Multi-factor authentication, WebAuthn, and one-time tokens](#multi-factor-authentication-webauthn-and-one-time-tokens)
- [CSRF, login redirects, and gateway trust](#csrf-login-redirects-and-gateway-trust)
- [SAML and LDAP](#saml-and-ldap)
- [Context propagation and observations](#context-propagation-and-observations)
- [TLS and session integrations](#tls-and-session-integrations)

## Security DSL and authorization migration

Spring Security 7 makes the following source-level changes (batch
`4.0.0-framework-7`):

- `AuthorizationManager#check` is removed; call `authorize`.
- Legacy access-decision APIs moved to `spring-security-access`.
- `AuthorizationManagerFactory` can supply managers for request- and method-based
  authorization.
- `HttpSecurity.and()` and `authorizeRequests` are removed.
- Replace `MvcRequestMatcher` and `AntPathRequestMatcher` with
  `PathPatternRequestMatcher`.

Servlet and WebFlux security configurations can be split into modules rather than
assembled as one monolith.

## OAuth 2.0 and authorization server

### Broader client auto-configuration

OAuth 2 client beans are auto-configured outside web applications as well as within
them (since `3.5.0`). Servlet and reactive web-security setup lives in separate
auto-configurations:

- servlet client configuration backs off only for a reactive web application; and
- reactive client configuration backs off only for a servlet web application.

### DPoP and confidential-client PKCE

Spring Security 6.5 clients support Demonstrating Proof of Possession. Servlet and
reactive confidential clients opt into PKCE with
`ClientRegistration.clientSettings.requireProofKey=true` (since `3.5.0`).

### Client and authorization-server changes

In `4.0.0-framework-7`:

- password-grant support is removed;
- HTTP service clients gain OAuth 2.0 integration;
- `@ClientRegistrationId` may be placed on a type;
- dynamic client registration is supported;
- `NimbusJwtDecoder` accepts a custom `JwkSource`;
- `NimbusJwtEncoder` has a builder for EC or RSA key pairs and secret keys; and
- Authorization Server enables PKCE by default.

Spring Authorization Server is now a Spring Security module. The former Kerberos
extension is also incorporated as a module.

## JWT resource servers

Servlet and reactive resource servers can derive authorities from one or more SpEL
expressions through
`spring.security.oauth2.resourceserver.jwt.authorities-claim-expressions` (since
`4.1.0`).

This setting is mutually exclusive with authority claim-name and delimiter
configuration. `authority-prefix` replaces the default `SCOPE_` prefix.
Resource-server auto-configuration now also works in non-web applications.

## Multi-factor authentication, WebAuthn, and one-time tokens

### Multi-factor authentication

Spring Security adds multi-factor authentication support. The default login page can
expose factors through the `factor.type` and `factor.reason` parameters (batch
`4.0.0-framework-7`).

### WebAuthn

Spring Security 6.5 adds JDBC persistence for WebAuthn/passkeys. The `webAuthn` DSL
accepts a custom HTTP message converter and a custom
`PublicKeyCredentialCreationOptionsRepository` (since `3.5.0`).

### One-time tokens

`oneTimeTokenLogin()` can customize `GenerateOneTimeTokenRequest` creation through a
`GenerateOneTimeTokenRequestResolver` (since `3.5.0`).

## CSRF, login redirects, and gateway trust

### SPA CSRF

Use the dedicated single-page-application mode (batch
`4.0.0-framework-7`):

~~~java
http.csrf(csrf -> csrf.spa());
~~~

### Relative login redirects

`LoginUrlAuthenticationEntryPoint` prefers relative redirects. This changes the
`Location` value visible to clients and tests (batch
`4.0.0-framework-7`).

### Trusted gateway proxies

Spring Cloud Gateway no longer processes `X-Forwarded-*` or `Forwarded` headers by
default. Configure a Java regular expression for trusted proxies; otherwise,
client-supplied forwarding headers remain untrusted (batch
`spring-cloud-2025.0.0`):

~~~properties
spring.cloud.gateway.server.webflux.trusted-proxies=10\.0\.0\..*
spring.cloud.gateway.server.webmvc.trusted-proxies=10\.0\.0\..*
~~~

## SAML and LDAP

### SAML 2.0

In `4.0.0-framework-7`:

- APIs based on `AssertingPartyDetails` are removed; use
  `AssertingPartyMetadata`.
- `Saml2AuthenticationTokenConverter` no longer accepts GET requests.
- OpenSAML 5 replaces OpenSAML 4.
- A JDBC `AssertingPartyMetadataRepository` is available.
- Single logout returns a `<saml2:LogoutResponse>` even when validation fails.

### LDAP tests and embedded servers

`ApacheDsContainer` and related ApacheDS integration are removed; use UnboundID for
LDAP tests and embedded setups (batch `4.0.0-framework-7`).

Set LDAP referral behavior with `spring.ldap.referral` (since `3.5.0`).

The embedded LDAP server can serve LDAPS when an SSL bundle is selected with
`spring.ldap.embedded.ssl.bundle` (since `4.1.0`).

## Context propagation and observations

Spring Security 6.5 can propagate the security context automatically with
Micrometer. The observation key typo
`security.security.reached.filter.section` is corrected to
`spring.security.reached.filter.section`; migrate dashboards and reports that use
the old key (since `3.5.0`).

## TLS and session integrations

### Mail

Configure `JavaMailSender` TLS through an SSL bundle under `spring.mail.ssl.*`
(since `3.4.0`).

### Reactive indexed sessions

Reactive web applications can use Spring Session's `indexed` repository type (since
`3.4.0`). See the data reference for repository details.
