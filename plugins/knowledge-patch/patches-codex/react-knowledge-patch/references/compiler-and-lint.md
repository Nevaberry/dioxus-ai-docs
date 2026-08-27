# Compiler and Hooks Lint

Compiler behavior is attributed to batch `compiler-1.0.0`; the Hooks ESLint v6 configuration change is attributed to `19.2.0`.

## Track optional chains and indexed reads

Compiler 1.0 can track optional-chain accesses and array indices as memoization dependencies. These reads can participate directly in generated memoization:

```jsx
const selectedName = users[selected]?.profile?.name;
```

## Consolidate compiler linting in the Hooks plugin

Remove `eslint-plugin-react-compiler` and use `eslint-plugin-react-hooks@latest`. The Hooks plugin contains the compiler-powered rules, its `recommended` preset incorporates compiler linting, and linting does not require the compiler itself to be installed. The plugin's compiler-powered rules are also available for explicit configuration.

Hooks ESLint v6 changed `recommended` into an ESLint flat-config preset. Existing eslintrc projects must choose the legacy preset explicitly:

```yaml
extends:
  - plugin:react-hooks/recommended-legacy
```

## Account for starter defaults

New Expo projects on SDK 54 or newer enable the compiler by default. Vite and Next.js do not make it unconditional; `create-vite` and `create-next-app` offer compiler-enabled starter choices.

Check the generated project configuration instead of assuming that all starters use the same default.

## Pin compiler upgrades when coverage is weak

Compiler releases can change memoization boundaries. Those changes may expose latent Rules-of-React violations by changing Effect dependency behavior.

When strong end-to-end coverage is unavailable, save an exact compiler version instead of a SemVer range and test each upgrade manually:

```sh
npm install --save-dev --save-exact babel-plugin-react-compiler@1.0.0
```
