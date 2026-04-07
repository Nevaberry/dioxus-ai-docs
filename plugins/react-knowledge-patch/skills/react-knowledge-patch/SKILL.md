---
name: react-knowledge-patch
description: "React changes since training cutoff (latest: 19.2.0) — Activity component, cacheSignal, Partial Pre-rendering, prerender/resume APIs, eslint-plugin-react-hooks v6. Load before working with React."
version: "19.2.0"
license: MIT
metadata:
  author: Nevaberry
---

# React Knowledge Patch

Claude Opus 4.6 knows React through 18.x. It is **unaware** of the features below, which cover React 19.0 through 19.2 (released 2025-10-01).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Server rendering APIs | [references/server-rendering.md](references/server-rendering.md) | cacheSignal, prerender, resume, resumeAndPrerender, Partial Pre-rendering |

---

## `<Activity />`

New component for pre-rendering and preserving state of hidden UI. Replaces conditional rendering with mode-based visibility.

```jsx
// Instead of: {isVisible && <Page />}
<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <Page />
</Activity>;
```

### Mode behavior

| Mode | Children | Effects | Updates |
|---|---|---|---|
| `visible` | Shown | Mounted | Processed normally |
| `hidden` | Hidden | Unmounted | Deferred until React is idle |

### When to use

- Pre-rendering likely navigation targets (e.g., next page in a wizard)
- Preserving state on back navigation (e.g., tab content, scroll position)
- Keeping off-screen content ready without the cost of full rendering

Unlike conditional rendering (`{show && <Component />}`), `<Activity>` preserves component state and DOM when toggling between modes. Hidden children are deprioritized but not destroyed.

---

## eslint-plugin-react-hooks v6

Now uses ESLint flat config by default.

```js
// eslint.config.js (flat config, v6 default)
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  reactHooks.configs.recommended,
];
```

For legacy `.eslintrc` config, change the extends name:

```diff
- extends: ['plugin:react-hooks/recommended']
+ extends: ['plugin:react-hooks/recommended-legacy']
```

---

## Reference Files

| File | Contents |
|---|---|
| [server-rendering.md](references/server-rendering.md) | cacheSignal for RSC, Partial Pre-rendering (prerender, resume, resumeAndPrerender), Node stream variants |
