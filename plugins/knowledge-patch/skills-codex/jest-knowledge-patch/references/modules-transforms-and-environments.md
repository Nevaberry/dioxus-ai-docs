# Modules, transforms, and environments

Use this reference when configuring ESM, CommonJS interop, TypeScript, Babel,
JSON imports, or custom JSDOM environments.

## Native ESM and TypeScript

Native ESM execution supports `import.meta.*` and `file://` URLs. Jest
configuration files can be written in TypeScript, and `.mts` and `.cts` work
without additional extension configuration.

When Node.js native TypeScript type stripping is active, Jest does not load a
transformer merely to remove types. Do not assume a configured transformer ran
just because a TypeScript file executed.

## Requiring ES modules

On Node.js 24.9 and newer, Jest supports `require()` of ES modules. A `.js`
file containing ESM syntax can fall back to native ESM without a
`"type": "module"` marker, including when the CommonJS parser rejects the file
during `require()`.

Test this fallback on the actual Node.js version used by CI. Older runtimes
must not be expected to provide the same `require()` behavior.

## CommonJS imported from ESM

The final interop semantics in `30.4.0` are:

- the complete `module.exports` value is always the default export;
- Jest does not perform Babel-style `__esModule` default unwrapping;
- named imports include own properties attached to a function assigned to
  `module.exports`;
- importers share the same CommonJS singleton.

For example:

```js
function main() {}
function helper() {}
module.exports = Object.assign(main, {helper});
```

An ESM consumer can use:

```js
import main, {helper} from './module.cjs';
```

If old tests expected `exports.default` to be unwrapped because
`__esModule` was set, update the expectation to the complete
`module.exports` value.

## Import attributes

Jest validates TC39 import attributes on ESM imports. JSON modules use:

```js
import data from './data.json' with {type: 'json'};
```

Use `with`, include the correct `type`, and treat invalid attributes as module
loading errors rather than transformer failures.

## Babel preset behavior

`babel-jest` normally applies `babel-preset-jest`. Set `excludeJestPreset` when
the project deliberately needs to opt out:

```js
export default {
  transform: {
    '^.+\\.[jt]sx?$': ['babel-jest', {excludeJestPreset: true}],
  },
};
```

Opting out can remove transformations or hoisting supplied by the preset, so
run mock-hoisting and syntax tests after enabling it.

In `30.0.0`, both `babel-jest` and `babel-preset-jest` declare
`@babel/core` with peer range `^7.11`. Resolve peer-dependency failures by
installing a compatible Babel core rather than bypassing the package manager.

## Babel integration types and coverage

`babel-jest` exports the `TransformerConfig` interface. TypeScript transformer
integrations should import this public type instead of reaching into internal
paths or maintaining a duplicate interface.

`babel-jest` collects coverage from `.mts` and `.cts`. Verify that collection
patterns include the files and that an unrelated ignore rule is not excluding
them.

## Bundled and custom JSDOM

The bundled `jest-environment-jsdom` uses JSDOM 26, up from JSDOM 21. This can
change observable DOM behavior; `window.location` mocks deserve explicit
review.

`@jest/environment-jsdom-abstract` provides the abstraction for environments
that need a custom JSDOM version. It later gained JSDOM 27 support in the
`30.1-30.3` update. This does not change the bundled environment to JSDOM 27;
it enables a custom environment to supply it.

When selecting a custom JSDOM:

1. Extend the abstract environment package.
2. Pin a compatible JSDOM implementation.
3. Test globals, URLs, navigation, serialization, and teardown.
4. Keep environment-specific expectations out of Node-only projects.

## Module and environment checklist

- Confirm the Node.js version before relying on ESM `require()`.
- Verify whether Node or a transformer strips TypeScript.
- Test `import.meta.*` and `file://` behavior in native ESM.
- Update CommonJS default-import expectations.
- Check named imports attached to function exports.
- Confirm all importers observe one CommonJS singleton.
- Use and validate JSON import attributes.
- Opt out of the Jest Babel preset only deliberately.
- Satisfy the Babel core peer range.
- Import `TransformerConfig` from `babel-jest`.
- Collect coverage from `.mts` and `.cts`.
- Distinguish bundled JSDOM 26 from custom JSDOM 27 support.
- Re-test `window.location` mocks and environment teardown.
