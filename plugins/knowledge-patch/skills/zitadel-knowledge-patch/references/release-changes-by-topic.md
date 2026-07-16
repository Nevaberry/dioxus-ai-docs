# Release changes by topic

- [Upgrade, storage, and setup](#upgrade-storage-and-setup)
- [API lifecycle, resources, and authorization](#api-lifecycle-resources-and-authorization)
- [Login, sessions, accounts, and presentation](#login-sessions-accounts-and-presentation)
- [OAuth, OIDC, SAML, SCIM, and token security](#oauth-oidc-saml-scim-and-token-security)
- [Identity providers and LDAP](#identity-providers-and-ldap)
- [Actions and outbound HTTP](#actions-and-outbound-http)
- [Telemetry, projections, and service reporting](#telemetry-projections-and-service-reporting)

## Upgrade, storage, and setup

### Version 3 license change (2025-05)

The ZITADEL repository changes from the Apache 2.0 license to AGPLv3 with version 3, making licensing part of the upgrade assessment.

### PostgreSQL-only storage in version 3 (2025-05)

CockroachDB support is removed in version 3. CockroachDB deployments must migrate to PostgreSQL using ZITADEL's `mirror` workflow rather than upgrade in place.

### Mirror behavior and configuration (2025-05)

The mirror gains a maximum authentication-request-age configuration and can be run multiple times reliably. May maintenance releases also ensure fields are included in mirror projections while notification projections are skipped.

### Required advisory for May maintenance upgrades (2025-05)

Before upgrading to 2.65.10, 2.70.12, 2.71.11, or 3.2.2, read and follow [technical advisory 10016](https://zitadel.com/docs/support/advisory/a10016).

### Decimal event-store values for mirror (2025-06)

Versions 2.66.18, 2.67.15, 2.68.11, and 2.69.11 use decimal event-store values to correct mirror operation. Upgrades to these releases must also follow [technical advisory 10016](https://zitadel.com/docs/support/advisory/a10016).

### Import and export preserve deactivation (4.0.0)

Importing exported deactivated users or organizations no longer recreates them as active; their deactivated state is preserved.

### Interrupted setup cleanup (4.0.0)

If the setup process is killed, failed setup steps are cleaned up automatically.

### Backslashes in queries (2025-08)

Versions 3.4.0 and 4.0.3 correctly escape backslashes in queries.

### Initialization with pre-provisioned database objects (2026-01)

Version 4.10.0 skips privileged database commands during initialization when the corresponding objects already exist.

### PostgreSQL 18 setup compatibility (2026-02)

Version 4.11.0 makes ZITADEL setup compatible with PostgreSQL 18.

### Trusted domains during instance setup (2026-03)

Version 4.12.0 allows trusted domains to be added as part of instance setup.

### PostgreSQL and Redis connection URLs (2026-03)

Version 4.13.0 accepts DSN/URL connection strings for PostgreSQL and Redis.

### Setup migration connection handling (2026-06)

Version 4.15.2 corrects connection handling during setup after migration steps 40, 64, and 70, allowing setup to continue correctly across those migrations.

### Event resource-owner reassignment (2026-06)

Version 4.15.2 allows the event store to overwrite an event's resource owner, enabling event-store operations that need to reassign ownership.

## API lifecycle, resources, and authorization

### System-user permission checks (2025-05)

The new permission-check framework supports system users, allowing system-user operations to participate in the new authorization checks.

### Console API v2 feature flag (2025-05)

Console can use API V2 for human-user creation and session listing behind a feature flag, and it can manage all currently available feature flags.

### Organization context for API v2 user creation (2025-06)

Version 3.3.0 fixes Console's organization context when creating users through API V2, so Console-based creation follows the selected organization.

### Session API permission checks (2025-07)

Versions 2.70.14, 2.71.13, and 3.3.2 correct permission checks on the Session API, changing authorization behavior for affected calls.

### Resource-based API status (4.0.0)

Version 4 completes the resource-based API migration for core instance, organization, project, application, and user resources. Actions V2 and Caches V2 are generally available; Instance Service V2, Project V2, App V2, Authorization V2, Permission V2, and Settings V3 remain beta at this milestone.

### V1 endpoint deprecations (4.0.0)

Version 4 deprecates the following V1 operations in favor of resource-based APIs:

- Organization and user objects: `GetOrgByDomainGlobal`, `AddMachineUser`, `UpdateMachine`, `GenerateMachineSecret`, `RemoveMachineSecret`, `GetMachineKeyByIDs`, `ListMachineKeys`, `AddMachineKey`, `RemoveMachineKey`, `UpdateUserName`, `SetUserMetadata`, `BulkSetUserMetadata`, `ListUserMetadata`, `GetUserMetadata`, `RemoveUserMetadata`, `BulkRemoveUserMetadata`, `UpdateHumanPhone`, `GetPersonalAccessTokenByIDs`, `ListPersonalAccessTokens`, `AddPersonalAccessToken`, `RemovePersonalAccessToken`, and `ListAppKeys`.
- Projects: `GetProjectByID`, `GetGrantedProjectByID`, `ListProjects`, `ListGrantedProjects`, `ListGrantedProjectRoles`, `AddProject`, `UpdateProject`, `DeactivateProject`, `ReactivateProject`, `RemoveProject`, `ListProjectRoles`, `AddProjectRole`, `BulkAddProjectRoles`, `UpdateProjectRole`, `RemoveProjectRole`, `GetProjectGrantByID`, `ListProjectGrants`, `ListAllProjectGrants`, `AddProjectGrant`, `UpdateProjectGrant`, `DeactivateProjectGrant`, `ReactivateProjectGrant`, and `RemoveProjectGrant`.
- Members: `ListUserMemberships`, `ListOrgMembers`, `AddOrgMember`, `UpdateOrgMember`, `RemoveOrgMember`, `ListProjectMembers`, `AddProjectMember`, `UpdateProjectMember`, `RemoveProjectMember`, `ListProjectGrantMembers`, `AddProjectGrantMember`, `UpdateProjectGrantMember`, and `RemoveProjectGrantMember`.
- Instance lifecycle and objects: `GetMyInstance`, `ListInstanceDomains`, `ListInstanceTrustedDomains`, `AddInstanceTrustedDomain`, `RemoveInstanceTrustedDomain`, `GetOrgByID`, `IsOrgUnique`, `GetDefaultOrg`, `ListIAMMembers`, `AddIAMMember`, `UpdateIAMMember`, and `RemoveIAMMember`.

### ConnectRPC transport for new APIs (4.0.0)

All new V2 APIs use gRPC with ConnectRPC exclusively and no longer add OpenAPI 2.0 endpoints; APIs from earlier releases keep their existing transports. ConnectRPC and gRPC-Web requests also have CORS support.

### Organization creation contracts (4.0.0)

`AddOrganizationRequest` accepts a caller-supplied organization ID, with uniqueness constraints preventing duplicate IDs. `AddOrganization()` now returns all organization administrators.

### Initial administrator PAT permission (4.0.0)

The initial administrator personal access token now includes the `IAM_LOGIN_CLIENT` permission.

### User self-deletion (4.0.0)

Users can delete their own accounts, so self-service clients may expose account deletion without an administrator-mediated operation.

### Trusted-domain sorting (4.0.0)

The `ListInstanceTrustedDomains()` gRPC endpoint adds sorting options for deterministic trusted-domain listings.

### `ListAppKeys()` result behavior (2025-08)

Version 4.0.2 fixes `ListAppKeys()` so it returns application keys again.

### Project creation permissions (2025-08)

Version 4.0.2 uses the correct permission when creating a project.

### Permission V2 user checks (2025-08)

Version 4.0.2 uses the correct `userID` column in Permission V2 checks.

### Project-role command permissions (2025-08)

Version 4.0.3 corrects permission checks for adding, updating, and deleting project roles in the command layer.

### Console user API v2 enabled by default (2025-09)

Version 4.1.2 enables `ConsoleUseV2UserApi` by default, changing API V2 user management in Console from opt-in to the default behavior.

### Project creation with members (2025-09)

Version 4.2.0 adds an option to create project members as part of project creation.

### Grant and self-management corrections (2025-09)

Version 4.1.0 correctly handles user grants on same-organization project grants, and version 4.1.1 corrects permission checks for Actions V1 post-creation user grants. Version 4.3.0 also corrects user self-management of metadata and deletion, generated project-grant IDs, and the organization used by user-grant queries.

### User listing by metadata (2025-09)

Version 4.2.0 adds metadata-based user listing. Versions 4.2.2 and 4.3.0 correct metadata-value comparison and sorting for list and export searches.

### API v2 promotions and beta deprecations (2025-10)

Version 4.5 promotes the Application and internal Permission services from V2 beta to GA, deprecates Settings V2 beta, and deprecates V2 beta endpoints where V2 replacements exist. Version 4.6 moves the Authorization and Instance services to V2 and promotes the Project service to GA while deprecating Project V2 beta.

### User-grant queries for multiple users (2025-10)

Version 4.3.1 adds an `InUserIDs` query to user-grant listing, allowing one request to select grants for multiple specified users.

### Organization v2beta permission checks (2025-11)

Version 4.6.3 corrects the permission check used by the Organization V2 beta service, changing authorization outcomes for affected calls.

### Typed-URL API binding (2025-11)

Version 4.6.5 adds an additional binding for URLs that include a type, enabling the typed URL form in API calls.

### Feature flags through environment variables (2025-11)

Version 4.6.5 makes feature flags usable from environment-variable configuration.

### Console framework configuration (2025-11)

Version 4.6.5 adds the missing framework configuration to Console's application-creation flow, so those framework choices can be configured during app creation.

### Organization API moves to v2 (2025-11)

Version 4.7.0 moves the Organization API from V2 beta to V2. Clients using the beta service should migrate to the corresponding V2 service.

### User-listing v2 permission upgrade caveat (2025-12)

Versions 3.4.5 and 4.7.2 force V2 permission checks for user listing, but both releases warned that some users could no longer list users after upgrading. The issue is resolved in versions 3.4.6 and 4.7.4 respectively, so affected deployments should upgrade past the problematic maintenance release.

### Membership-role synchronization (2025-12)

Version 4.7.3 synchronizes membership roles from projections, and version 4.7.4 corrects the setup execution check for that synchronization.

### Administrator-list filters (2026-01)

Version 4.9.1 implements the previously missing filters on the `ListAdministrators` endpoint.

### Organization context on creation (2026-01)

Version 4.10.0 correctly handles `organization_id` on API creation requests.

### Application lookup by protocol identifier (2026-01)

Version 4.10.0 allows application filtering by OIDC client ID and SAML entity ID.

### Caller-provided OIDC application IDs (2026-02)

Version 4.11.0 honors an ID supplied in an OIDC application creation request, so callers can rely on the requested identifier instead of having it replaced.

### Console self-management without explicit roles (2026-02)

Version 4.11.0 restores Console self-management for users who do not have explicit roles.

### Allowed-language API data (2026-02)

Version 4.11.0 adds `allowed_languages` to API responses.

### User-update permissions use request data (2026-02)

Versions 4.11.1 and 3.4.7 evaluate user-update permissions from the data supplied in the request, correcting authorization for affected updates.

### Machine-user access-token type (2026-03)

Version 4.12.0 lets the API specify the access-token type for a machine user.

### Metadata APIs and Actions V2 (2026-03)

Version 4.13.0 adds user metadata to `CreateUser` and a metadata field to `UpdateUser`; `SetOrganizationMetadata` and `SetUserMetadata` can also delete metadata. Actions V2 can update metadata through the `RetrieveIdentityProviderIntent` API.

### Management API and organization-scope enforcement (2026-03)

Versions 3.4.8 and 4.12.2 correct permission checks on some management API endpoints and handle encoded paths in authentication middleware. Versions 3.4.9 and 4.12.3 enforce organization scopes.

### Console API v2 configuration key (2026-04)

Version 4.13.1 restores `ConsoleUseV2UserApi` as the configuration feature key; deployments configuring Console's V2 user API must use that key.

### Certificate and public-key authentication (2026-04)

Version 4.14.0 adds an option to use X.509 certificates for system-API-user tokens and allows ECDSA and ED25519 public keys.

### Console configuration corrections (2026-04)

Version 4.14.0 always shows the settings page to administrators and prevents duplicate SMTP configuration creation. It also corrects JWT-provider callback URLs and normalizes updates containing an empty OIDC redirect URI.

### Console role and Actions V1 permissions (2026-05)

Version 4.15.0 allows role assignments to be deleted from an administrator profile and displays Actions V1 in Console using the correct permissions.

## Login, sessions, accounts, and presentation

### SAML application login UI selection (2025-05)

Console can specify the Login UI for SAML applications, making the login implementation selectable per SAML app.

### Invite codes for verified email addresses (2025-05)

Versions 3.2.1 and 2.71.11 accept invite codes for users whose email addresses are already verified.

### Proxy protocol validation and HTTPS enforcement (2025-05)

Versions 2.70.12, 2.71.11, and 3.2.2 validate the protocol header and enforce HTTPS, making correct proxy scheme information part of request acceptance.

### Restricted-language settings (2025-06)

Versions 2.70.13, 2.71.12, and 3.2.3 fix setting restricted languages, so deployments that rely on language restrictions should use one of these maintenance releases or newer.

### Login v1 password reset by email or phone (2025-07)

Version 3.3.1 handles password reset when a user authenticates with an email address or phone number.

### Existing passkeys and U2F credentials in the Session API (2025-07)

Version 3.3.1 allows existing passkeys and U2F credentials to be used with the Session API.

### Login V2 default for new customers (4.0.0)

Login V2, built on the Session API, reaches feature parity with Login V1 and becomes the default login experience for new customers.

### Hosted-login localization (4.0.0)

A hosted-login translation API is available, and hosted login adds Turkish language support.

### Authenticated account selection (2025-08)

Versions 2.71.15, 3.4.0, and 4.0.3 restrict the Login select-account page to previously authenticated users.

### Session expiration filtering (2025-08)

Versions 2.71.16, 3.3.3, and 4.0.1 add an expiration-date filter to the List Sessions API.

### Case-insensitive login discovery (2025-08)

Version 4.0.2 ignores case in login-name and email matching during user discovery.

### Login logout completion (2025-08)

Version 4.0.3 uses `/logout/done` as the successful Login logout page and accepts `post_logout_redirect` as that page's post-logout URI parameter. Keep this Login route parameter distinct from OIDC `post_logout_redirect_uri`.

### Login V2 integration URLs (2025-09)

Version 4.1.0 makes the Login V2 feature base URI configurable and supplies default URL templates. Version 4.2.0 adds the Login V2 URL to identity-provider configuration in Console.

### Login callback, proxy, and development-mode behavior (2025-09)

Version 4.1.0 checks email verification before continuing a login callback, version 4.2.0 corrects Safari cookie handling in Development Mode, and version 4.3.0 derives the correct Login host when running behind a proxy.

### Multi-method MFA session validation (2025-09)

Version 4.3.0 allows MFA session validation to account for multiple authentication methods.

### Organization-scoped login and external passkeys (2025-10)

Version 4.3.1 adds organization-domain scoping and external passkey registration to Login. Version 4.5 also scopes identity-provider auto-linking to the organization.

### Login frontend theming and localization (2025-10)

Version 4.4 adds a comprehensive Login theme system and translation support. Version 4.5 adds Japanese localization to the Login frontend.

### Dual-stack Login frontend (2025-10)

Version 4.4 serves the Login UI over both IPv4 and IPv6, allowing it to operate in either network environment.

### Invite-code delivery and email verification (2025-10)

Version 4.5 sends invite codes only to users whose email address is unverified. A verified user no longer receives a code through this delivery path.

### Authentication hardening across maintained release lines (2025-10)

Versions 2.71.18, 3.4.3, and 4.6.0 check for 2FA even when it is not enforced, honor lockout policy during password changes that verify the old password, add tar-pit checks, and sanitize host headers before use.

### MFA checks ignore unready authentication methods (2025-11)

Versions 2.71.19, 3.4.4, and 4.6.5 ignore authentication methods that are not ready when evaluating MFA requirements. An incomplete method no longer participates in the MFA-requirement decision.

### Login proxy-header propagation (2025-12)

Version 4.7.1 centralizes Login's host-header resolution and forwards the resolved headers to its API calls, correcting behavior when Login operates behind a proxy.

### Username changes from the 2FA screen (2025-12)

Version 4.7.2 fixes the Login back button on the two-factor authentication screen so a user can return and change the username.

### Login frontend security updates (2025-12)

Version 4.7.5 updates its React and Next.js components for CVE-2025-55182, CVE-2025-66478, CVE-2025-55184, and CVE-2025-55183.

### Login V1 password verification (2025-12)

Version 4.7.6 updates Login V1's password-verification handling, changing the behavior deployments receive from that login path.

### SMTPUTF8 addresses and passwordless SMTP configuration (2026-01)

Version 4.8.1 accepts SMTPUTF8 email addresses. Version 4.9.1 also permits an SMTP configuration with no password.

### Recovery-code MFA (2026-01)

Version 4.9.0 adds recovery codes as a supported MFA method.

### Login policy for unknown usernames (2026-01)

Version 4.9.0 corrects the `LoginPolicy.IgnoreUnknownUsernames` configuration, and version 4.9.1 correctly routes Login to `/password` when `ignoreUnknownUsername` is enabled.

### Empty custom Login headers (2026-01)

Version 4.9.0 deletes a custom request header when its value is empty instead of retaining the header.

### Additional locales (2026-01)

Version 4.9.0 adds Ukrainian, French, and Dutch localization, and version 4.10.0 adds Arabic language support.

### Generalized code-verification errors (2026-01)

Versions 3.4.6 and 4.9.1 generalize the error message returned by code-verification failures, so clients must not rely on the earlier specific messages.

### Password-expiry and password-change behavior (2026-01)

Version 4.10.0 limits Login V1 password-expiry checks to local users that have a password. It also corrects missing-permission and eventual-consistency failures on `/password/change`.

### Passkey reauthentication (2026-01)

Version 4.10.0 adds passkey reauthentication to Login.

### SMS OTP country-code selection (2026-01)

Login V1 adds a country-code selector for SMS OTP. The feature was not correctly included in the version 4.10.0 build, so deployments that rely on it must use version 4.10.1.

### Login local-authentication policy naming (2026-02)

Version 4.11.0 replaces `allowUsernamePassword` with `allowLocalAuthentication` in Login and updates the corresponding Console wording. The Login UI also now respects configured password-complexity settings.

### SMTP OAuth and unauthenticated configurations (2026-02)

Version 4.11.0 adds XOAUTH/XOAuth2 for SMTP and exposes it in Console. SMTP testing no longer requires authentication; when no authentication is configured, the gRPC response reports auth `none` and includes scopes.

### Automatic email-verification control (2026-02)

Version 4.11.0 allows Login's automatic email verification to be disabled.

### Invite-code lifecycle (2026-03)

Version 4.12.0 permits creating a new invite code while the previous code is still valid. Versions 3.4.8 and 4.12.2 base WebAuthn invite-code expiration on the code's creation date.

### Password reset and session termination (2026-03)

Version 4.12.0 adds a current-password field to password reset and terminates a user's sessions after that user is deleted or deactivated.

### Login service credentials and TLS (2026-03)

Version 4.12.0 lets Login authenticate from a service-key file selected by `LOGIN_SERVICE_KEY_FILE`, adds optional TLS termination, and uses the OpenSSL CA store for certificate validation. Version 4.13.0 also supports supplying a private-key file through environment configuration.

```sh
LOGIN_SERVICE_KEY_FILE=/path/to/service-key
```

### Login deployment and routing behavior (2026-03)

Version 4.12.0 resolves Login's CSP `img-src` at build time rather than runtime, derives available languages dynamically from settings, and adds redirect configuration for multi-domain deployments. Version 4.13.0 makes Login V2 honor `ui_locales`.

### Instance setup and recovery-code activation (2026-04)

Version 4.13.1 stops sending initialization emails to administrators during instance setup, corrects the setup organization-existence check, and makes a recovery code active as soon as it is added.

### Login invitation and protocol context (2026-04)

Version 4.14.0 sends users with no primary authentication method through the invitation flow instead of email verification. Resending an invite or email code carries the OIDC or SAML request ID, email verification preserves OIDC request context, and duplicate email-code verification is prevented.

### Login trust, key, and startup configuration (2026-04)

Version 4.14.0 loads certificates from `SSL_CERT_DIR` without requiring hashed filenames, supports PKCS#1 keys for Login client authentication, and adds `ZITADEL_API_AWAITINITIALCONN` support.

### Login presentation (2026-04)

Version 4.14.0 adds Portuguese translations to Login V2 and makes the theme toggle respect branding `themeMode`, including the related CSP correction.

### Localized signup legal links (2026-05)

Version 4.15.0 resolves localized legal links correctly during signup.

### Login proxy custom headers (2026-06)

Version 4.15.1 applies custom request headers configured through environment variables when Login proxies requests, so proxied API calls receive those headers.

### Forced-MFA email-verification fallback (2026-06)

Version 4.15.1 redirects to email verification when MFA is forced but no factors are visible, allowing the login flow to continue instead of leaving the user without a usable factor.

### Registration session retry (2026-06)

Version 4.15.1 retries session creation after registration when it receives `NotFound`, rather than ending the registration flow on that response.

### Passkey registration from identity-provider sessions (2026-06)

Version 4.15.2 accepts identity-provider sessions during passkey registration, so externally authenticated users can register a passkey in that flow.

### Login custom branding fonts (2026-06)

Version 4.15.2 loads the custom font from branding settings and permits it in Login's CSP, preventing the configured font from being blocked.

## OAuth, OIDC, SAML, SCIM, and token security

### Web Keys management moves to API v2 beta (2025-05)

OIDC Web Keys can be managed in Console or through the beta API V2; the API V3 alpha requests are removed. Web Key generation is also available in instance defaults.

### Native HTTPS loopback redirects (2025-05)

Native applications may use `https://` loopback redirect addresses, so HTTPS loopback callbacks no longer need to be rejected during application configuration.

### Imported password hash formats (2025-05)

Password-import compatibility expands to salted MD5 in version 3.0 and to SHA2 and PHPass in version 3.1, allowing migrations to preserve passwords stored in those formats.

### Logout integration support (2025-05)

OIDC back-channel logout works with custom login UIs in version 3.0, and version 3.2 adds federated logout for SAML identity providers.

### Login v1 organization token context (2025-07)

Version 3.3.1 ensures that Login V1 always puts the user's organization into the token context, so downstream token processing can rely on that context being present.

### SCIM email type attribute (2025-07)

Version 3.3.1 adds the `type` attribute to `ScimEmail`, expanding the SCIM email representation consumed by clients.

### OIDC logout hints (4.0.0)

The OIDC `end_session_endpoint` handles `logout_hint`, so relying parties can supply that hint during logout.

### Typed SAML identity-provider intent data (4.0.0)

Identity-provider intents return typed SAML form-post data.

### SAML authentication milestone (4.0.0)

Successful SAML application authentication records the `AuthenticationSucceededOnApplication` milestone on the session.

### SCIM create-password handling (4.0.0)

A SCIM metadata setting can ignore a random password supplied during user creation, allowing provisioning integrations to avoid applying that generated password.

### OIDC client ID configuration (2025-08)

Versions 3.3.3 and 4.0.1 disable the client ID in OIDC configuration.

### SAML responses without a NameID (2025-08)

Versions 3.3.3 and 4.0.1 use the transient mapping attribute when a SAML response has no `NameID`.

### Generated Web Keys setup step (2025-08)

Version 3.4.0 generates a Web Keys setup step, incorporating Web Key initialization into setup.

### Web Keys enabled by default on version 3 (2025-09)

Version 3.4.1 enables the OIDC Web Keys feature by default.

### Configurable SAML identity-provider signatures (2025-09)

Version 4.1.0 adds `SignatureMethod` configuration for SAML identity providers, and version 4.3.0 corrects signature-algorithm handling.

### Invalid OIDC ID token hints are ignored (2025-09)

Versions 3.4.2 and 4.1.4 ignore invalid `id_token_hint` values instead of rejecting the flow.

### Requested-audience roles in OIDC userinfo (2025-09)

Version 4.3.0 adds a userinfo claim containing roles for all requested audiences.

### Requested-audience roles claim reverted (2025-10)

Version 4.3.2 removes the OIDC userinfo claim added in 4.3.0 for returning roles for all requested audiences. Clients must not rely on that claim after upgrading.

### Drupal 7 password hashes (2025-10)

Version 4.6.0 adds Drupal 7 hash verification through passwap, expanding compatibility for migrated passwords stored in that format.

### SAML service-provider certificate Common Name (2025-10)

Version 4.5 adds a Common Name to the SAML service-provider certificate, which may affect integrations that inspect that certificate field.

### Bare localhost OIDC redirect URIs (2025-10)

Version 4.5 accepts localhost OIDC redirect URIs without a path or explicit port, such as `http://localhost`.

### Client-credentials ID token lifetime (2026-01)

Version 4.9.0 adds a lifetime to ID tokens issued through the client-credentials flow; clients must no longer expect these tokens to omit lifetime information.

### Login V1 reauthentication with ID token hints (2026-01)

Version 4.9.1 corrects automatic reauthentication through `id_token_hint` in Login V1.

### SAML POST flow cookie limits (2026-02)

Version 4.11.0 changes Login's SAML POST flow to bypass cookie limits and corrects SAML service-provider POST handling.

### Token exchange and back-channel logout graduate (2026-02)

Version 4.11.0 promotes OAuth/OIDC token exchange and OIDC back-channel logout from beta to GA. Console can also manage an OIDC application's back-channel logout URI.

### Token V2 subject validation (2026-02)

Versions 4.11.0 and 3.4.7 compare the Token V2 subject with the user ID, so mismatched identities no longer pass that subject check.

### Gateway and OIDC hardening (2026-04)

Version 4.14.0 increases gRPC `MaxSendMsgSize`, returns HTTP 401 for unauthenticated V1 gateway errors, corrects invalid JWT-assertion error handling, and uses authenticated encryption for opaque OIDC tokens. The instance interceptor also propagates errors other than `NotFound`.

### OAuth client binding during token use (2026-06)

Versions 3.4.12 and 4.15.2 verify `client_id` during authorization-code exchange and refresh-token flows, preventing a code or refresh token from being used by the wrong client.

### Token-exchange client and scope validation (2026-06)

Version 4.15.3 validates the client and scopes during token exchange, rejecting exchanges whose client or requested scopes are invalid.

### OIDC and SAML failure redirect handling (2026-06)

Version 4.15.3 guards `defaultRedirectUri` in OIDC and SAML `FailedPrecondition` paths, so those error flows no longer assume a default redirect is present.

## Identity providers and LDAP

### Single-use intent tokens (2025-05)

Intent tokens now expire and cannot be reused, so integrations must complete an intent with a fresh, unexpired token.

### LDAP user-filter combination (2025-05)

Versions 3.1.0 and 2.71.11 correctly OR-join multiple LDAP user filters, which can change matches for deployments using compound LDAP filtering.

### JWT identity-provider intents (2025-06)

Version 3.3.0 adds intent support for JWT identity providers, allowing JWT-based external identity flows to participate in the identity-provider intent lifecycle.

### Login v1 auto-linking with suffixed usernames (2025-07)

Version 3.3.1 correctly auto-links users in organizations that use suffixed usernames.

### Case-insensitive identity-provider external IDs (2025-08)

Versions 3.3.6 and 4.0.2 compare identity-provider external IDs case-insensitively.

### Entra ID intent user information (2025-08)

Version 4.0.3 correctly unmarshals Entra ID user information when retrieving identity-provider intent information.

### Identity-provider flow routing and callbacks (2025-10)

Version 4.3.1 redirects directly into an identity-provider flow when password authentication is disabled. Version 4.5 adds identity-provider login fallback and a `postError` redirect URL, while 4.6.1 corrects the success URL used by identity-provider flows.

### GitHub identity-provider email fallback (2025-10)

When GitHub returns an empty profile email, version 4.3.1 queries GitHub's email data separately so the federated identity can still obtain an email address.

### LDAP identifier character support (2025-10)

Version 4.4 supports non-ASCII characters in LDAP bind distinguished names. Version 4.5 also allows special characters in LDAP sign-in identifiers.

### Identity-provider linking conditions are validated (2025-11)

Versions 2.71.19, 3.4.4, and 4.6.6 validate the conditions used for identity-provider linking. Account-linking integrations should expect configured linking conditions to be enforced.

### Identity-provider login without organization context (2025-11)

Version 4.6.3 falls back to the default organization when Login creates an identity-provider user without organization context. Version 4.7.0 also enables organization discovery for Login flows started without that context.

### External identity-provider user updates (2025-11)

Version 4.6.5 restores user-information updates when a user authenticates through an external identity provider.

### Explicit identity-provider linking from an existing session (2026-01)

Version 4.9.0 allows Login to explicitly link an identity provider using an existing session ID.

### Identity-provider intent data (2026-03)

Version 4.12.0 adds `login_hint` to identity-provider intents and returns a refresh token in `RetrieveIdentityIntentResponse`.

### Identity-provider discovery and registration policy (2026-03)

Version 4.12.0 checks primary authentication methods during Login user discovery. Version 4.13.0 removes the `loginSettings.allowRegister` check from identity-provider flows.

### LDAP username-filter escaping (2026-05)

Versions 3.4.10 and 4.15.0 escape usernames used in LDAP filters, preventing username characters from being interpreted as filter syntax.

### JWT identity-provider claim validation (2026-06)

Versions 3.4.12 and 4.15.2 always validate `exp` and `iat` claims for JWT identity providers and manage and validate the token audience. Tokens that fail timing or audience checks are no longer accepted.

### PKCE for external OAuth and OIDC providers (2026-06)

Version 4.15.2 applies PKCE when building OAuth and OIDC identity providers, allowing integrations that require PKCE to complete their authorization flows.

### Verified email required for identity-provider auto-linking (2026-06)

Version 4.15.3 verifies an external user's email before auto-linking the account. An unverified external email address no longer qualifies for automatic linking.

## Actions and outbound HTTP

### Actions management moves to API v2 beta (2025-05)

Actions V2 management is available in Console, and the beta API V2 replaces the removed API V3 alpha requests. Actions V2 also gains function support, no longer requires its feature flag, and exposes the refresh token to post-authentication action context.

### Actions V2 context and ordering (4.0.0)

Actions V2 context includes `clientID`. Action lists default to creation-date sorting, and execution ordering uses IDs.

### User information in action metadata context (2025-08)

Version 4.0.1 adds user information to the action context when setting metadata.

### Actions V2 execution input (2025-09)

Versions 3.4.2 and 4.1.3 restore `event_payload` on event executions. Version 4.2.0 also propagates request headers into Actions V2 executions.

### HTTP-provider signing keys (2025-09)

Version 4.2.0 adds signing-key support to HTTP providers.

### Actions V1 organization metadata (2025-11)

Version 4.6.4 returns organization metadata from Actions V1 again, restoring behavior for actions that consume it.

### Actions V2 `all` condition execution (2025-12)

Version 4.7.1 correctly executes request- and response-type Actions V2 executions whose condition is `all`.

### JWT and JWE payload types for Actions V2 (2025-12)

Version 4.8.0 adds JWT and JWE payload-type options to Actions V2.

### Actions target-URL denylist (2026-02)

Version 4.11.1 adds a denylist for Actions target URLs, so Action configurations can reject targets covered by that denylist.

### Protected outbound HTTP connections (2026-06)

Version 4.15.2 uses the protected HTTP client for outgoing connections, making outbound requests subject to its connection protections.

## Telemetry, projections, and service reporting

### Telemetry controls (2025-05)

The metrics and tracing service name is configurable in version 3.0, and projection handlers expose Prometheus metrics.

### Organization cache isolation (2025-06)

Versions 2.70.13, 2.71.12, and 3.2.3 prevent one instance from overwriting another instance's organization cache.

### River queue OpenTelemetry metrics (2025-07)

Version 3.3.1 enables OpenTelemetry metrics for the River queue, allowing its queue activity to be included in telemetry collection.

### Opt-out Service Ping (4.0.0)

Service Ping securely sends anonymized instance metrics and usage data to the customer portal and is opt-out. Its endpoint is corrected at this milestone, and its default interval is validated and randomized.

### OpenTelemetry metric scope metadata (2025-08)

Versions 2.71.15, 3.3.6, and 4.0.2 stop adding default OpenTelemetry scope information to metrics, so collectors and dashboards must not rely on that default metadata.

### Per-instance projection disabling (2025-08)

Versions 3.3.3 and 4.0.1 allow projections to be disabled for specific instances.

### Expanded Service Ping reporting (2025-09)

Version 4.2.0 adds more resource counts to Service Ping reports, and version 4.2.1 logs report body sizes.

### Projection event-processing correctness (2025-09)

Versions 3.4.2 and 4.2.0 prevent projections from skipping events written in the same microsecond or raced by event pushes. Version 3.4.2 also prevents two projections from using the same table, while versions 3.4.2 and 4.2.1 update failed-event state after reduction errors.

### Corrected River metric units (2025-09)

Versions 2.71.17, 3.4.2, and 4.1.0 correct the units reported by River OpenTelemetry metrics, which may change dashboard and alert interpretation after upgrade.

### Corrected gRPC status-code metrics (2025-10)

Version 4.6.0 corrects status-code mapping in `grpc_server_grpc_status_code_total`, so dashboards and alerts may classify gRPC outcomes differently after upgrade.

### Projection locking follows configuration (2025-10)

Version 4.6.2 bases projection locking behavior on its configuration, so deployments with non-default projection-locking settings should expect those settings to be honored.

### ConnectRPC tracing (2025-12)

Version 4.7.2 adds the tracing interceptor to ConnectRPC services, making those API calls participate in request tracing.

### Cross-application tracing for API v2 (2026-02)

Version 4.11.0 enables cross-application distributed tracing for V2 APIs.

### Log streams and GCP error reporting (2026-02)

Version 4.11.0 adds log streams and GCP Error Reporting support. Version 4.11.1 corrects the stream used during setup and correctly masks grouped structured-log attributes.

### Login readiness and push-based OpenTelemetry (2026-03)

Version 4.13.0 adds a Login readiness-probe endpoint and push-based OpenTelemetry logs, metrics, and traces. OpenTelemetry resources use the configured service name.

### Standard OpenTelemetry environment variables (2026-04)

Version 4.14.0 supports standard OpenTelemetry environment variables through autoexport.
