# Developer Tooling

## Lint Plugin API (2.2+, unstable)

Extend `deno lint` with custom rules via `Deno.lint.Plugin`. Configure in deno.json:
```json
{ "lint": { "plugins": ["./my-plugin.ts", "jsr:@scope/plugin", "npm:@scope/plugin"] } }
```
```ts
export default {
  name: "my-plugin",
  rules: {
    "no-foo": {
      create(context) {
        return {
          // Visitor-based API (ESLint-like)
          VariableDeclarator(node) {
            if (node.id.type === "Identifier" && node.id.name === "foo") {
              context.report({ node, message: "Don't use foo" });
            }
          },
          // CSS-selector syntax also supported
          'VariableDeclarator[id.name="bar"]'(node) {
            context.report({ node, message: "Don't use bar" });
          },
        };
      },
    },
  },
} satisfies Deno.lint.Plugin;
```
Requires `--unstable` flag. Full types under `Deno.lint` namespace.

## `deno fmt` Tagged Template Formatting (2.3+)

Formats embedded CSS, HTML, and SQL inside tagged templates (e.g., `` html`...` ``, `` css`...` ``, `` sql`...` ``). SQL formatting requires `--unstable-sql`. Also adds 14 new formatter options (e.g., `useBraces`, `trailingCommas`, `quoteProps`).

## New Default Lint Rules (2.5+)

- `no-unversioned-import` (recommended set): requires version in `npm:`/`jsr:` specifiers.
- `no-import-prefix` (workspace set): disallows inline `npm:`/`jsr:`/`https:` imports when deno.json/package.json exists — use import maps instead.
