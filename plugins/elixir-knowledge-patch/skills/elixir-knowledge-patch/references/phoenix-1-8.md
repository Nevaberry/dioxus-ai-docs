# Phoenix 1.8

Requires OTP 25+.

## Scopes: First-Class Secure Data Access

Generators now create a `%MyApp.Accounts.Scope{}` struct (added by `phx.gen.auth`) that threads through all context functions for automatic data filtering and scoped PubSub:

```elixir
# Generated context functions take scope as first arg
def list_posts(%Scope{} = scope) do
  Repo.all(from p in Post, where: p.user_id == ^scope.user.id)
end

# LiveViews use socket.assigns.current_scope
def mount(_params, _session, socket) do
  Blog.subscribe_posts(socket.assigns.current_scope)
  {:ok, stream(socket, :posts, Blog.list_posts(socket.assigns.current_scope))}
end
```

Configure default scope in `config/config.exs`:

```elixir
config :my_app, :scopes, user: [default: true, ...]
```

## Magic Link Auth by Default

`phx.gen.auth` now generates passwordless magic link auth by default. Includes `require_sudo_mode` plug for sensitive operations requiring recent authentication.

## Simplified Layouts

Single `root.html.heex` layout. App layout is now an explicit function component call in templates instead of `use Phoenix.LiveView, layout: ...`:

```heex
<Layouts.app flash={@flash}>
  <:breadcrumb><.link navigate={~p"/posts"}>Posts</.link></:breadcrumb>
  <p>My content</p>
</Layouts.app>
```

Multiple app layouts: just create `<Layouts.admin>`, `<Layouts.cart>`, etc.

## Security Headers

`put_secure_browser_headers` now sets `content-security-policy: "base-uri 'self'; frame-ancestors 'self';"` by default. Removed deprecated `x-download-options` and `x-frame-options`.

## Deprecations & Breaking Changes

- `use Phoenix.Controller` now **requires** `:formats` option
- `put_layout(conn, :print)` (without module) deprecated
- `:trailing_slash` router option deprecated → use `Phoenix.VerifiedRoutes`
- `config` variable in `Phoenix.Endpoint` removed → use `Application.compile_env/3`
- Generator context argument now optional (defaults to plural name)
- Generators use Ecto 3.13 `Repo.transact/2`
