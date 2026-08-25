# Scopes and Authentication

Use this reference when generating scoped resources, designing ownership-aware
context APIs, nesting routes under an organization or tenant, or upgrading
generated authentication. The generator-scope behavior is documented by the
`1.8-guides` batch.

## Generated scopes are data-access boundaries

Running:

```console
$ mix phx.gen.auth Accounts User users
```

creates an `Accounts.Scope` struct. Unless the application already has another
default scope, the generator also registers a default user scope.

For browser requests, `fetch_current_scope_for_user` assigns the scope as
`:current_scope`. Generated authentication provides the corresponding LiveView
mount hook. Generated controllers and LiveViews then pass the scope as the
first argument to context operations.

After a default is configured, `phx.gen.schema`, `phx.gen.context`,
`phx.gen.live`, `phx.gen.html`, and `phx.gen.json` generate ownership fields and
scoped queries instead of unqualified data access:

```elixir
def list_posts(%Scope{} = scope) do
  Repo.all(from post in Post, where: post.user_id == ^scope.user.id)
end
```

Put generated authenticated LiveView routes in the authenticated
`live_session`. The session's mount hook must establish the scope before any
generated scoped operation runs.

## Declare a generator scope

Scopes are discovered from application configuration. An application may have
only one default scope.

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

The options have distinct responsibilities:

- `module` identifies the scope struct module.
- `assign_key` names the connection or socket assign.
- `access_path` tells generated code how to read the owner identifier.
- `schema_key`, `schema_type`, and `schema_table` define the generated
  ownership column and association.
- `test_data_fixture` supplies scope fixture data.
- `test_setup_helper` names the setup function used by generated controller or
  LiveView tests.

The fixture module must implement `<name>_scope_fixture/0`; for the `user`
scope, that is `user_scope_fixture/0`. The setup helper must be importable by
the generated tests.

Set `schema_migration_type` when the migration column type needs to differ from
`schema_type`. Set `schema_table: nil` when the ownership value should be a
plain scope-id column rather than a foreign key.

## Use multiple and route-aware scopes

Define multiple scopes when the application has more than one ownership
boundary, then select a non-default scope with `--scope`:

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

`route_prefix` nests generated routes. `route_access_path` selects the
URL-facing value, such as a slug, independently of the database ownership key
selected by `access_path`.

For route-derived scopes:

1. Start from the authenticated user scope.
2. Load the requested organization through that existing scope so the lookup
   itself remains authorization-aware.
3. Update `:current_scope` in a browser plug.
4. Perform the same update in a LiveView `on_mount` hook.

This makes generated paths use the route value while preserving scoped access
for both controller and LiveView requests.

## Magic-link-first authentication

Generated authentication uses email confirmation and magic-link login first.
Password authentication is opt-in, and registration no longer asks the user to
choose a password.

The generated `UserAuth` provides:

- `fetch_current_scope_for_user` to establish the current scope;
- `require_authenticated_user` to enforce sign-in; and
- `require_sudo_mode` for sensitive operations that require recent
  authentication.

Run `fetch_current_scope_for_user` before `require_authenticated_user` in the
browser pipeline.

## Generated-auth asset requirement

The auth generator warns when esbuild is unavailable. Its generated features
assume that `phoenix_html.js` is present in the JavaScript bundle, so verify the
asset import rather than dismissing the warning.

## Migrate authentication generated before Phoenix 1.8

Generated auth code is not updated automatically. To move from the earlier
password-registration flow:

1. Create a new migration that makes `hashed_password` nullable. Do not edit an
   old migration that may already have run.
2. Set `hashed_password` to `nil` for every account that is still unconfirmed.
   This avoids credential pre-stuffing.
3. Plan for the operation to invalidate a password chosen by someone who has
   just registered but not confirmed.

Deploy the data migration during low traffic, or add magic-link login without
fully replacing the existing flow when that invalidation window is
unacceptable.
