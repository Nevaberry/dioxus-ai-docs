# Release changes by topic

Use the exact batch attribution on each item when evaluating a maintenance or feature upgrade. Items are grouped by the task they affect rather than by release date.

## Upgrade, storage, setup, and data behavior

- **Version 3 license change (2025-05).** The repository changes from Apache 2.0 to AGPLv3 with version 3, making licensing part of the upgrade assessment.
- **PostgreSQL-only storage in version 3 (2025-05).** CockroachDB support is removed in V3.0. Migrate CockroachDB deployments to PostgreSQL with `mirror`; do not upgrade them in place.
- **Imported password hash formats (2025-05).** Password import adds salted MD5 in V3.0 and SHA2 and PHPass in V3.1 so those stored passwords can survive migration.
- **Mirror behavior and configuration (2025-05).** Mirror adds maximum authentication-request age, becomes reliably repeatable, includes fields in mirror projections, and skips notification projections in the May maintenance releases.
- **Required advisory for May maintenance upgrades (2025-05).** Before 2.65.10, 2.70.12, 2.71.11, or 3.2.2, follow [technical advisory 10016](https://zitadel.com/docs/support/advisory/a10016).
- **Organization cache isolation (2025-06).** Versions 2.70.13, 2.71.12, and 3.2.3 prevent one instance from overwriting another instance's organization cache.
- **Decimal event-store values for mirror (2025-06).** Versions 2.66.18, 2.67.15, 2.68.11, and 2.69.11 use decimal event-store values to correct mirror; these upgrades also require advisory 10016.
- **Import and export preserve deactivation (4.0.0).** Exported deactivated users and organizations remain deactivated when imported.
- **Interrupted setup cleanup (4.0.0).** A killed setup process now cleans up failed setup steps automatically.
- **Per-instance projection disabling (2025-08).** Versions 3.3.3 and 4.0.1 allow selected projections to be disabled for specific instances.
- **Backslashes in queries (2025-08).** Versions 3.4.0 and 4.0.3 correctly escape backslashes in queries.
- **Generated Web Keys setup step (2025-08).** Version 3.4.0 incorporates Web Key generation into setup.
- **Projection event-processing correctness (2025-09).** Versions 3.4.2 and 4.2.0 stop projections skipping same-microsecond or push-raced events; 3.4.2 also prevents projections sharing a table, and 3.4.2 plus 4.2.1 update failed-event state after reduction errors.
- **Drupal 7 password hashes (2025-10).** Version 4.6.0 adds verify-only Drupal 7 hash compatibility through passwap.
- **Projection locking follows configuration (2025-10).** Version 4.6.2 honors configured projection-locking behavior.
- **Membership-role synchronization (2025-12).** Version 4.7.3 synchronizes membership roles from projections; 4.7.4 corrects the setup execution check for that synchronization.
- **Initialization with pre-provisioned database objects (2026-01).** Version 4.10.0 skips privileged initialization commands when their database objects already exist.
- **PostgreSQL 18 setup compatibility (2026-02).** Version 4.11.0 makes setup work with PostgreSQL 18.
- **Trusted domains during instance setup (2026-03).** Version 4.12.0 can add trusted domains while setting up an instance.
- **PostgreSQL and Redis connection URLs (2026-03).** Version 4.13.0 accepts DSN/URL connection strings for both PostgreSQL and Redis.
- **Instance setup and recovery-code activation (2026-04).** Version 4.13.1 stops administrator initialization emails during setup, fixes the setup organization-existence check, and activates a recovery code as soon as it is added.
- **Setup migration connection handling (2026-06).** Version 4.15.2 fixes connection handling after setup migrations 40, 64, and 70.
- **Event resource-owner reassignment (2026-06).** Version 4.15.2 lets the event store overwrite an event's resource owner where reassignment is required.
- **FIPS 140-3 build and checks (2026-08).** Version 4.16.0 adds a FIPS 140-3-compliant build and runtime checks for a distinct validated runtime path.

## API generations, resources, permissions, and queries

- **Actions management moves to API v2 beta (2025-05).** Console and API V2 beta replace the removed V3 alpha Actions requests. V2 adds functions, drops its feature flag, and exposes the refresh token to post-authentication context.
- **Web Keys management moves to API v2 beta (2025-05).** Console and API V2 beta replace the removed V3 alpha Web Key requests, and instance defaults can generate Web Keys.
- **System-user permission checks (2025-05).** The new permission framework supports system users.
- **Console API v2 feature flag (2025-05).** Console can create humans and list sessions through API V2 behind a feature flag and can manage all available feature flags.
- **Organization context for API v2 user creation (2025-06).** Version 3.3.0 makes Console V2 user creation use the selected organization.
- **Session API permission checks (2025-07).** Versions 2.70.14, 2.71.13, and 3.3.2 correct Session API authorization checks.
- **Resource-based API status (4.0.0).** Version 4 completes resource-based migration for core instance, organization, project, application, and user resources. Actions V2 and Caches V2 are GA; Instance V2, Project V2, App V2, Authorization V2, Permission V2, and Settings V3 remain beta at that milestone.
- **V1 endpoint deprecations (4.0.0).** Replace these V1 calls with resource-based APIs:

  - Organization and user objects: `GetOrgByDomainGlobal`, `AddMachineUser`, `UpdateMachine`, `GenerateMachineSecret`, `RemoveMachineSecret`, `GetMachineKeyByIDs`, `ListMachineKeys`, `AddMachineKey`, `RemoveMachineKey`, `UpdateUserName`, `SetUserMetadata`, `BulkSetUserMetadata`, `ListUserMetadata`, `GetUserMetadata`, `RemoveUserMetadata`, `BulkRemoveUserMetadata`, `UpdateHumanPhone`, `GetPersonalAccessTokenByIDs`, `ListPersonalAccessTokens`, `AddPersonalAccessToken`, `RemovePersonalAccessToken`, and `ListAppKeys`.
  - Projects: `GetProjectByID`, `GetGrantedProjectByID`, `ListProjects`, `ListGrantedProjects`, `ListGrantedProjectRoles`, `AddProject`, `UpdateProject`, `DeactivateProject`, `ReactivateProject`, `RemoveProject`, `ListProjectRoles`, `AddProjectRole`, `BulkAddProjectRoles`, `UpdateProjectRole`, `RemoveProjectRole`, `GetProjectGrantByID`, `ListProjectGrants`, `ListAllProjectGrants`, `AddProjectGrant`, `UpdateProjectGrant`, `DeactivateProjectGrant`, `ReactivateProjectGrant`, and `RemoveProjectGrant`.
  - Members: `ListUserMemberships`, `ListOrgMembers`, `AddOrgMember`, `UpdateOrgMember`, `RemoveOrgMember`, `ListProjectMembers`, `AddProjectMember`, `UpdateProjectMember`, `RemoveProjectMember`, `ListProjectGrantMembers`, `AddProjectGrantMember`, `UpdateProjectGrantMember`, and `RemoveProjectGrantMember`.
  - Instance lifecycle and objects: `GetMyInstance`, `ListInstanceDomains`, `ListInstanceTrustedDomains`, `AddInstanceTrustedDomain`, `RemoveInstanceTrustedDomain`, `GetOrgByID`, `IsOrgUnique`, `GetDefaultOrg`, `ListIAMMembers`, `AddIAMMember`, `UpdateIAMMember`, and `RemoveIAMMember`.

- **ConnectRPC transport for new APIs (4.0.0).** New V2 APIs use gRPC with ConnectRPC exclusively and add no OpenAPI 2.0 endpoints; earlier APIs keep existing transports. ConnectRPC and gRPC-Web requests support CORS.
- **Organization creation contracts (4.0.0).** `AddOrganizationRequest` accepts a caller-supplied unique organization ID, and `AddOrganization()` returns all organization administrators.
- **User self-deletion (4.0.0).** Users can delete their own accounts without an administrator-mediated operation.
- **Trusted-domain sorting (4.0.0).** `ListInstanceTrustedDomains()` adds sorting options.
- **Session expiration filtering (2025-08).** Versions 2.71.16, 3.3.3, and 4.0.1 add an expiration-date filter to List Sessions.
- **OIDC client ID configuration (2025-08).** Versions 3.3.3 and 4.0.1 disable the client ID in OIDC configuration.
- **`ListAppKeys()` result behavior (2025-08).** Version 4.0.2 restores application keys to this result.
- **Project creation permissions (2025-08).** Version 4.0.2 uses the correct project-creation permission.
- **Permission V2 user checks (2025-08).** Version 4.0.2 uses the correct `userID` column.
- **Project-role command permissions (2025-08).** Version 4.0.3 corrects command-layer permission checks for adding, updating, and deleting project roles.
- **Console user API v2 enabled by default (2025-09).** Version 4.1.2 makes `ConsoleUseV2UserApi` the default rather than opt-in.
- **Project creation with members (2025-09).** Version 4.2.0 can create project members as part of project creation.
- **Grant and self-management corrections (2025-09).** Version 4.1.0 fixes same-organization project-grant user grants; 4.1.1 fixes Actions V1 post-creation grant permissions; 4.3.0 fixes metadata and deletion self-management, generated project-grant IDs, and user-grant organization selection.
- **User listing by metadata (2025-09).** Version 4.2.0 adds metadata filters; 4.2.2 and 4.3.0 correct metadata-value comparison and sorting in lists and exports.
- **Requested-audience roles in OIDC userinfo (2025-09).** Version 4.3.0 added a userinfo claim containing roles for all requested audiences.
- **Requested-audience roles claim reverted (2025-10).** Version 4.3.2 removes that 4.3.0 userinfo claim; clients must not depend on it after upgrade.
- **API v2 promotions and beta deprecations (2025-10).** Version 4.5 makes Application and internal Permission V2 GA and deprecates Settings V2 beta and beta endpoints with V2 replacements. Version 4.6 moves Authorization and Instance to V2, makes Project V2 GA, and deprecates Project V2 beta.
- **User-grant queries for multiple users (2025-10).** Version 4.3.1 adds `InUserIDs` to user-grant listing.
- **Organization v2beta permission checks (2025-11).** Version 4.6.3 corrects the Organization V2 beta authorization check.
- **Typed-URL API binding (2025-11).** Version 4.6.5 adds a binding for URLs that include a type.
- **Organization API moves to v2 (2025-11).** Version 4.7.0 replaces Organization V2 beta with V2.
- **User-listing v2 permission upgrade caveat (2025-12).** Versions 3.4.5 and 4.7.2 forced V2 checks but prevented some users listing users; upgrade to at least 3.4.6 or 4.7.4 respectively.
- **Administrator-list filters (2026-01).** Version 4.9.1 implements the missing `ListAdministrators` filters.
- **Organization context on creation (2026-01).** Version 4.10.0 correctly handles `organization_id` on creation requests.
- **Application lookup by protocol identifier (2026-01).** Version 4.10.0 filters applications by OIDC client ID or SAML entity ID.
- **Caller-provided OIDC application IDs (2026-02).** Version 4.11.0 honors the ID supplied in an OIDC application creation request.
- **Allowed-language API data (2026-02).** Version 4.11.0 adds `allowed_languages` to responses.
- **User-update permissions use request data (2026-02).** Versions 4.11.1 and 3.4.7 evaluate authorization from the update request data.
- **Machine-user access-token type (2026-03).** Version 4.12.0 lets callers select the access-token type for a machine user.
- **Metadata APIs and Actions V2 (2026-03).** Version 4.13.0 adds metadata to `CreateUser` and `UpdateUser`; `SetOrganizationMetadata` and `SetUserMetadata` can delete metadata, and Actions V2 can update it through `RetrieveIdentityProviderIntent`.
- **Management API and organization-scope enforcement (2026-03).** Versions 3.4.8 and 4.12.2 fix selected Management API checks and encoded authentication paths; 3.4.9 and 4.12.3 enforce organization scopes.
- **Console API v2 configuration key (2026-04).** Version 4.13.1 restores `ConsoleUseV2UserApi` as the feature key.
- **Console role and Actions V1 permissions (2026-05).** Version 4.15.0 allows administrator-profile role assignment deletion and displays Actions V1 under the correct permissions.
- **Dynamic OIDC client registration and management (2026-08).** Version 4.17.0 implements RFC 7591 registration and RFC 7592 management.
- **Security-settings API route (2026-08).** Version 4.17.0 accepts `SetSecuritySettings` at `/v2/settings/security`.
- **Adjacent user-grant role removal (2026-08).** Version 4.16.0 correctly removes adjacent roles in a single user-grant update.

## Login, sessions, users, MFA, and passkeys

- **Native HTTPS loopback redirects (2025-05).** Native applications may configure `https://` loopback callbacks.
- **Single-use intent tokens (2025-05).** Intent tokens expire and cannot be reused; complete each intent with a fresh, unexpired token.
- **Invite codes for verified email addresses (2025-05).** Versions 3.2.1 and 2.71.11 accept invite codes even when the user's email is already verified.
- **Login v1 auto-linking with suffixed usernames (2025-07).** Version 3.3.1 correctly auto-links users in organizations that suffix usernames.
- **Login v1 organization token context (2025-07).** Version 3.3.1 always places the user's organization into Login V1 token context.
- **Login v1 password reset by email or phone (2025-07).** Version 3.3.1 handles reset after authentication by email address or phone number.
- **Existing passkeys and U2F credentials in the Session API (2025-07).** Version 3.3.1 lets existing credentials satisfy Session API checks.
- **Login V2 default for new customers (4.0.0).** Session-based Login V2 reaches feature parity with V1 and becomes the default for new customers.
- **Initial administrator PAT permission (4.0.0).** The initial administrator PAT includes `IAM_LOGIN_CLIENT`.
- **Authenticated account selection (2025-08).** Versions 2.71.15, 3.4.0, and 4.0.3 restrict the select-account page to previously authenticated users.
- **Case-insensitive login discovery (2025-08).** Version 4.0.2 ignores case when matching login names and email during discovery.
- **Login logout completion (2025-08).** Version 4.0.3 uses `/logout/done` for successful logout and accepts `post_logout_redirect` as the URI parameter.
- **Login V2 integration URLs (2025-09).** Version 4.1.0 makes the V2 feature base URI configurable and adds default templates; 4.2.0 exposes the V2 URL in Console IdP configuration.
- **Login callback, proxy, and development-mode behavior (2025-09).** Version 4.1.0 checks email verification before continuing a callback; 4.2.0 fixes Safari cookies in Development Mode; 4.3.0 derives the correct proxied Login host.
- **Multi-method MFA session validation (2025-09).** Version 4.3.0 evaluates multiple authentication methods when validating MFA sessions.
- **Organization-scoped login and external passkeys (2025-10).** Version 4.3.1 adds organization-domain scoping and external passkey registration; 4.5 scopes IdP auto-linking to the organization.
- **Invite-code delivery and email verification (2025-10).** Version 4.5 sends invite codes only when the user's email is unverified.
- **Bare localhost OIDC redirect URIs (2025-10).** Version 4.5 accepts a localhost callback with no path or explicit port, such as `http://localhost`.
- **Authentication hardening across maintained release lines (2025-10).** Versions 2.71.18, 3.4.3, and 4.6.0 check 2FA even when not enforced, honor lockout during old-password verification, add tar-pit checks, and sanitize host headers.
- **MFA checks ignore unready authentication methods (2025-11).** Versions 2.71.19, 3.4.4, and 4.6.5 exclude incomplete methods from MFA-requirement decisions.
- **Identity-provider login without organization context (2025-11).** Version 4.6.3 falls back to the default organization when creating an IdP user without context; 4.7.0 also discovers organizations for context-free Login flows.
- **Login proxy-header propagation (2025-12).** Version 4.7.1 centralizes Login host resolution and forwards the resolved proxy headers to API calls.
- **Username changes from the 2FA screen (2025-12).** Version 4.7.2 fixes the back button so users can change the username.
- **Login frontend security updates (2025-12).** Version 4.7.5 updates React and Next.js components for CVE-2025-55182, CVE-2025-66478, CVE-2025-55184, and CVE-2025-55183.
- **Login V1 password verification (2025-12).** Version 4.7.6 updates the V1 password-verification behavior.
- **Explicit identity-provider linking from an existing session (2026-01).** Version 4.9.0 can link an IdP explicitly using an existing session ID.
- **Recovery-code MFA (2026-01).** Version 4.9.0 adds recovery codes as an MFA method.
- **Login policy for unknown usernames (2026-01).** Version 4.9.0 fixes `LoginPolicy.IgnoreUnknownUsernames`; 4.9.1 routes to `/password` when `ignoreUnknownUsername` is enabled.
- **Empty custom Login headers (2026-01).** Version 4.9.0 deletes a custom request header when its configured value is empty.
- **Login V1 reauthentication with ID token hints (2026-01).** Version 4.9.1 corrects automatic reauthentication using `id_token_hint`.
- **Generalized code-verification errors (2026-01).** Versions 3.4.6 and 4.9.1 replace specific verification failure text with a generalized message; clients must not branch on the older messages.
- **Password-expiry and password-change behavior (2026-01).** Version 4.10.0 limits V1 expiry checks to local users with passwords and fixes permission and eventual-consistency failures at `/password/change`.
- **Passkey reauthentication (2026-01).** Version 4.10.0 adds passkey reauthentication.
- **SMS OTP country-code selection (2026-01).** Login V1 adds a country selector, but it was missing from the 4.10.0 build; use 4.10.1 or newer.
- **Login local-authentication policy naming (2026-02).** Version 4.11.0 replaces `allowUsernamePassword` with `allowLocalAuthentication`, updates Console wording, and makes Login honor password-complexity settings.
- **Console self-management without explicit roles (2026-02).** Version 4.11.0 restores self-management for users without explicit roles.
- **Automatic email-verification control (2026-02).** Version 4.11.0 allows Login automatic email verification to be disabled.
- **Identity-provider intent data (2026-03).** Version 4.12.0 adds `login_hint` to IdP intents and returns a refresh token in `RetrieveIdentityIntentResponse`.
- **Invite-code lifecycle (2026-03).** Version 4.12.0 permits replacing a still-valid invite code; versions 3.4.8 and 4.12.2 base WebAuthn invite expiry on code creation time.
- **Password reset and session termination (2026-03).** Version 4.12.0 adds current password to reset and terminates sessions after user deletion or deactivation.
- **Identity-provider discovery and registration policy (2026-03).** Version 4.12.0 checks primary methods during user discovery; 4.13.0 removes `loginSettings.allowRegister` from IdP flows.
- **Login invitation and protocol context (2026-04).** Version 4.14.0 sends users without a primary method into invitation, carries OIDC or SAML IDs when resending codes, preserves OIDC context through verification, and prevents duplicate email-code verification.
- **Forced-MFA email-verification fallback (2026-06).** Version 4.15.1 redirects to email verification when MFA is forced but no factors are visible.
- **Registration session retry (2026-06).** Version 4.15.1 retries post-registration session creation after `NotFound`.
- **Passkey registration from identity-provider sessions (2026-06).** Version 4.15.2 accepts IdP sessions when registering a passkey.
- **Verified email required for identity-provider auto-linking (2026-06).** Version 4.15.3 rejects auto-linking when the external email is unverified.
- **Native-application callbacks and passkey links (2026-08).** Version 4.16.0 restores native custom protocol schemes; 4.17.0 adds native-app passkey links.
- **User-verified passkeys satisfy MFA (2026-08).** Version 4.17.0 treats a user-verified passkey as fulfilling MFA in session-validity checks.
- **Authentication-method enrollment hardening (2026-08).** Versions 4.16.2 and 3.4.14 require authentication before WebAuthn/U2F and TOTP/OTP enrollment; 4.17.1 and 3.4.15 add passkey-code permission checks and require the MFA prompt before 2FA enrollment.
- **Browser OTP code delivery (2026-08).** Version 4.17.1 prevents browser Login from requesting OTP codes via `returnCode`.
- **Deactivated-organization enforcement in Login V2 (2026-08).** Version 4.17.1 blocks authentication for users in deactivated organizations.
- **External-identity-provider login hardening (2026-08).** Versions 4.16.2 and 3.4.14 prevent account pre-hijacking in federated Login V1.
- **Identity-provider users without name fields (2026-08).** Version 4.16.0 allows automatic IdP user creation even when upstream name fields are missing.
- **OIDC login-hint handling (2026-08).** Version 4.16.0 preserves the correct `oidc_` request ID through `prompt=login` with `login_hint`; 4.17.0 honors the hint without an auto-submit loop.
- **Invite-code recovery and generation (2026-08).** Version 4.16.0 adds invite codes to secret generators; 4.17.0 permits invite codes after all authentication methods are removed.

## OIDC, OAuth, SAML, identity providers, and token security

- **SAML application login UI selection (2025-05).** Console can select the Login implementation per SAML application.
- **Logout integration support (2025-05).** V3.0 adds OIDC back-channel logout for custom Login UIs, and V3.2 adds federated logout for SAML IdPs.
- **LDAP user-filter combination (2025-05).** Versions 3.1.0 and 2.71.11 correctly OR-join multiple user filters, which can change compound-filter matches.
- **Proxy protocol validation and HTTPS enforcement (2025-05).** Versions 2.70.12, 2.71.11, and 3.2.2 validate scheme headers and enforce HTTPS; proxies must forward the correct protocol.
- **JWT identity-provider intents (2025-06).** Version 3.3.0 lets JWT providers participate in the IdP intent lifecycle.
- **OIDC logout hints (4.0.0).** The end-session endpoint accepts `logout_hint`.
- **Typed SAML identity-provider intent data (4.0.0).** IdP intents return typed SAML form-post data.
- **SAML authentication milestone (4.0.0).** Successful SAML application authentication records `AuthenticationSucceededOnApplication` on the session.
- **SAML responses without a NameID (2025-08).** Versions 3.3.3 and 4.0.1 use the transient mapping attribute when `NameID` is absent.
- **Case-insensitive identity-provider external IDs (2025-08).** Versions 3.3.6 and 4.0.2 compare external IDs without case sensitivity.
- **Entra ID intent user information (2025-08).** Version 4.0.3 correctly unmarshals Entra user data from IdP intents.
- **Configurable SAML identity-provider signatures (2025-09).** Version 4.1.0 adds `SignatureMethod`; 4.3.0 fixes signature-algorithm handling.
- **Invalid OIDC ID token hints are ignored (2025-09).** Versions 3.4.2 and 4.1.4 ignore an invalid `id_token_hint` rather than reject the flow.
- **Identity-provider flow routing and callbacks (2025-10).** Version 4.3.1 enters the IdP flow when password authentication is disabled; 4.5 adds fallback and `postError`; 4.6.1 fixes the success URL.
- **GitHub identity-provider email fallback (2025-10).** Version 4.3.1 queries GitHub email data separately when the profile email is empty.
- **LDAP identifier character support (2025-10).** Version 4.4 permits non-ASCII bind DNs; 4.5 permits special characters in LDAP sign-in identifiers.
- **SAML service-provider certificate Common Name (2025-10).** Version 4.5 adds a Common Name to the SP certificate.
- **Identity-provider linking conditions are validated (2025-11).** Versions 2.71.19, 3.4.4, and 4.6.6 enforce configured account-linking conditions.
- **External identity-provider user updates (2025-11).** Version 4.6.5 restores user-information updates after external authentication.
- **Client-credentials ID token lifetime (2026-01).** Version 4.9.0 adds lifetime information to client-credentials ID tokens.
- **SAML POST flow cookie limits (2026-02).** Version 4.11.0 bypasses Login cookie limits in SAML POST and fixes SP POST handling.
- **Token exchange and back-channel logout graduate (2026-02).** Version 4.11.0 makes token exchange and back-channel logout GA, and Console can manage the back-channel logout URI.
- **Token V2 subject validation (2026-02).** Versions 4.11.0 and 3.4.7 require the Token V2 subject to match the user ID.
- **Certificate and public-key authentication (2026-04).** Version 4.14.0 supports X.509 certificates for System API user tokens and ECDSA and ED25519 public keys.
- **Gateway and OIDC hardening (2026-04).** Version 4.14.0 raises gRPC `MaxSendMsgSize`, returns HTTP 401 for unauthenticated V1 gateway errors, fixes invalid JWT-assertion errors, encrypts opaque OIDC tokens with authenticated encryption, and propagates non-`NotFound` interceptor errors.
- **JWT identity-provider claim validation (2026-06).** Versions 3.4.12 and 4.15.2 always validate JWT IdP `exp`, `iat`, and managed audience values.
- **OAuth client binding during token use (2026-06).** Versions 3.4.12 and 4.15.2 verify `client_id` during authorization-code and refresh-token use.
- **PKCE for external OAuth and OIDC providers (2026-06).** Version 4.15.2 applies PKCE when constructing external OAuth and OIDC providers.
- **Protected outbound HTTP connections (2026-06).** Version 4.15.2 uses the protected HTTP client for outbound connections.
- **LDAP username-filter escaping (2026-05).** Versions 3.4.10 and 4.15.0 escape usernames before embedding them in LDAP filters so user input cannot become filter syntax.
- **Token-exchange client and scope validation (2026-06).** Version 4.15.3 validates the client and requested scopes during exchange.
- **OIDC and SAML failure redirect handling (2026-06).** Version 4.15.3 guards missing `defaultRedirectUri` in `FailedPrecondition` paths.
- **ZITADEL as an identity provider (2026-08).** Version 4.17.0 adds ZITADEL as an external IdP with CRUD, intent start/retrieval, Login V1 presentation, active-provider listing, and instance-role synchronization.

## Actions, SCIM, metadata, and outbound providers

- **SCIM email type attribute (2025-07).** Version 3.3.1 adds `type` to `ScimEmail`.
- **Actions V2 context and ordering (4.0.0).** Context includes `clientID`; action lists default to creation date; execution ordering uses IDs.
- **SCIM create-password handling (4.0.0).** SCIM metadata can ignore a random password supplied during user creation.
- **User information in action metadata context (2025-08).** Version 4.0.1 adds user information when an Action sets metadata.
- **Actions V2 execution input (2025-09).** Versions 3.4.2 and 4.1.3 restore `event_payload` for event executions; 4.2.0 forwards request headers.
- **HTTP-provider signing keys (2025-09).** Version 4.2.0 adds signing keys to HTTP providers.
- **Actions V1 organization metadata (2025-11).** Version 4.6.4 restores organization metadata to V1 Actions.
- **Actions V2 `all` condition execution (2025-12).** Version 4.7.1 correctly runs request and response executions whose condition is `all`.
- **JWT and JWE payload types for Actions V2 (2025-12).** Version 4.8.0 adds signed JWT and encrypted JWE target payloads.
- **Actions target-URL denylist (2026-02).** Version 4.11.1 can reject Action targets covered by the URL denylist.
- **Actions metadata and actor context (2026-08).** Version 4.17.0 adds `appendMetadataRaw`, and userinfo Actions receive actor information.
- **Legacy Actions filesystem isolation (2026-08).** Versions 4.16.1 and 3.4.13 prevent embedded Actions from importing server filesystem paths through `require`.

## Console, Login presentation, localization, and notification delivery

- **Restricted-language settings (2025-06).** Versions 2.70.13, 2.71.12, and 3.2.3 fix setting restricted languages.
- **Hosted-login localization (4.0.0).** A translation API is available, and hosted Login adds Turkish.
- **Web Keys enabled by default on version 3 (2025-09).** Version 3.4.1 enables the feature by default.
- **Login frontend theming and localization (2025-10).** Version 4.4 adds the theme system and translations; 4.5 adds Japanese.
- **Dual-stack Login frontend (2025-10).** Version 4.4 serves Login over IPv4 and IPv6.
- **Feature flags through environment variables (2025-11).** Version 4.6.5 accepts feature flags from environment configuration.
- **Console framework configuration (2025-11).** Version 4.6.5 adds missing framework choices during application creation.
- **SMTPUTF8 addresses and passwordless SMTP configuration (2026-01).** Version 4.8.1 accepts SMTPUTF8 addresses; 4.9.1 permits SMTP without a password.
- **Additional locales (2026-01).** Version 4.9.0 adds Ukrainian, French, and Dutch; 4.10.0 adds Arabic.
- **SMTP OAuth and unauthenticated configurations (2026-02).** Version 4.11.0 adds XOAUTH/XOAuth2 and Console support. SMTP testing works without auth, and the gRPC response reports auth `none` with scopes.
- **Login deployment and routing behavior (2026-03).** Version 4.12.0 resolves Login CSP `img-src` at build time, derives languages from settings, and adds multi-domain redirects; 4.13.0 honors `ui_locales`.
- **Login service credentials and TLS (2026-03).** Version 4.12.0 supports `LOGIN_SERVICE_KEY_FILE`, optional TLS termination, and the OpenSSL CA store; 4.13.0 can take a private-key file from environment configuration.

  ```sh
  LOGIN_SERVICE_KEY_FILE=/path/to/service-key
  ```

- **Login trust, key, and startup configuration (2026-04).** Version 4.14.0 loads `SSL_CERT_DIR` certificates without hashed filenames, accepts PKCS#1 Login client keys, and adds `ZITADEL_API_AWAITINITIALCONN`.
- **Console configuration corrections (2026-04).** Version 4.14.0 always shows Settings to administrators, prevents duplicate SMTP setup, fixes JWT-provider callback URLs, and normalizes empty OIDC redirect updates.
- **Login presentation (2026-04).** Version 4.14.0 adds Portuguese and makes theme toggling honor branding `themeMode`, including the CSP fix.
- **Localized signup legal links (2026-05).** Version 4.15.0 resolves localized legal links correctly.
- **Login proxy custom headers (2026-06).** Version 4.15.1 applies environment-configured request headers while proxying.
- **Login custom branding fonts (2026-06).** Version 4.15.2 loads the branding font and permits it in Login CSP.

## Telemetry, service reporting, and runtime observability

- **Telemetry controls (2025-05).** Version 3.0 makes the metrics and tracing service name configurable and exposes Prometheus metrics from projection handlers.
- **River queue OpenTelemetry metrics (2025-07).** Version 3.3.1 includes River queue activity in OpenTelemetry collection.
- **Opt-out Service Ping (4.0.0).** Service Ping sends anonymized instance metrics and usage to the customer portal unless disabled; this release fixes its endpoint and validates and randomizes its default interval.
- **OpenTelemetry metric scope metadata (2025-08).** Versions 2.71.15, 3.3.6, and 4.0.2 stop adding default scope information, so collectors must not require it.
- **Expanded Service Ping reporting (2025-09).** Version 4.2.0 adds resource counts; 4.2.1 logs report-body sizes.
- **Corrected River metric units (2025-09).** Versions 2.71.17, 3.4.2, and 4.1.0 correct River units, potentially changing dashboard and alert interpretation.
- **Corrected gRPC status-code metrics (2025-10).** Version 4.6.0 fixes outcome mapping in `grpc_server_grpc_status_code_total`.
- **ConnectRPC tracing (2025-12).** Version 4.7.2 adds the tracing interceptor to ConnectRPC services.
- **Cross-application tracing for API v2 (2026-02).** Version 4.11.0 enables distributed tracing across V2 applications.
- **Log streams and GCP error reporting (2026-02).** Version 4.11.0 adds log streams and GCP Error Reporting; 4.11.1 fixes the setup stream and masks grouped structured-log attributes.
- **Login readiness and push-based OpenTelemetry (2026-03).** Version 4.13.0 adds Login readiness and push logs, metrics, and traces; resources use the configured service name.
- **Standard OpenTelemetry environment variables (2026-04).** Version 4.14.0 supports standard variables through autoexport.
- **HTTP metric route labels (2026-08).** Version 4.16.3 records route patterns rather than individual paths, reducing label cardinality and changing dashboard assumptions.
