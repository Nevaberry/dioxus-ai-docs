# Organizations & Permissions

## `organizationSyncOptions` in `clerkMiddleware()`

When building multi-tenant apps with org slugs in URLs (e.g., `/orgs/acmecorp/dashboard`), configure `clerkMiddleware()` to auto-activate the correct organization based on the URL:

```tsx
import { clerkMiddleware } from '@clerk/nextjs/server'

export default clerkMiddleware(
  (auth, req) => {
    // your middleware checks
  },
  {
    organizationSyncOptions: {
      organizationPatterns: [
        '/orgs/:slug',       // matches /orgs/acmecorp
        '/orgs/:slug/(.*)',  // matches /orgs/acmecorp/dashboard/settings
      ],
    },
  },
)
```

If the URL matches a pattern and a different org is active in the session, the middleware auto-switches to the org with that slug. If the slug doesn't exist or the user isn't a member, the active org is left unchanged (no error thrown).

Pair with `<OrganizationSwitcher>` / `<OrganizationList>` using `:slug` interpolation:

```tsx
<OrganizationSwitcher
  afterCreateOrganizationUrl="/orgs/:slug"
  afterSelectOrganizationUrl="/orgs/:slug"
/>
```

## Role Sets

Role Sets control which roles are available in each organization. Organizations are assigned a Role Set — if a role isn't in the set, members can't be assigned to it. Managed via Dashboard only (no programmatic API).

- **Primary Role Set**: Default set with `org:admin` and `org:member`. Can be modified.
- **Default Role Set**: Auto-assigned to new organizations. Defaults to Primary.
- Custom Role Sets require the **Enhanced B2B Authentication** add-on.
- Changing an org's Role Set triggers a **remapping flow** if members have roles not in the new set.

Key implication for code: if `organization.updateMember({ userId, role })` fails, the role may not be in the org's assigned Role Set.

## System Permissions

Clerk provides system permissions that power the Frontend API and org components:

- `org:sys_profile:manage` / `org:sys_profile:delete`
- `org:sys_memberships:read` / `org:sys_memberships:manage`
- `org:sys_domains:read` / `org:sys_domains:manage`
- `org:sys_billing:read` / `org:sys_billing:manage`

**Important**: System Permissions are NOT included in session token claims. To check permissions server-side, create Custom Permissions (e.g., `org:invoices:create`) instead. Custom Permissions follow the format `org:<feature>:<permission>`.
