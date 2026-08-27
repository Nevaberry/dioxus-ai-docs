# Authorization, Roles, Groups, and Feature Flags

## Authorization resources and roles

Use authorization resources and role APIs instead of the removed legacy FGA
package. Environment and organization roles are available, including
resource-scoped custom roles.

Permissions and roles expose `resourceTypeSlug`. Supply `resource_type_slug`
when creating an organization role, use typed
`CreateAuthorizationResourceOptions` for resources, and pass `role_slug` when
creating invitations.

## Role assignments

Resource and group role-assignment endpoints are available. Assignment lists
can be filtered by `resource` and `role_slug`. Inspect the returned assignment
`source` to distinguish direct grants from group-derived grants.

## Multi-role provisioning

Organization memberships can hold multiple roles assigned through AuthKit,
SSO, or Directory Sync. During SSO setup, IT administrators can map
identity-provider groups to roles in Admin Portal.

## Feature Flags runtime evaluation

Use the Feature Flags runtime client to evaluate flags locally when a network
request for every decision is unsuitable.

## Feature Flags control plane

Feature flags can roll out to organizations, target individual users, and be
fetched for an organization through the API. A management API controls flags,
and flag updates can be delivered to Slack.
