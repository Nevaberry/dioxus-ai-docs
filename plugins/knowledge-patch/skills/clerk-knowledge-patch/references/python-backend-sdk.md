# Python Backend SDK

## Authenticate requests

`Clerk.authenticate_request()` accepts an `httpx.Request` and `AuthenticateRequestOptions`. Constrain accepted authorized-party values with `authorized_parties`.

```py
state = clerk.authenticate_request(
    request,
    AuthenticateRequestOptions(
        authorized_parties=['https://example.com'],
    ),
)
```

The returned state exposes `is_signed_in` plus either verified `payload` or failure `reason`. Machine routes can narrow accepted credentials through `accepts_token`, for example `['oauth_token']`.

## Agent tasks

`clerk.agent_tasks.create()` creates a task on behalf of a user and returns a URL that creates a session when visited.

```py
task = clerk.agent_tasks.create(request={
    "on_behalf_of": {
        "user_id": "user_id",
        "identifier": "user@example.com",
    },
    "permissions": clerk_backend_api.CreateAgentTaskPermissions.WILDCARD_,
    "agent_name": "support-agent",
    "task_description": "Resolve the support request",
    "redirect_url": "https://example.com/complete",
})
```

For one `agent_name` within an instance, `agent_id` remains stable. Every call receives a unique `task_id`. Cancel a pending task with `revoke(agent_task_id=...)`.

## API-key lifecycle

The `clerk.api_keys` resource provides:

- `create_api_key`
- `get_api_keys`
- `get_api_key`
- `update_api_key`
- `delete_api_key`
- `get_api_key_secret`
- `revoke_api_key`
- `verify_api_key`

Creation requires `name` and `subject`, and can include claims, scopes, a description, and `seconds_until_expiration`. Verification accepts the key secret itself.

```py
key = clerk.api_keys.create_api_key(
    name="deploy",
    subject="user_id",
    scopes=["read"],
    seconds_until_expiration=3600,
)
verified = clerk.api_keys.verify_api_key(secret="api-key-secret")
```

## Billing administration

`clerk.billing` can:

- List Plans and prices.
- Create customer-specific prices.
- Manage Subscription items and free trials.
- Create price transitions.
- Read statements and payment attempts.

Custom-price amounts are cents, with a 100-cent minimum, and default to USD. Subscription-item cancellation defaults to the end of the Billing period unless `end_now=True`. Repeating a free-trial extension with the same future timestamp is idempotent.

```py
price = clerk.billing.create_price(plan_id="plan_id", amount=100)
item = clerk.billing.cancel_subscription_item(
    subscription_item_id="item_id",
    end_now=False,
)
```

User and Organization resources each expose `get_billing_subscription`, `get_billing_credit_balance`, and `adjust_billing_credit_balance`.

## Bulk operations

`clerk.invitations.bulk_create()` accepts no more than 10 invitations per call.

- Existing invitations conflict unless that entry sets `ignore_existing`.
- An existing user with the email always conflicts.
- `notify` controls whether Clerk sends invitation email.

The SDK also includes `users.bulk_ban()`, `users.bulk_unban()`, and `waitlist_entries.bulk_create()`.

## Instance OAuth and Protect controls

Read and update instance OAuth behavior with `get_o_auth_application_settings()` and `update_o_auth_application_settings()`. Settings include `dynamic_oauth_client_registration` and `oauth_jwt_access_tokens`.

Instance Protect is separate: use `get_instance_protect()` and `update_instance_protect()` with `rules_enabled` and `specter_enabled`.

```py
clerk.instance_settings.update_o_auth_application_settings(request={
    "dynamic_oauth_client_registration": False,
    "oauth_jwt_access_tokens": True,
})
clerk.instance_settings.update_instance_protect(request={
    "rules_enabled": True,
    "specter_enabled": True,
})
```

## Production domain changes

`clerk.instance_settings.change_domain()` invalidates every current user session and may cause brief deployment downtime. A domain change also requires:

- DNS and certificate deployment.
- Updated social-connection redirect URLs.
- Replacement keys in application code.

Coordinate those changes as one deployment.

## Machine-token authorization

Creating an M2M token requires a Machine Secret Key. Listing, revoking, and verifying tokens may use either a Machine Secret Key or the instance Secret Key.

A Machine Secret Key can:

- List only its own machine's tokens.
- Revoke only tokens managed by that machine.
- Verify only tokens granted access to it.

The instance Secret Key can operate on any token in the instance.

## Machine secret rotation and scopes

`machines.rotate_secret_key()` accepts `previous_token_ttl`, the grace period for the old key. Use `0` for immediate expiry; the maximum is 28,800 seconds (eight hours).

Add M2M access with `create_scope(machine_id=..., to_machine_id=...)`. Each machine supports at most 150 scopes.

```py
clerk.machines.rotate_secret_key(
    machine_id="machine_id",
    previous_token_ttl=300,
)
clerk.machines.create_scope(
    machine_id="caller_id",
    to_machine_id="target_id",
)
```

## Deprecated surfaces

- `clerk.beta_features.update_production_instance_domain()` is deprecated; use the instance-settings domain operation.
- `clerk.clients.list()` is scheduled for removal.
- Legacy email/SMS template upsert, list, get, revert, delivery-toggle, and preview operations are deprecated.

## Retries and errors

Only retry-capable operations accept per-call `retries=RetryConfig(...)`. Set `retry_config` on `Clerk` for a client-wide strategy.

HTTP failures derive from `ClerkBaseError`, which exposes `message`, `status_code`, `headers`, `body`, `raw_response`, and optional structured `data`. `ClerkErrors` contains API error lists. Network failures are `httpx.RequestError`. `ResponseValidationError.cause` contains the underlying Pydantic validation error.

## Upgrade safety

Pin the Python SDK to an exact version and inspect generated request and response schemas even for 5.x patch and minor updates.

- Version 5.0.4 marks the `api_keys.create_api_key()` response as breaking.
- Version 5.0.7 changes request or response schemas for user, Billing, and Organization-domain operations.
- Version 5.1.0 incompatibly changes the `miscellaneous.get_public_interstitial()` request.
- Version 6.0.0 incompatibly changes requests for `users.update()` and `organizations.update()`.
- Version 6.0.0 adds `organizations.replace_metadata()` for replacement rather than merge semantics.

## Email and phone verification

Version 5.0.7 adds `email_addresses.replace_for_user()` and `phone_numbers.replace_for_user()`. It also adds the breaking `verification_scim` member to the email-verification union.

Version 5.1.0 adds `prepare_verification()` and `attempt_verification()` to both email-address and phone-number resources. Both replacement calls can set `identification_status`, and OTP verification results expose `channel`.

## Enterprise connection test runs

Version 5.1.0 adds `enterprise_connections.create_test_run()` and `list_test_runs()`. Enterprise-connection custom attributes accept and return `multi_valued` in create, update, and response schemas.

## Billing-period and discount fields

`billing.create_price()` accepts `supported_billing_periods`, and created or listed prices expose it. Statement group-item totals and payment-attempt totals include `discounts`.

## Organization Role Sets and ban state

Organization create and update requests accept `role_set_key`. Organization resources, including those embedded in user and membership responses, expose it. Organization-membership `public_user_data` includes `banned`, preserving the user's instance-level ban state.

## Sign-in strategy and M2M lifetime

`instance_settings.update()` accepts `preferred_sign_in_strategy_when_password_required`. M2M token creation accepts `min_remaining_ttl_seconds` to require a minimum remaining lifetime.
