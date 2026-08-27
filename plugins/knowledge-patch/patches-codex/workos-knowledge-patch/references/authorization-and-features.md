# Authorization, Roles, Groups, and Feature Flags

Use this reference for authorization resources, scoped roles, assignments,
groups, permissions, API keys, and feature evaluation.

## Authorization resources and roles

The SDK includes environment and organization roles, authorization resources,
and resource-scoped custom roles. Permissions and role objects expose
`resourceTypeSlug`. Pass `resource_type_slug` to
`createOrganizationRole`; use `CreateAuthorizationResourceOptions` for typed
resource creation.

The legacy FGA package was deprecated in Node SDK v8.4 and removed in v9.
Migrate FGA integrations to authorization resources and role APIs.

## Role assignments

Resource and group role-assignment endpoints are available. Filter lists with
`resource` and `role_slug`. Returned assignments include `source`, which
distinguishes a direct grant from a grant inherited through a group.

Invitations accept `role_slug`. `listEffectivePermissionsByExternalId` uses the
corrected endpoint as of v9.1.1; the same patch restored the established
Authorization method names after generated renames.

## Multiple roles and group provisioning

An organization membership may hold multiple roles provisioned through
AuthKit, SSO, or Directory Sync. During SSO setup, IT administrators can map
identity-provider groups to roles in Admin Portal.

The SDK exposes Groups endpoints and group event types. Typed events also cover
organization roles and permissions, feature flags, and groups; deserialized
role events expose `resourceTypeSlug`.

## Feature Flags

Use the Feature Flags runtime client to evaluate flags locally when an API call
per decision is undesirable.

The control plane supports organization rollouts, per-user targeting, an API
for fetching flags for an organization, and a management API. Flag updates can
be delivered to Slack. AuthKit authentication surfaces can return active
feature flags alongside the rest of the user's state.

## Organization and user API keys

Organization-owned API keys can be managed through an API. Handle key deletion
with the `api_key.revoked` event; `api_key.deleted` is obsolete.

Under the SDK contracts attributed to `10.10.0`, user API-key methods are also
available, `ApiKey.owner` includes a user variant and `organizationId`, and
API-key validation results can include an agent registration ID.
