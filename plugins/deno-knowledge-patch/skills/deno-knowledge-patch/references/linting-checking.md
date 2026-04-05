# Linting & Type Checking

## Lint Plugin System (2.2+, unstable)

Register plugins in `deno.json` under `lint.plugins`. Plugins use an ESLint-like visitor API typed as `Deno.lint.Plugin`.

```jsonc
// deno.json
{ "lint": { "plugins": ["./my-plugin.ts", "jsr:@scope/plugin", "npm:@scope/plugin"] } }
```

```ts
export default {
  name: "my-plugin",
  rules: {
    "no-foo": {
      create(context) {
        return {
          // Visitor-based or CSS selector: 'VariableDeclarator[id.name="foo"]'
          VariableDeclarator(node) {
            if (node.id.type === "Identifier" && node.id.name === "foo") {
              context.report({ node, message: "Use a descriptive name" });
            }
          },
        };
      },
    },
  },
} satisfies Deno.lint.Plugin;
```

## New Default Lint Rules (2.5+)

- `no-unversioned-import` (recommended set): requires version in `npm:` and `jsr:` specifiers
- `no-import-prefix` (workspace set): disallows inline `npm:`, `jsr:`, `https:` imports — use import map entries instead

## `--unstable-tsgo` (2.6+)

Use Go-based TypeScript checker for faster type checking:

```bash
deno check --unstable-tsgo main.ts
# or
DENO_UNSTABLE_TSGO=1 deno check main.ts
```

## `--check-js` (2.7+)

Type-check JS files without config: `deno check --check-js main.js`.

## `deno fmt --fail-fast` (2.7+)

Stop formatting on first error: `deno fmt --check --fail-fast`.
