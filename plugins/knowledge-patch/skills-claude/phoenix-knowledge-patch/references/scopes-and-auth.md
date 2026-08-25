# Scoped Data Access and Authentication

## Generated scopes are data-access boundaries

The `1.8-guides` generator guidance makes scopes part of generated context
APIs. Running:

```console
$ mix phx.gen.auth Accounts User users
```

creates an `Accounts.Scope` struct and, unless another default already exists,
registers a default user scope. `fetch_current_scope_for_user` assigns that
scope as `:current_scope` for browser requests, and a corresponding LiveView
mount hook installs it for LiveViews.

Generated controllers and LiveViews pass the scope as the first argument to
context operations. After a default scope is configured, `phx.gen.schema`,
`phx.gen.context`, `phx.gen.live`, `phx.gen.html`, and `phx.gen.json` generate
ownership fields and scoped queries instead of unqualified access:

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

Put generated authenticated LiveView routes in the authenticated
`live_session`. The mount hook must assign the scope before generated context
operations run.

## Declare a generator scope

Generators discover scopes through application configuration. There may be
only one default scope. `access_path` tells generated code how to reach the
owner identifier; the `schema_*` keys describe the generated ownership column
and association.

```elixir
config :my_app, :scopes,
  user: [
    default: true,
    module: MyApp.Accounts.Scope,
    assign_key: :current_scope,
    access_path: [:user, :id],
    schema_key: :user_id,
    schema_type: :id,
    schema_table: :users,
    test_data_fixture: MyApp.AccountsFixtures,
    test_setup_helper: :register_and_log_in_user
  ]
```

The fixture module must export `<name>_scope_fixture/0`, such as
`user_scope_fixture/0`. The configured setup helper must be importable by the
generated controller or LiveView tests.

Use `schema_migration_type` when the ownership column's migration type differs
from `schema_type`. Set `schema_table: nil` to generate a plain scope-ID column
instead of a foreign key.

## Select multiple and route-aware scopes

An application may configure multiple scopes and choose a non-default scope
with `--scope`. `route_prefix` nests generated routes. `route_access_path` may
use a public route value such as a slug independently of the database ownership
key in `access_path`.

```elixir
config :my_app, :scopes,
  organization: [
    module: MyApp.Accounts.Scope,
    assign_key: :current_scope,
    access_path: [:organization, :id],
    route_prefix: "/organizations/:org",
    route_access_path: [:organization, :slug],
    schema_key: :org_id,
    schema_type: :id,
    schema_table: :organizations,
    test_data_fixture: MyApp.AccountsFixtures,
    test_setup_helper: :register_and_log_in_user_with_org
  ]
```

```console
$ mix phx.gen.live Blog Post posts title:string body:text --scope organization
```

For a route-derived organization scope, first load the organization through
the existing user scope. Then update `:current_scope` in both a browser plug
and a LiveView `on_mount` hook. This retains authorization-aware nested
lookups while allowing generated paths to use the configured slug.

## Use magic-link-first authentication

The Phoenix 1.8 auth generator uses email confirmation and magic-link login.
Password authentication is opt-in, and registration no longer collects a
password.

Generated `UserAuth` provides:

- `fetch_current_scope_for_user` to establish the current scope.
- `require_authenticated_user` to enforce authentication; it must run after
  the scope-fetching plug.
- `require_sudo_mode` to protect sensitive operations with a recent-auth
  requirement.

## Migrate authentication generated before 1.8

Generated authentication code is not updated automatically. For a complete
migration from the older password-registration flow:

1. Add a new migration that makes `hashed_password` nullable. Do not edit an
   old migration that has already run.
2. Set `hashed_password` to `nil` for every still-unconfirmed account. This
   prevents credential pre-stuffing against accounts whose email address has
   not been confirmed.
3. Plan for the race in which a newly registered person has just chosen a
   password: the cleanup can invalidate it. Deploy during low traffic, or add
   magic links without fully replacing the existing flow.

## Keep generated authentication assets available

The auth generator warns when esbuild is unavailable. Its generated behavior
assumes `phoenix_html.js` is included in the JavaScript bundle, so preserve or
replace that inclusion deliberately when customizing asset tooling.
