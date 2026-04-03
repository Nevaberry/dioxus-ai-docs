# Spring Security 7.0 (2026-01)

## PathPatternRequestMatcher Replaces All Others

`MvcRequestMatcher` and `AntPathRequestMatcher` removed. Use `PathPatternRequestMatcher`:
```java
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/api/**").hasRole("USER")  // uses PathPattern by default
    .anyRequest().authenticated()
);
```

## DSL Cleanup

- **`and()` removed** — use lambda DSL exclusively
- **`authorizeRequests` removed** — use `authorizeHttpRequests` only
- **`AuthorizationManager#check` removed** — use `authorize`

## SPA CSRF Support

```java
http.csrf(csrf -> csrf.spa());
```

## Multi-Factor Authentication

Built-in MFA support. Default login page shows factors based on `factor.type` and `factor.reason` params.

## Authorization Server Merged

Spring Authorization Server is now part of Spring Security. PKCE enabled by default.

## OAuth2 for HTTP Service Clients

```java
@ClientRegistrationId("my-client")  // works at type level
interface MyApi {
    @GetExchange("/data")
    Data getData();
}
```

## Other Changes

- Password grant support removed
- Open SAML 4 removed (use SAML 5)
- `ApacheDsContainer` removed (use UnboundID for LDAP)
