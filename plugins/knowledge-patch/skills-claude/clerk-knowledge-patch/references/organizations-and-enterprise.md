# Organizations and enterprise

## Activity reporting

An Organization's Dashboard profile includes a year-selectable daily activity
report showing the percentage of members active each day. History begins in
January 2026.

## Enterprise connection API

Manage SAML and OIDC through `/v1/enterprise_connections`. Migrate from the
legacy `/saml_connections` surface, which may be phased out. Creation accepts
`provider`, `domains`, `name`, and `organization_id`; listing accepts optional
`organization_id` plus pagination.

```text
POST   /v1/enterprise_connections
GET    /v1/enterprise_connections
GET    /v1/enterprise_connections/{enterpriseConnectionID}
PATCH  /v1/enterprise_connections/{enterpriseConnectionID}
DELETE /v1/enterprise_connections/{enterpriseConnectionID}
```

## Active Organization and tenant scoping

Each tab remembers its own Active Organization, but the singleton session cookie
reflects whichever tab is currently active. Tenant-scoped background work must
fetch a token with `getToken()` in its tab and send it as a bearer token rather
than trusting the cookie.

## Membership defaults

Organizations are disabled until enabled. Applications created since August
22, 2025 default to **Membership required** when enabling Organizations; new
and existing users must complete the Organization session task. Older apps keep
optional membership. Selecting **Membership optional** enables Personal
Accounts and starts users in their individual workspace.

## Slug routing and activation checks

Slugs default to disabled for applications created after October 7, 2025. When
enabled, components can navigate under `/orgs/:slug`, and Next.js middleware can
synchronize through `organizationSyncOptions`. An unknown or unjoined slug
leaves the previous Organization active. Compare the route slug with `orgSlug`
before reading or rendering tenant data.

```ts
export default clerkMiddleware((_auth, _req) => {}, {
  organizationSyncOptions: {
    organizationPatterns: ['/orgs/:slug', '/orgs/:slug/(.*)'],
  },
})
```

## Automatic first-Organization naming

Automatic first-Organization creation and default naming are separate settings,
both off by default. Naming tries the email domain, then a member template such
as `{{user.first_name}}'s organization`, then the fallback. Without automatic
creation, the same rules only prefill manual creation.

## Membership and deletion limits

Users can join any number of Organizations. Each Organization defaults to five
members; `maxAllowedMemberships: 0` means unlimited. Disabling new-member
Organization deletion affects only subsequently created Organizations;
existing Organizations retain their current deletion behavior.

## Creator and Default Role invariants

The Creator Role defaults to `org:admin` and must retain
`org:sys_memberships:manage`, `org:sys_memberships:read`, and
`org:sys_profile:delete`. The member Default Role defaults to `org:member` and
is used for invitations and Verified Domain enrollment. Replace a Creator or
Default Role before deleting it, and reassign all members before deleting any
in-use Role.

## Invitations

Organization invitations require Email even when email sign-in is disabled.
Frontend `organization.inviteMember()` always routes through Account Portal and
cannot set a redirect. Server-created invitations can supply `redirect_url`,
whose destination must host sign-in or a custom acceptance flow.

After link-based sign-up, `OrganizationInvitation.publicMetadata` is copied to
`OrganizationMembership.publicMetadata`. Single and bulk creation are limited
to 250 and 50 requests per application per hour. On HTTP 429, wait for
`Retry-After`.

## Verified Domains

Verified Domains are enabled application-wide. Common/disposable domains are
rejected, and one domain cannot also back enterprise SSO for the same
Organization. Each domain chooses exactly one mode:

- `automatic_invitation` lets a matching user accept immediately.
- `automatic_suggestion` creates an admin-approved membership request, currently
  reviewable only through `<OrganizationSwitcher />`.

## Enterprise SSO membership lifecycle

Signing in through an Organization connection JIT-provisions membership with
the Default Role. Removing such a member is temporary while the IdP and
connection remain valid. Moving a connection leaves existing memberships in
place and adds users to the destination Organization on their next sign-in.

## Google Workspace Directory Sync

Google SAML connections can pull users, groups, and group memberships through a
service account rather than waiting for sign-in. This guidance comes from batch
`2026-07-31-2026-08-17`. Configure the **Directory sync** tab with a
domain-wide-delegated service-account key and an administrator to impersonate.
Synced groups can map to Roles. Attribute paths may be standard, such as
`organizations.title`, custom-schema paths such as
`customSchemas.EmployeeInfo.costCenter`, or multi-valued array paths. Disabling
sync preserves credentials for later re-enablement.

## Self-service OIDC connections

Organizations can expose OIDC setup in the **Security** tab of
`<OrganizationProfile />` when self-service enterprise SSO is enabled. The
administrator needs `org:sys_entconns:manage`. The flow verifies domains with
DNS TXT, accepts discovery or explicit authorization/token/user-info endpoints
plus client credentials, reads `sub` and `email` from the ID token and optional
`given_name`/`family_name`, requires a test before activation, and scopes the
connection to that Organization.

## System and Custom Permissions

System Permissions such as `org:sys_memberships:manage` drive FAPI and prebuilt
components but are absent from session claims. Server `has({ permission })`
must use an equivalent Custom Permission.

## Role Sets and migration

An Organization's Role Set limits which application Roles its members can
receive. Editing a set immediately affects every assigned Organization;
changing the Default Role Set affects only new Organizations. Switching or
deleting sets, or removing an in-use Role, requires mapping affected members to
Roles in the replacement set.

`Organization.getRoles()` returns `has_role_set_migration`. While true,
membership Role updates are blocked; custom Role UI must wait for or complete
the migration.

## Organization hook collections

`useOrganization()` leaves `memberships`, `invitations`, `membershipRequests`,
and `domains` unpopulated unless explicitly requested. `useOrganizationList()`
does the same for `userMemberships`, `userInvitations`, and `userSuggestions`.
Passing `true` fetches page one with 10 records; an options object controls page
size or accumulation with `infinite`.
