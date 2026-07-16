# Concepts and migrations

## Database secret boundary

ZITADEL AES-256-encrypts database-held secrets with a `masterkey` that must be exactly 32 bytes. The master key, TLS key material, and initial administrator credentials remain outside that store, so self-hosters must supply and protect them separately.

## Password migration and rehashing

Password and client-secret hashes use Modular Crypt Format, embedding the algorithm, parameters, salt, and hash. Only `bcrypt` is enabled by default; migrations must enable other `Verifiers`, successful checks transparently rehash when the configured algorithm or cost changes, insecure MD5 and Drupal 7 formats are verify-only, and Argon2 is disabled on ZITADEL Cloud.

## Read-after-write behavior

Commands append events while queries read projections, so list and query results can lag behind a successful write; reads by ID often trigger projection catch-up. Clients should tolerate this eventual consistency instead of treating a momentarily stale query as a failed write.

## Projection failure diagnostics

Projection progress is tracked per instance in `projections.current_sequences` and corresponding `notification`, `auth`, and `adminapi` tables. After retry exhaustion an event is recorded in the matching `failed_events` table so later events are not blocked. Event sequence numbers preserve ordering but are not guaranteed to be contiguous, which matters when monitoring lag or consuming audit events.

## Virtual instance isolation

A fresh installation creates one virtual instance, but one deployment can host multiple fully isolated instances; each is a top-level resource that normally has its own domain and issuer, default settings, and organizations. Use a separate virtual instance rather than an organization when a customer needs an independent issuer and complete configuration isolation.

## Terminology across API generations

Current documentation maps `IAM` to **Instance**, `Member`/`Membership`/`Manager` to **Administrator**, and `User Grant`/`Authorization` to **Role Assignment**. Older API and resource names can retain the former terms, so these labels do not denote separate resource types.

## Individual cross-organization access

An external role assignment grants project roles directly to a specific user who remains in another organization. Unlike a project grant, it provides individual access without delegating role-assignment management to the user's organization.

## Linked external identities control login routing

Once an existing user enters a username linked to an external identity, ZITADEL redirects to that provider without offering a local-versus-external choice; local authentication is used only if the external login fails. If exactly one external provider is configured and password login is disabled, authentication requests redirect to it immediately.

## Actions migration overlap

Configured Actions V2 execute in addition to legacy Actions V1 rather than replacing them. A staged migration must prevent duplicate side effects and remove the old action after the equivalent V2 execution is active.

## Rolling zero-downtime upgrades

ZITADEL's rolling-upgrade model keeps the old release serving while the new release applies database schema updates and joins background-job leader election. Route traffic to the new release only after it reports readiness, and back up the database and review release notes before upgrading.
