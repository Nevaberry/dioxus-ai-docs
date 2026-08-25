# Python Backend SDK

## Request authentication

`Clerk.authenticate_request()` accepts an `httpx.Request` and
`AuthenticateRequestOptions`. Use `authorized_parties` to constrain authorized
party values. The returned state exposes `is_signed_in` and either verified
`payload` or failure `reason`. Machine routes can filter through
`accepts_token`, for example `['oauth_token']`.

```py
state = clerk.authenticate_request(
    request,
    AuthenticateRequestOptions(authorized_parties=['https://example.com']),
)
```

## Agent tasks

`clerk.agent_tasks.create()` creates a task on a user's behalf and returns a URL
that creates a session when opened. `agent_id` is stable for an `agent_name`
within an instance; every call has a unique `task_id`. Revoke pending work with
`revoke(agent_task_id=...)`.

```py
task = clerk.agent_tasks.create(request={
    "on_behalf_of": {"user_id": "user_id", "identifier": "user@example.com"},
    "permissions": clerk_backend_api.CreateAgentTaskPermissions.WILDCARD_,
    "agent_name": "support-agent",
    "task_description": "Resolve the support request",
    "redirect_url": "https://example.com/complete",
})
```

## API-key lifecycle

`clerk.api_keys` provides `create_api_key`, `get_api_keys`, `get_api_key`,
`update_api_key`, `delete_api_key`, `get_api_key_secret`, `revoke_api_key`, and
`verify_api_key`. Creation requires name and subject and may include claims,
scopes, description, and expiration seconds. Verification accepts the secret.

```py
key = clerk.api_keys.create_api_key(
    name="deploy", subject="user_id", scopes=["read"],
    seconds_until_expiration=3600,
)
verified = clerk.api_keys.verify_api_key(secret="api-key-secret")
```

## Billing administration

`clerk.billing` can list Plans and prices, create customer-specific prices,
manage Subscription items and trials, create price transitions, and read
statements and payment attempts. Custom price amounts are cents with a 100-cent
minimum and default to USD. Cancellation defaults to the period end unless
`end_now=True`. Repeating a trial extension with the same future timestamp is
idempotent.

```py
price = clerk.billing.create_price(plan_id="plan_id", amount=100)
item = clerk.billing.cancel_subscription_item(
    subscription_item_id="item_id", end_now=False,
)
```

User and Organization resources also provide `get_billing_subscription`,
`get_billing_credit_balance`, and `adjust_billing_credit_balance`.

## Bulk operations

`clerk.invitations.bulk_create()` accepts at most 10 entries. Existing
invitations conflict unless their entry uses `ignore_existing`; an existing user
always conflicts. `notify` controls email delivery. The SDK also exposes
`users.bulk_ban()`, `users.bulk_unban()`, and
`waitlist_entries.bulk_create()`.

## Instance OAuth and protection controls

Read and update OAuth behavior with `get_o_auth_application_settings()` and
`update_o_auth_application_settings()`, including
`dynamic_oauth_client_registration` and `oauth_jwt_access_tokens`. Manage
Instance Protect separately through `get_instance_protect()` and
`update_instance_protect()` with `rules_enabled` and `specter_enabled`.

## Production domain changes

`clerk.instance_settings.change_domain()` invalidates every current user
session and can briefly interrupt deployment. Coordinate DNS and certificates,
update social-connection redirect URLs, and replace application keys.

## Machine authorization and rotation

M2M token creation requires a Machine Secret Key. Listing, revocation, and
verification accept a Machine Secret Key or instance Secret Key. A machine key
can list only its machine's tokens, revoke only tokens it manages, and verify
only tokens granted access to it; the instance key can act on all instance
tokens.

`machines.rotate_secret_key(previous_token_ttl=...)` controls the old key's
grace period: use `0` for immediate expiry and do not exceed 28,800 seconds.
Create machine-to-machine access with
`create_scope(machine_id=..., to_machine_id=...)`; a machine can have at most
150 scopes.

## Deprecated surfaces

- `beta_features.update_production_instance_domain()` is superseded by the
  instance-settings domain operation.
- `clerk.clients.list()` is scheduled for removal.
- Legacy email/SMS template upsert, list, get, revert, delivery-toggle, and
  preview operations are deprecated.

## Retries and errors

Only retry-capable methods accept `retries=RetryConfig(...)`. Set
`retry_config` on `Clerk` for a client-wide strategy. HTTP failures derive from
`ClerkBaseError`, with `message`, `status_code`, `headers`, `body`,
`raw_response`, and optional structured `data`. `ClerkErrors` carries API error
lists, network failures are `httpx.RequestError`, and
`ResponseValidationError.cause` contains the underlying Pydantic error.

## Upgrade compatibility

Pin exact SDK versions and inspect generated schemas for every 5.x patch or
minor upgrade:

- 5.0.4 makes the `api_keys.create_api_key()` response breaking.
- 5.0.7 changes request or response types for user, Billing, and Organization
  domain operations.
- 5.1.0 incompatibly changes the
  `miscellaneous.get_public_interstitial()` request.
- 6.0.0 incompatibly changes request models for `users.update()` and
  `organizations.update()`, and adds `organizations.replace_metadata()` for
  replacement rather than merge.

## Verification and enterprise-connection additions

5.0.7 adds `email_addresses.replace_for_user()` and
`phone_numbers.replace_for_user()` and adds a breaking `verification_scim`
variant to the email verification union. 5.1.0 adds `prepare_verification()` and
`attempt_verification()` to both resources, allows replacement calls to set
`identification_status`, and exposes OTP-result `channel`.

5.1.0 also adds `enterprise_connections.create_test_run()` and
`list_test_runs()`. Enterprise custom attributes gain `multi_valued` in create,
update, and returned connection models.

## Billing, Organizations, and instance additions

- `billing.create_price()` and price results support
  `supported_billing_periods`.
- Statement group-item and payment-attempt totals include `discounts`.
- Organization create/update accepts `role_set_key`; Organization models,
  including embedded user and membership forms, expose it.
- Membership `public_user_data` exposes `banned` for instance-level ban state.
- `instance_settings.update()` accepts
  `preferred_sign_in_strategy_when_password_required`.
- M2M creation accepts `min_remaining_ttl_seconds` to require a minimum
  remaining token lifetime.
