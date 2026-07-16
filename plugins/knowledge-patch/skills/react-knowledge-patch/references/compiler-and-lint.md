# Compiler and Hooks Lint

The compiler behavior is attributed to `compiler-1.0.0`; the ESLint v6 configuration shipped with the React 19.2 tooling updates.

## Dependency tracking

Compiler 1.0 can track optional-chain accesses and indexed reads as memoization dependencies. Keep idiomatic expressions such as this intact:

```jsx
const selectedName = users[selected]?.profile?.name;
```

These reads can participate directly in generated memoization; they do not need to be rewritten merely to make dependency tracking work.

## Consolidated lint plugin

Compiler linting moved into the Hooks plugin. Remove `eslint-plugin-react-compiler` and install the current Hooks plugin:

```sh
npm remove eslint-plugin-react-compiler
npm install --save-dev eslint-plugin-react-hooks@latest
```

The Hooks plugin's recommended preset includes compiler-powered linting, and linting does not require `babel-plugin-react-compiler` to be installed. The plugin also exposes compiler-powered rules for projects that opt into additional checks.

## ESLint flat config

In v6, `recommended` is a flat-config preset:

```js
// eslint.config.js
import reactHooks from "eslint-plugin-react-hooks";

export default [
  reactHooks.configs.recommended,
];
```

An eslintrc project must use the explicitly named legacy preset:

```yaml
extends:
  - plugin:react-hooks/recommended-legacy
```

Do not leave an eslintrc project on `plugin:react-hooks/recommended` after upgrading to v6.

## Starter defaults

Compiler adoption differs across starters:

- Expo SDK 54 and newer enable the compiler by default for newly created applications.
- `create-vite` offers a compiler-enabled choice.
- `create-next-app` offers a compiler-enabled choice.

## Upgrade policy

Compiler releases can change memoization boundaries. Those changes can expose latent Rules-of-React violations, especially through different Effect dependency behavior.

When end-to-end coverage is not strong enough to detect behavioral changes, save the compiler package at an exact version instead of accepting a SemVer range:

```sh
npm install --save-dev --save-exact babel-plugin-react-compiler@1.0.0
```

Test each compiler upgrade manually before updating the pin.
