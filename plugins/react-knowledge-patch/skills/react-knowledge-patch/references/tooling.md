# Tooling Changes

## eslint-plugin-react-hooks v6

*Released with React 19.2 (2025-10-01)*

### Breaking change: flat config by default

The default export is now ESLint flat config format (for `eslint.config.js`). The legacy `.eslintrc` format requires a new import path.

### ESLint flat config (default)

```js
// eslint.config.js
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  reactHooks.configs.recommended,
  // ... other configs
];
```

### Legacy .eslintrc config

```diff
- extends: ['plugin:react-hooks/recommended']
+ extends: ['plugin:react-hooks/recommended-legacy']
```

The `recommended-legacy` preset provides identical rules in the legacy config format.

### React Compiler rules

The `recommended` preset now includes opt-in rules powered by the React Compiler. These rules perform deeper analysis of hook dependencies and component purity beyond what the traditional `rules-of-hooks` and `exhaustive-deps` rules check.
