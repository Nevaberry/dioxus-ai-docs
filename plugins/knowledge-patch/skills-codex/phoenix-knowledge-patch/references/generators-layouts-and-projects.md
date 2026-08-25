# Generators, Layouts, and Generated Projects

Use this reference when creating a project or resource, adapting templates and
layouts, or accounting for generator-created files and side effects. General
generated-project behavior here is attributed to `1.8.x`.

## Layouts are function components

New applications use a single `root.html.heex` around the render pipeline.
Dynamic layouts such as `app.html.heex` are regular function components called
from templates; do not configure them as additional render-pipeline layouts.

```heex
<Layouts.app flash={@flash}>
  ...
</Layouts.app>
```

When upgrading controller layout calls, name the layout module explicitly:

```elixir
put_layout(conn, html: {MyAppWeb.Layouts, :print})
```

Module-less layouts are deprecated.

## Generate resources with inferred contexts

The context argument is optional for `phx.gen.live`, `phx.gen.html`, and
`phx.gen.json`. When omitted, the generator derives it from the plural resource
name. `phx.gen.context` can also infer a context from the schema.

```console
$ mix phx.gen.live Post posts title:string
```

Once a default generator scope is configured, `phx.gen.schema`,
`phx.gen.context`, `phx.gen.live`, `phx.gen.html`, and `phx.gen.json` emit
ownership fields and scoped context calls. Pass `--scope organization` (or the
appropriate configured name) to select a non-default scope.

See [Scopes and Authentication](scopes-and-authentication.md) before editing
the generated ownership field or removing the scope argument from a context
function.

## Use interactive project creation

`phx.new` supports an interactive mode:

```console
$ mix phx.new my_app --interactive
```

The interactive flow can collect project choices instead of requiring every
choice as a command-line flag.

## Generated themes and development settings

Tailwind-enabled projects include daisyUI-backed light, dark, and system
themes.

Generated development configuration also:

- honors the `PORT` environment variable; and
- enables HEEx `:debug_tags_location` to make rendered elements traceable to
  their template source during development.

Generated `prod.exs` enables `force_ssl` by default. Check proxy and endpoint
configuration before treating redirect behavior as an application routing
bug.

## Authentication assets

`phx.gen.auth` warns when esbuild is missing because the generated features
expect `phoenix_html.js` to be included in the JavaScript bundle. Ensure the
asset pipeline imports it, especially when replacing the generated JavaScript
tooling.

## Repository and container side effects

When Git is installed, `phx.new` initializes a repository. Account for that
side effect when generating into a directory managed by a larger repository or
by another source-control workflow.

The `--docker` option generates an image based on Debian trixie. Review native
package names and installation commands when carrying forward customization
from an older base image.

## Generated development guidance

New projects include a `mix precommit` alias for the generated pre-commit
checks.

They also include:

- an `AGENTS.md` file compatible with `usage_rules`; and
- a `usage_rules` directory used to synchronize Phoenix guidance.

Preserve or deliberately replace these files when regenerating project
scaffolding; they are part of the generated developer workflow rather than
runtime application code.
