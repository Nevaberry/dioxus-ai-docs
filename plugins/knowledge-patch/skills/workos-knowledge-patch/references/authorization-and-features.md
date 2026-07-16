# Authorization, Roles, Groups, and Feature Flags

## Authorization resources and roles

Use authorization resources and role APIs for scoped authorization. Apply the
legacy FGA removal described in the Node SDK migration reference when upgrading.

The SDK supports:

- environment roles;
- organization roles;
- authorization resources; and
- resource-scoped custom roles.

Permission and role objects expose `resourceTypeSlug`. Pass
`resource_type_slug` to `createOrganizationRole`, and use
`CreateAuthorizationResourceOptions` for typed resource creation.

Invitations accept `role_slug`.

## Role assignments

Use both resource and group role-assignment endpoints. Filter assignment lists
with `resource` and `role_slug`.

Returned role assignments contain `source`. Inspect it to distinguish direct
grants from roles inherited through a group.

## Multi-role provisioning

An organization membership can hold multiple roles across AuthKit, SSO, and
Directory Sync. Do not collapse membership state to one role when consuming or
persisting it.

During SSO setup, an IT administrator can map identity-provider groups to roles
in Admin Portal. Account for those group-derived roles when explaining or
auditing effective access.

## Feature Flag evaluation

Use the Feature Flags runtime client to evaluate flags locally when an API
request for every evaluation is undesirable.

The Feature Flag control plane supports:

- organization rollouts;
- fetching flags for an organization through the API;
- targeting individual users;
- flag management through the management API; and
- delivery of flag updates to Slack.
