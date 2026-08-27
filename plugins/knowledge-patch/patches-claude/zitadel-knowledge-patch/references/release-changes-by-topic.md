# Release changes by topic

This reference organizes maintenance and release changes by the work they affect. Batch IDs are included inline for compatibility decisions.

## Upgrade boundaries and deprecations

- **License assessment (2025-05).** The repository changes from Apache 2.0 to AGPLv3 with version 3; assess licensing before upgrading.
- **PostgreSQL-only storage (2025-05).** CockroachDB support ends in version 3. Migrate to PostgreSQL with `mirror`; do not upgrade CockroachDB in place.
- **Required maintenance advisory (2025-05).** Before 2.65.10, 2.70.12, 2.71.11, or 3.2.2, follow [technical advisory 10016](https://zitadel.com/docs/support/advisory/a10016).
- **Decimal mirror values (2025-06).** Releases 2.66.18, 2.67.15, 2.68.11, and 2.69.11 correct mirror with decimal event-store values and also require advisory 10016.
- **Resource-based API milestone (4.0.0).** Version 4 completes migration of core instance, organization, project, application, and user resources. Actions V2 and Caches V2 are GA; Instance V2, Project V2, App V2, Authorization V2, Permission V2, and Settings V3 remain beta at this milestone.
- **V1 operation deprecations (4.0.0).** Replace these with resource-based APIs:
  - Organization/users: `GetOrgByDomainGlobal`, `AddMachineUser`, `UpdateMachine`, `GenerateMachineSecret`, `RemoveMachineSecret`, `GetMachineKeyByIDs`, `ListMachineKeys`, `AddMachineKey`, `RemoveMachineKey`, `UpdateUserName`, `SetUserMetadata`, `BulkSetUserMetadata`, `ListUserMetadata`, `GetUserMetadata`, `RemoveUserMetadata`, `BulkRemoveUserMetadata`, `UpdateHumanPhone`, `GetPersonalAccessTokenByIDs`, `ListPersonalAccessTokens`, `AddPersonalAccessToken`, `RemovePersonalAccessToken`, and `ListAppKeys`.
  - Projects: `GetProjectByID`, `GetGrantedProjectByID`, `ListProjects`, `ListGrantedProjects`, `ListGrantedProjectRoles`, `AddProject`, `UpdateProject`, `DeactivateProject`, `ReactivateProject`, `RemoveProject`, `ListProjectRoles`, `AddProjectRole`, `BulkAddProjectRoles`, `UpdateProjectRole`, `RemoveProjectRole`, `GetProjectGrantByID`, `ListProjectGrants`, `ListAllProjectGrants`, `AddProjectGrant`, `UpdateProjectGrant`, `DeactivateProjectGrant`, `ReactivateProjectGrant`, and `RemoveProjectGrant`.
  - Members: `ListUserMemberships`, `ListOrgMembers`, `AddOrgMember`, `UpdateOrgMember`, `RemoveOrgMember`, `ListProjectMembers`, `AddProjectMember`, `UpdateProjectMember`, `RemoveProjectMember`, `ListProjectGrantMembers`, `AddProjectGrantMember`, `UpdateProjectGrantMember`, and `RemoveProjectGrantMember`.
  - Instance: `GetMyInstance`, `ListInstanceDomains`, `ListInstanceTrustedDomains`, `AddInstanceTrustedDomain`, `RemoveInstanceTrustedDomain`, `GetOrgByID`, `IsOrgUnique`, `GetDefaultOrg`, `ListIAMMembers`, `AddIAMMember`, `UpdateIAMMember`, and `RemoveIAMMember`.
- **New API transport (4.0.0).** New V2 APIs use gRPC plus ConnectRPC exclusively and add no OpenAPI 2.0 endpoints; older APIs retain their transports. ConnectRPC and gRPC-Web support CORS.
- **API promotions (2025-10).** Version 4.5 promotes Application and internal Permission from v2beta to V2 GA and deprecates Settings v2beta plus beta endpoints with V2 replacements. Version 4.6 moves Authorization and Instance to V2, promotes Project to GA, and deprecates Project v2beta.
- **Organization API promotion (2025-11).** Version 4.7.0 moves Organization from v2beta to V2; migrate beta clients.

## Security and authorization corrections

- **System-user checks (2025-05).** The new authorization framework supports system users, so their operations participate in permission checks.
- **Proxy scheme enforcement (2025-05).** Releases 2.70.12, 2.71.11, and 3.2.2 validate the protocol header and enforce HTTPS; proxies must forward the correct scheme.
- **Session API permissions (2025-07).** Releases 2.70.14, 2.71.13, and 3.3.2 correct Session API permission checks.
- **Project creation permission (2025-08).** Version 4.0.2 uses the correct permission when creating projects.
- **Permission V2 user lookup (2025-08).** Version 4.0.2 checks the correct `userID` column.
- **Project-role commands (2025-08).** Version 4.0.3 corrects permission checks for add, update, and delete project-role commands.
- **Grant and self-management permissions (2025-09).** Version 4.1.0 fixes same-organization project-grant user grants; 4.1.1 fixes Actions V1 post-creation grant permissions; 4.3.0 corrects user metadata/deletion self-management, generated project-grant IDs, and the organization used by grant queries.
- **Authentication hardening (2025-10).** Releases 2.71.18, 3.4.3, and 4.6.0 check 2FA even when optional, honor lockout during old-password verification, add tar-pit checks, and sanitize host headers.
- **Organization v2beta authorization (2025-11).** Version 4.6.3 corrects the service's permission check.
- **User-listing upgrade caveat (2025-12).** Versions 3.4.5 and 4.7.2 force V2 user-list permissions but can prevent some listings; use at least 3.4.6 or 4.7.4 respectively.
- **Generalized verification errors (2026-01).** Versions 3.4.6 and 4.9.1 stop exposing earlier specific code-verification messages; clients must not branch on them.
- **User-update request authorization (2026-02).** Versions 4.11.1 and 3.4.7 evaluate permission from request data.
- **Token V2 subject validation (2026-02).** Versions 4.11.0 and 3.4.7 compare token subject with user ID.
- **Management scope enforcement (2026-03).** Versions 3.4.8 and 4.12.2 fix Management permissions and encoded-path handling; 3.4.9 and 4.12.3 enforce organization scopes.
- **Gateway and token hardening (2026-04).** Version 4.14.0 raises gRPC `MaxSendMsgSize`, maps unauthenticated V1 gateway errors to HTTP 401, corrects invalid JWT-assertion errors, encrypts opaque OIDC tokens with authenticated encryption, and propagates interceptor errors other than `NotFound`.
- **LDAP filter injection defense (2026-05).** Versions 3.4.10 and 4.15.0 escape usernames embedded in LDAP filters.
- **JWT IdP validation (2026-06).** Versions 3.4.12 and 4.15.2 always validate `exp`, `iat`, issuer/signature, and managed audience for JWT identity providers.
- **OAuth client binding (2026-06).** Versions 3.4.12 and 4.15.2 verify `client_id` during authorization-code exchange and refresh.
- **Protected outbound HTTP (2026-06).** Version 4.15.2 routes outgoing connections through the protected client.
- **Token-exchange validation (2026-06).** Version 4.15.3 validates client and scopes.
- **Verified-email auto-linking (2026-06).** Version 4.15.3 requires a verified external email before automatic account linking.
- **FIPS runtime (2026-08).** Version 4.16.0 adds a FIPS 140-3-compliant build and runtime checks.
- **Enrollment authorization (2026-08).** Versions 4.16.2/3.4.14 require authentication before WebAuthn/U2F and TOTP/OTP enrollment; 4.17.1/3.4.15 add passkey-code permission checks and require the MFA prompt before 2FA enrollment.
- **External IdP pre-hijacking defense (2026-08).** Versions 4.16.2 and 3.4.14 harden Login V1; federated deployments should use those lines or newer.
- **Legacy Action isolation (2026-08).** Versions 4.16.1 and 3.4.13 prevent embedded Actions from accessing server files via `require`.

## API and protocol behavior

- **Native HTTPS loopbacks (2025-05).** Native applications may configure `https://` loopback redirects.
- **Logout integration (2025-05).** Version 3.0 enables OIDC back-channel logout for custom Login, and 3.2 adds federated logout for SAML IdPs.
- **Organization context in V2 user creation (2025-06).** Version 3.3.0 makes Console creation use the selected organization.
- **Login V1 token context (2025-07).** Version 3.3.1 always includes the user's organization in token processing context.
- **OIDC logout hints (4.0.0).** `end_session_endpoint` accepts `logout_hint`.
- **SAML application milestone (4.0.0).** Successful SAML app authentication records `AuthenticationSucceededOnApplication` on the session.
- **Session expiry queries (2025-08).** Versions 2.71.16, 3.3.3, and 4.0.1 add an expiration-date filter to List Sessions.
- **OIDC client-ID configuration (2025-08).** Versions 3.3.3 and 4.0.1 disable the client ID in OIDC configuration.
- **Backslash query escaping (2025-08).** Versions 3.4.0 and 4.0.3 correctly escape backslashes.
- **`ListAppKeys()` restoration (2025-08).** Version 4.0.2 returns application keys again.
- **Invalid ID-token hints (2025-09).** Versions 3.4.2 and 4.1.4 ignore invalid `id_token_hint` instead of rejecting the flow.
- **Requested-audience userinfo claim (2025-09, 2025-10).** Version 4.3.0 added roles for all requested audiences, but 4.3.2 removed that claim. Clients on later releases must not rely on it.
- **Multiple-user grant query (2025-10).** Version 4.3.1 adds `InUserIDs` to list grants for several users.
- **Bare localhost redirect (2025-10).** Version 4.5 accepts `http://localhost` without a path or explicit port.
- **Typed URL binding (2025-11).** Version 4.6.5 adds an API binding for URLs that include a type.
- **ConnectRPC tracing (2025-12).** Version 4.7.2 adds the tracing interceptor.
- **Client-credentials ID-token lifetime (2026-01).** Version 4.9.0 gives those ID tokens lifetime information.
- **Creation organization context (2026-01).** Version 4.10.0 correctly handles `organization_id` on creation requests.
- **Protocol-ID application lookup (2026-01).** Version 4.10.0 filters applications by OIDC client ID or SAML entity ID.
- **Caller-provided OIDC app IDs (2026-02).** Version 4.11.0 preserves the requested ID.
- **Token exchange and back-channel logout GA (2026-02).** Version 4.11.0 graduates both and lets Console manage the back-channel logout URI.
- **Cross-application V2 tracing (2026-02).** Version 4.11.0 connects distributed traces across applications.
- **Machine access-token type (2026-03).** Version 4.12.0 lets the API select a machine user's token type.
- **Certificate/public-key authentication (2026-04).** Version 4.14.0 supports X.509 system-user tokens plus ECDSA and ED25519 public keys.
- **Dynamic OIDC registration (2026-08).** Version 4.17.0 implements RFC 7591 registration and RFC 7592 management.
- **Security settings route (2026-08).** Version 4.17.0 accepts `SetSecuritySettings` at `/v2/settings/security`.

## Login, sessions, and authentication

- **Selectable SAML Login UI (2025-05).** Console can select the Login implementation per SAML application.
- **Single-use intent tokens (2025-05).** Intent tokens expire and cannot be reused; complete each flow with a fresh token.
- **Verified-address invite codes (2025-05).** Versions 3.2.1 and 2.71.11 accept invite codes even when email is already verified.
- **Login V1 suffixed-name auto-linking (2025-07).** Version 3.3.1 correctly links users in organizations with suffixed usernames.
- **Password reset by alternate login (2025-07).** Version 3.3.1 handles resets when the user signs in with email or phone.
- **Existing WebAuthn credentials in sessions (2025-07).** Version 3.3.1 lets Session API use existing passkeys and U2F credentials.
- **Login V2 default (4.0.0).** Session-based Login V2 reaches V1 feature parity and becomes the default for new customers.
- **Hosted Login localization (4.0.0).** A translation API is available and Turkish is added.
- **Initial administrator Login permission (4.0.0).** Its PAT includes `IAM_LOGIN_CLIENT`.
- **Authenticated account selection (2025-08).** Versions 2.71.15, 3.4.0, and 4.0.3 show only previously authenticated users on select-account.
- **Case-insensitive discovery (2025-08).** Version 4.0.2 ignores case when matching login names and emails.
- **Logout completion (2025-08).** Version 4.0.3 uses `/logout/done` and accepts `post_logout_redirect`.
- **Login integration URLs (2025-09).** Version 4.1.0 configures the feature base URI and default templates; 4.2.0 exposes Login V2 URL in IdP Console configuration.
- **Callback, proxy, and Development Mode (2025-09).** Version 4.1.0 verifies email before callback, 4.2.0 fixes Safari cookies in Development Mode, and 4.3.0 derives the correct proxied host.
- **Multi-method MFA validation (2025-09).** Version 4.3.0 accounts for several authentication methods in session validation.
- **Organization-scoped Login and external passkeys (2025-10).** Version 4.3.1 adds organization-domain scope plus external passkey registration; version 4.5 scopes IdP auto-linking by organization.
- **Login theme and languages (2025-10).** Version 4.4 introduces broad themes and translations; 4.5 adds Japanese.
- **Dual-stack Login (2025-10).** Version 4.4 listens over IPv4 and IPv6.
- **Invite delivery rule (2025-10).** Version 4.5 sends invite codes only when the user's email is unverified.
- **Unready MFA methods (2025-11).** Versions 2.71.19, 3.4.4, and 4.6.5 ignore methods that are not ready when deciding MFA requirements.
- **IdP login without organization context (2025-11).** Version 4.6.3 falls back to the default organization for creation; 4.7.0 adds organization discovery.
- **Proxy-header propagation (2025-12).** Version 4.7.1 centralizes host resolution and forwards resolved headers to Login API calls.
- **Change username from 2FA screen (2025-12).** Version 4.7.2 fixes the back button.
- **Login frontend CVEs (2025-12).** Version 4.7.5 updates React/Next.js components for CVE-2025-55182, CVE-2025-66478, CVE-2025-55184, and CVE-2025-55183.
- **Login V1 password verification (2025-12).** Version 4.7.6 changes its password-verification handling; test deployments that retain this path.
- **Explicit IdP linking (2026-01).** Version 4.9.0 links a provider from an existing session ID.
- **Recovery-code MFA (2026-01).** Version 4.9.0 adds recovery codes.
- **Unknown-username policy (2026-01).** Version 4.9.0 fixes `LoginPolicy.IgnoreUnknownUsernames`; 4.9.1 routes to `/password` when enabled.
- **Empty custom headers (2026-01).** Version 4.9.0 deletes rather than preserves a header whose configured value is empty.
- **Additional locales (2026-01).** Version 4.9.0 adds Ukrainian, French, and Dutch; 4.10.0 adds Arabic.
- **Login V1 reauthentication (2026-01).** Version 4.9.1 corrects automatic reauthentication with `id_token_hint`.
- **Password expiry/change (2026-01).** Version 4.10.0 limits V1 expiry checks to local password users and fixes permission/eventual-consistency failures on `/password/change`.
- **Passkey reauthentication (2026-01).** Version 4.10.0 adds it to Login.
- **SMS OTP country selector (2026-01).** The feature missed the 4.10.0 build; use 4.10.1 or newer.
- **Local authentication naming (2026-02).** Version 4.11.0 replaces `allowUsernamePassword` with `allowLocalAuthentication`, updates Console wording, and applies password-complexity settings.
- **SAML POST cookie limits (2026-02).** Version 4.11.0 bypasses cookie limits and fixes service-provider POST handling.
- **Automatic email-verification control (2026-02).** Version 4.11.0 can disable automatic verification.
- **IdP intent fields (2026-03).** Version 4.12.0 adds `login_hint` and returns a refresh token from `RetrieveIdentityIntentResponse`.
- **Invite lifecycle (2026-03).** Version 4.12.0 allows a new invite while the prior code is valid; 3.4.8/4.12.2 base WebAuthn invite expiry on creation time.
- **Password reset and session termination (2026-03).** Version 4.12.0 adds current password to reset and terminates sessions after deletion or deactivation.
- **Login deployment behavior (2026-03).** Version 4.12.0 resolves CSP `img-src` at build time, derives languages from settings, and adds multi-domain redirects; 4.13.0 honors `ui_locales`.
- **IdP discovery/registration policy (2026-03).** Version 4.12.0 checks primary methods during discovery; 4.13.0 removes `loginSettings.allowRegister` from IdP flows.
- **Recovery-code activation at setup (2026-04).** Version 4.13.1 activates a recovery code immediately when added.
- **Invitation and protocol context (2026-04).** Version 4.14.0 routes users without a primary method into invitation, preserves OIDC/SAML IDs during resends and verification, and prevents duplicate code verification.
- **Login presentation (2026-04).** Version 4.14.0 adds Portuguese and makes theme toggle honor branding `themeMode`, with a CSP correction.
- **Localized legal links (2026-05).** Version 4.15.0 resolves signup legal links correctly.
- **Proxy custom headers (2026-06).** Version 4.15.1 applies environment-configured headers to proxied API calls.
- **Forced-MFA fallback (2026-06).** Version 4.15.1 redirects to email verification when no factors are visible.
- **Registration retry (2026-06).** Version 4.15.1 retries session creation after registration on `NotFound`.
- **IdP-session passkey registration (2026-06).** Version 4.15.2 accepts externally authenticated sessions.
- **Branding fonts (2026-06).** Version 4.15.2 loads the configured font and permits it in Login CSP.
- **Native callbacks and passkey links (2026-08).** Version 4.16.0 restores native custom schemes; 4.17.0 adds native-app passkey links.
- **User-verified passkeys as MFA (2026-08).** Version 4.17.0 counts them during session-validity checks.
- **Browser OTP delivery (2026-08).** Version 4.17.1 prevents browser Login from obtaining OTP through `returnCode`.
- **Deactivated organizations (2026-08).** Version 4.17.1 blocks Login V2 for their users.
- **Users without upstream names (2026-08).** Version 4.16.0 allows automatic IdP user creation despite missing name fields.
- **OIDC login hints (2026-08).** Version 4.16.0 preserves the `oidc_` request ID with `prompt=login`; 4.17.0 prevents a `login_hint` auto-submit loop.
- **Invite recovery (2026-08).** Version 4.16.0 adds invite-code secret generation; 4.17.0 permits codes after all authentication methods are removed.

## Identity providers and federation

- **LDAP filter composition (2025-05).** Versions 3.1.0 and 2.71.11 correctly OR-join multiple user filters, changing compound-filter matches.
- **JWT IdP intents (2025-06).** Version 3.3.0 brings JWT providers into the intent lifecycle.
- **Typed SAML intent data (4.0.0).** Intent retrieval returns typed SAML form-post data.
- **SAML response without `NameID` (2025-08).** Versions 3.3.3 and 4.0.1 use the transient mapping attribute.
- **Case-insensitive external IDs (2025-08).** Versions 3.3.6 and 4.0.2 compare them without case sensitivity.
- **Entra intent user info (2025-08).** Version 4.0.3 correctly unmarshals it.
- **SAML signature configuration (2025-09).** Version 4.1.0 adds `SignatureMethod`; 4.3.0 fixes signature-algorithm handling.
- **IdP routing and callbacks (2025-10).** Version 4.3.1 jumps directly to IdP when passwords are disabled; 4.5 adds fallback and `postError`; 4.6.1 corrects success URL.
- **GitHub email fallback (2025-10).** Version 4.3.1 queries the email API when profile email is empty.
- **LDAP identifier characters (2025-10).** Version 4.4 supports non-ASCII bind DNs; 4.5 accepts special characters in sign-in identifiers.
- **SAML SP certificate Common Name (2025-10).** Version 4.5 adds one; integrations inspecting certificates should account for it.
- **Link-condition validation (2025-11).** Versions 2.71.19, 3.4.4, and 4.6.6 enforce configured linking conditions.
- **External user updates (2025-11).** Version 4.6.5 restores local user-information updates after external authentication.
- **PKCE for external providers (2026-06).** Version 4.15.2 applies PKCE when building OAuth and OIDC IdPs.
- **ZITADEL provider type (2026-08).** Version 4.17.0 adds ZITADEL as an IdP, CRUD and intent APIs, Login V1 selection, active-provider listing, and instance-role synchronization.

## Actions changes

- **Actions management transition (2025-05).** Console and beta API V2 replace removed V3 alpha requests. V2 adds functions, no longer needs a feature flag, and exposes refresh token in post-auth context.
- **Actions V2 context and ordering (4.0.0).** Context includes `clientID`; lists default to creation date and executions order by IDs.
- **Metadata context user info (2025-08).** Version 4.0.1 includes user information when an Action sets metadata.
- **Execution input (2025-09).** Versions 3.4.2/4.1.3 restore `event_payload`; 4.2.0 propagates request headers.
- **V1 organization metadata (2025-11).** Version 4.6.4 restores it.
- **`all` conditions (2025-12).** Version 4.7.1 correctly executes request/response V2 conditions set to `all`.
- **JWT and JWE targets (2025-12).** Version 4.8.0 adds these payload types.
- **Target URL denylist (2026-02).** Version 4.11.1 lets configurations reject covered target URLs.
- **Metadata mutation (2026-03).** Version 4.13.0 lets Actions V2 update metadata through `RetrieveIdentityProviderIntent`; user APIs add metadata create/update/delete behavior.
- **Console V1 visibility (2026-05).** Version 4.15.0 displays Actions V1 with correct permissions.
- **Raw metadata and actor context (2026-08).** Version 4.17.0 adds `appendMetadataRaw` and gives userinfo Actions actor information.

## Users, organizations, projects, and Console

- **Console V2 feature flag (2025-05).** Console can use V2 for human creation and session listing behind a flag and can manage all available flags.
- **Web Keys transition (2025-05).** Console and beta V2 replace removed V3 alpha operations; instance defaults can generate keys.
- **Restricted languages (2025-06).** Releases 2.70.13, 2.71.12, and 3.2.3 correct language restriction settings.
- **SCIM email type (2025-07).** Version 3.3.1 adds `type` to `ScimEmail`.
- **Organization creation contracts (4.0.0).** `AddOrganizationRequest` accepts a unique caller-supplied ID, and `AddOrganization()` returns every administrator.
- **SCIM random-password handling (4.0.0).** A metadata setting can ignore a random creation password.
- **User self-deletion (4.0.0).** Self-service clients can offer account deletion.
- **Generated Web Keys setup (2025-08).** Version 3.4.0 adds a setup step for Web Key initialization.
- **Console V2 user API default (2025-09).** Version 4.1.2 enables `ConsoleUseV2UserApi` by default.
- **Web Keys default on V3 (2025-09).** Version 3.4.1 enables the feature by default.
- **Create projects with members (2025-09).** Version 4.2.0 adds the option.
- **Metadata user listing (2025-09).** Version 4.2.0 adds filtering; 4.2.2 and 4.3.0 fix comparison and sorting for list/export.
- **Console app framework configuration (2025-11).** Version 4.6.5 restores missing framework choices during creation.
- **Feature flags from environment (2025-11).** Version 4.6.5 accepts environment configuration.
- **Membership-role synchronization (2025-12).** Version 4.7.3 syncs from projections; 4.7.4 fixes its setup execution check.
- **Administrator list filters (2026-01).** Version 4.9.1 implements previously missing filters.
- **Console self-management (2026-02).** Version 4.11.0 restores it for users without explicit roles.
- **Allowed language responses (2026-02).** Version 4.11.0 adds `allowed_languages` to API responses.
- **User metadata APIs (2026-03).** Version 4.13.0 adds metadata to create/update; `SetOrganizationMetadata` and `SetUserMetadata` can delete.
- **Console V2 config key (2026-04).** Version 4.13.1 restores `ConsoleUseV2UserApi`.
- **Console corrections (2026-04).** Version 4.14.0 always shows administrators Settings, prevents duplicate SMTP creation, fixes JWT-provider callback URLs, and normalizes empty OIDC redirect updates.
- **Role assignment deletion (2026-05).** Version 4.15.0 allows deletion from an administrator profile.
- **Adjacent grant roles (2026-08).** Version 4.16.0 correctly removes consecutive roles in one update.

## Email and notification providers

- **SMTPUTF8 and passwordless SMTP (2026-01).** Version 4.8.1 accepts SMTPUTF8; 4.9.1 allows a configuration without a password.
- **SMTP OAuth and unauthenticated mode (2026-02).** Version 4.11.0 adds XOAUTH/XOAuth2 in Console; tests can run without auth, and gRPC reports auth `none` with scopes.
- **HTTP-provider signing keys (2025-09).** Version 4.2.0 adds them.

## Setup, storage, projections, and migration

- **Mirror repeatability and scope (2025-05).** Mirror adds maximum auth-request age, works across repeat runs, includes fields in mirror projections, and skips notification projections.
- **Cross-instance cache isolation (2025-06).** Versions 2.70.13, 2.71.12, and 3.2.3 prevent organization-cache overwrite between instances.
- **Interrupted setup cleanup (4.0.0).** Failed steps are cleaned up when setup is killed.
- **Import/export deactivation state (4.0.0).** Deactivated users and organizations remain deactivated after export/import.
- **Trusted-domain sorting (4.0.0).** `ListInstanceTrustedDomains()` adds deterministic sorting.
- **Per-instance projection disabling (2025-08).** Versions 3.3.3 and 4.0.1 add it.
- **Projection correctness (2025-09).** Versions 3.4.2/4.2.0 prevent skipped same-microsecond or push-raced events; 3.4.2 prevents two projections sharing one table; 3.4.2/4.2.1 update failed-event state after reduction errors.
- **Configured projection locks (2025-10).** Version 4.6.2 follows projection-locking configuration.
- **Pre-provisioned database objects (2026-01).** Version 4.10.0 skips privileged init commands when the objects already exist.
- **PostgreSQL 18 (2026-02).** Version 4.11.0 setup supports it.
- **Trusted domains at setup (2026-03).** Version 4.12.0 accepts them during instance creation.
- **PostgreSQL and Redis URLs (2026-03).** Version 4.13.0 accepts DSN/URL strings.
- **Instance setup corrections (2026-04).** Version 4.13.1 stops initialization emails to administrators and fixes the organization-existence check.
- **Setup migration connections (2026-06).** Version 4.15.2 corrects handling after steps 40, 64, and 70.
- **Event resource-owner reassignment (2026-06).** Version 4.15.2 permits overwrite for operations that must reassign ownership.

## Telemetry, service reporting, and runtime behavior

- **Telemetry controls (2025-05).** Metrics/tracing service name is configurable and projection handlers expose Prometheus metrics.
- **River OpenTelemetry metrics (2025-07).** Version 3.3.1 emits queue metrics.
- **Metric scope metadata removal (2025-08).** Versions 2.71.15, 3.3.6, and 4.0.2 stop adding default scope information; dashboards must not depend on it.
- **Service Ping defaults (4.0.0).** Opt-out anonymized reporting corrects its endpoint and validates/randomizes the interval.
- **Expanded Service Ping (2025-09).** Version 4.2.0 reports more resource counts; 4.2.1 logs report body sizes.
- **River units (2025-09).** Versions 2.71.17, 3.4.2, and 4.1.0 correct metric units; revisit alerts.
- **gRPC status metrics (2025-10).** Version 4.6.0 corrects `grpc_server_grpc_status_code_total` mapping.
- **Logs and GCP Error Reporting (2026-02).** Version 4.11.0 adds both; 4.11.1 fixes the setup stream and masks grouped structured attributes.
- **Login readiness and push telemetry (2026-03).** Version 4.13.0 adds a readiness endpoint plus push logs, metrics, and traces; resources use configured service name.
- **Standard OpenTelemetry environment variables (2026-04).** Version 4.14.0 supports them through autoexport.
- **HTTP metric route labels (2026-08).** Version 4.16.3 reports route patterns rather than raw request paths, reducing label cardinality.

## Additional compatibility details

- **Imported password formats (2025-05).** Version 3.0 adds salted MD5 verification; 3.1 adds SHA2 and PHPass.
- **Drupal 7 password hashes (2025-10).** Version 4.6.0 adds verify support through passwap.
- **SAML app Login selection (2025-05).** Console can choose the Login UI per SAML app.
- **SCIM create-password behavior (4.0.0).** Provisioners can ignore generated random passwords through metadata.
- **User information in Action metadata (2025-08).** Version 4.0.1 adds user information to metadata-setting context.
- **External-provider users without names (2026-08).** Version 4.16.0 avoids failing automatic creation solely for missing upstream name fields.
