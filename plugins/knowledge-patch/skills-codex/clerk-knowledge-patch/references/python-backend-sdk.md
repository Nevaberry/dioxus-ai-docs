# Python Backend SDK

## Authenticate requests and filter token types

`Clerk.authenticate_request()` accepts an `httpx.Request` and
`AuthenticateRequestOptions`. Constrain authorized-party values with
`authorized_parties`. The returned state exposes `is_signed_in` and either the
verified `payload` or failure `reason`. Machine routes can narrow acceptance
through `accepts_token`, such as `['oauth_token']`.

```python
state = clerk.authenticate_request(
    request,
    AuthenticateRequestOptions(
        authorized_parties=['https://example.com'],
    ),
)
```

## Create and revoke Agent Tasks

`clerk.agent_tasks.create()` creates a task on behalf of a user and returns a
URL that creates a session when visited. An `agent_id` stays stable for a given
`agent_name` within one instance; each call creates a unique `task_id`. Cancel a
pending task through `revoke(agent_task_id=...)`.

```python
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

## Manage API keys through their full lifecycle

`clerk.api_keys` provides `create_api_key`, `get_api_keys`, `get_api_key`,
`update_api_key`, `delete_api_key`, `get_api_key_secret`, `revoke_api_key`, and
`verify_api_key`.

Creation requires `name` and `subject`; it may also include claims, scopes,
description, and expiration seconds. Verification accepts the secret itself.

```python
key = clerk.api_keys.create_api_key(
    name="deploy",
    subject="user_id",
    scopes=["read"],
    seconds_until_expiration=3600,
)
verified = clerk.api_keys.verify_api_key(secret="api-key-secret")
```

## Administer Billing resources

`clerk.billing` lists Plans and prices, creates customer-specific prices,
manages Subscription items and free trials, creates price transitions, and
reads statements and payment attempts.

Custom prices are in cents, have a 100-cent minimum, and default to USD.
Cancellation defaults to the end of the Billing period unless `end_now=True`.
Repeating a free-trial extension with the same future timestamp is idempotent.

```python
price = clerk.billing.create_price(plan_id="plan_id", amount=100)
item = clerk.billing.cancel_subscription_item(
    subscription_item_id="item_id",
    end_now=False,
)
```

User and Organization resources each expose `get_billing_subscription`,
`get_billing_credit_balance`, and `adjust_billing_credit_balance`.

## Run bulk account and invitation operations

`clerk.invitations.bulk_create()` accepts at most 10 invitations. An existing
invitation conflicts unless that entry uses `ignore_existing`; an existing user
with the address always conflicts. `notify` decides whether to send email.

The SDK also provides `users.bulk_ban()`, `users.bulk_unban()`, and
`waitlist_entries.bulk_create()`.

## Configure OAuth and Instance Protect

Read and update OAuth behavior with
`get_o_auth_application_settings()` and
`update_o_auth_application_settings()`. Options include
`dynamic_oauth_client_registration` and `oauth_jwt_access_tokens`.

Instance Protect is separate: use `get_instance_protect()` and
`update_instance_protect()` with `rules_enabled` and `specter_enabled`.

```python
clerk.instance_settings.update_o_auth_application_settings(request={
    "dynamic_oauth_client_registration": False,
    "oauth_jwt_access_tokens": True,
})
clerk.instance_settings.update_instance_protect(request={
    "rules_enabled": True,
    "specter_enabled": True,
})
```

## Plan production-domain changes as deployments

`clerk.instance_settings.change_domain()` invalidates all current user sessions
and can cause brief downtime. Coordinate DNS and certificate deployment, update
social-connection redirect URLs, and replace application keys.

`clerk.beta_features.update_production_instance_domain()` is deprecated in
favor of this instance-settings operation.

## Enforce machine-token authorization boundaries

Creating an M2M token requires a Machine Secret Key. Listing, revoking, and
verifying may use a Machine Secret Key or the instance Secret Key:

- A machine key lists only its machine's tokens, revokes only tokens managed by
  that machine, and verifies only tokens granted access to it.
- The instance key operates on any token in the instance.

## Rotate machine secrets and limit scopes

`machines.rotate_secret_key()` accepts `previous_token_ttl`, the grace period
for the old key. Use `0` for immediate expiration; the maximum is 28,800 seconds
(eight hours). Add M2M access with
`create_scope(machine_id=..., to_machine_id=...)`; each machine supports at most
150 scopes.

```python
clerk.machines.rotate_secret_key(
    machine_id="machine_id",
    previous_token_ttl=300,
)
clerk.machines.create_scope(
    machine_id="caller_id",
    to_machine_id="target_id",
)
```

## Remove deprecated Python surfaces

Besides the production-domain method, `clerk.clients.list()` is scheduled for
removal. Legacy email/SMS template upsert, list, get, revert,
delivery-toggle, and preview operations are also deprecated.

## Configure retries and handle errors

Only retry-capable operations accept `retries=RetryConfig(...)`. Set
`retry_config` on `Clerk` to change the client-wide strategy.

HTTP errors derive from `ClerkBaseError`, exposing `message`, `status_code`,
`headers`, `body`, `raw_response`, and optional structured `data`. `ClerkErrors`
contains API error lists. Network failures are `httpx.RequestError`.
`ResponseValidationError.cause` contains the underlying Pydantic validation
error.

## Pin versions across generated schema changes

Python 5.x is not safe to upgrade solely by semver expectations. Pin an exact
version and review generated request and response types on every update.

- 5.0.4 marks the `api_keys.create_api_key()` response as breaking.
- 5.0.7 changes types across user, Billing, and Organization-domain
  operations.
- 5.1.0 incompatibly changes the
  `miscellaneous.get_public_interstitial()` request.
- 6.0.0 incompatibly changes request types for `users.update()` and
  `organizations.update()`, and adds `organizations.replace_metadata()` for
  replacement rather than merge behavior.

## Use current email and phone verification operations

Version 5.0.7 adds `email_addresses.replace_for_user()` and
`phone_numbers.replace_for_user()`, and adds the breaking `verification_scim`
variant to the email-verification union.

Version 5.1.0 adds `prepare_verification()` and `attempt_verification()` to both
resources. Both replacement operations can set `identification_status`, and
OTP verification results expose `channel`.

## Test enterprise connections and preserve attribute cardinality

Version 5.1.0 adds `enterprise_connections.create_test_run()` and
`list_test_runs()`. Enterprise-connection custom attributes accept and return
`multi_valued` in create, update, and response types.

## Preserve Billing periods and discounts

`billing.create_price()` accepts `supported_billing_periods`, and price create
and list responses expose it. Statement group-item totals and payment-attempt
totals now include `discounts`.

## Preserve Role Sets and membership ban state

Organization create and update requests accept `role_set_key`; Organization
types, including those embedded in user and membership responses, expose it.
Organization-membership `public_user_data` includes `banned`, preserving the
user's instance-wide ban state.

## Configure sign-in strategy and M2M lifetime

`instance_settings.update()` accepts
`preferred_sign_in_strategy_when_password_required`. M2M token creation accepts
`min_remaining_ttl_seconds` when requesting a minimum remaining lifetime.
