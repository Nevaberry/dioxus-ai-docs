# Compiler and Hooks Lint

## Configure Hooks ESLint v6

Since `19.2.0`, the v6 `recommended` preset uses ESLint flat config. Existing
eslintrc projects must opt into the legacy preset explicitly:

```yaml
extends:
  - plugin:react-hooks/recommended-legacy
```

The Hooks plugin offers React Compiler-powered rules. With Compiler 1.0
(`compiler-1.0.0`), remove `eslint-plugin-react-compiler`, install
`eslint-plugin-react-hooks@latest`, and use its `recommended` preset, which
includes the compiler-powered rules. Linting does not require the compiler
package itself to be installed.

## Use optional chains and indexed reads directly

Compiler 1.0 (`compiler-1.0.0`) tracks optional-chain accesses and array
indices as memoization dependencies. Idiomatic reads can participate directly
in generated memoization:

```jsx
const selectedName = users[selected]?.profile?.name;
```

## Know starter defaults

Compiler 1.0 starter behavior (`compiler-1.0.0`) differs by platform:

- New Expo projects on SDK 54 and newer enable the compiler by default.
- `create-vite` and `create-next-app` offer compiler-enabled choices rather
  than enabling it unconditionally.

Check the generated project configuration instead of assuming every starter
uses the same default.

## Pin upgrades when behavior lacks coverage

Compiler releases can change memoization boundaries. Those changes can expose
latent Rules-of-React violations by changing Effect dependency behavior. If
the application lacks strong end-to-end coverage, pin the Compiler 1.0 package
to an exact version and test upgrades manually (`compiler-1.0.0`):

```sh
npm install --save-dev --save-exact babel-plugin-react-compiler@1.0.0
```
