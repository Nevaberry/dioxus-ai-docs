# Modules and Transforms

## Native ESM and TypeScript

Native ESM execution supports `import.meta.*` and `file://`. Jest configuration
files may be TypeScript, and `.mts` and `.cts` work without extra extension
configuration. When Node's native TypeScript type stripping is active, Jest no
longer loads a transformer solely to strip types. (30-guide)

`babel-jest` can collect coverage from `.mts` and `.cts` files. (30.4.0)

## Requiring ES modules

On Node 24.9 and newer, Jest supports `require()` of ES modules. A `.js` file
containing ESM syntax may fall back to native ESM without a `"type": "module"`
marker. That fallback also applies when the CommonJS parser rejects the file
during `require()`. (30.4.0)

## CommonJS imported from ESM

The final interop rules are: (30.4.0)

- The entire `module.exports` value is always the default export.
- Jest does not apply Babel-style `__esModule` default unwrapping.
- Named imports include own properties attached to a function assigned to
  `module.exports`.
- Importers share the same CommonJS singleton.

For example:

```js
function main() {}
function helper() {}
module.exports = Object.assign(main, {helper});
// ESM: import main, {helper} from './module.cjs';
```

Audit code that expected the old `__esModule` unwrapping behavior, particularly
code that reads or mocks a CommonJS default export.

## Import attributes

Jest validates TC39 import attributes on ESM imports. JSON imports can use the
`with {type: 'json'}` form: (30.4.0)

```js
import data from './data.json' with {type: 'json'};
```

## Babel transformer configuration

Set `excludeJestPreset` when `babel-jest` must not automatically apply
`babel-preset-jest`: (30.0.0)

```js
export default {
  transform: {
    '^.+\\.[jt]sx?$': ['babel-jest', {excludeJestPreset: true}],
  },
};
```

`babel-jest` exports the public `TransformerConfig` interface for TypeScript
integrations that need to type transformer configuration. (30.1-30.3)

## Custom JSDOM environments

`@jest/environment-jsdom-abstract` abstracts the JSDOM environment so a custom
JSDOM version can be used. Support for JSDOM 27 is available for custom
JSDOM-based test environments. (30.0.0; 30.1-30.3)

The standard `jest-environment-jsdom` uses JSDOM 26 rather than 21; review DOM
behavior changes separately from any custom-environment version choice.
(30-guide)

## Resolution through `require.resolve`

`moduleNameMapper` applies when resolving modules via `require.resolve()` with
the `paths` option. Mapped modules should therefore resolve consistently in
this path-aware form as well as in ordinary module loading. (30.4.0)

