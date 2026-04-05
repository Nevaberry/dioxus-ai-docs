# React Plugin v6

`@vitejs/plugin-react` v6 (shipped with Vite 8.0) uses Oxc instead of Babel for React Refresh — Babel is no longer a dependency.

## Basic Usage

```js
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

## React Compiler Support

For React Compiler support, use the new `reactCompilerPreset` with `@rolldown/plugin-babel`:

```js
import react from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { reactCompilerPreset } from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset] }),
  ],
})
```
