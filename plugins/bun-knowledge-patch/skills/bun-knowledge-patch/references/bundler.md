# Bundler (`bun build`)

## Basic Usage

```sh
bun build ./app.ts --outdir=dist
bun build ./styles.css --outdir=dist     # CSS bundling
```

## Standalone Executables

```sh
bun build --compile app.ts
bun build --compile --target=bun-windows-x64 app.ts  # Cross-compile
bun build --compile --bytecode app.ts                 # Faster startup
```

### Programmatic API

```ts
await Bun.build({
  entrypoints: ["./cli.ts"],
  compile: "bun-linux-x64-musl",
});

await Bun.build({
  entrypoints: ["./app.ts"],
  compile: {
    target: "bun-windows-x64",
    outfile: "./my-app.exe",
    windows: { icon: "./icon.ico", title: "My App", version: "1.0.0" },
  },
});
```

### Embed Runtime Flags

```sh
bun build --compile --compile-exec-argv="--smol --hot" app.ts
```

### Config Autoload Control

Standalone executables skip config files by default. Opt in:

```sh
bun build --compile --compile-autoload-tsconfig --compile-autoload-package-json app.ts
bun build --compile --no-compile-autoload-dotenv --no-compile-autoload-bunfig app.ts
```

## Production HTML Builds

```sh
bun build ./index.html --production --outdir=dist
```

## Ahead-of-Time Bundling

Bundle full-stack apps where server imports HTML:

```ts
import homepage from "./index.html";
Bun.serve({ routes: { "/": homepage } });
```

```sh
bun build ./server.ts --target=bun --outdir=dist
bun build ./server.ts --compile --outfile=my-app  # Single executable
```

## Bundle Analysis

```sh
bun build entry.js --metafile=meta.json --outdir=dist
bun build entry.js --metafile-md --outdir=dist                  # LLM-friendly
bun build entry.js --metafile=meta.json --metafile-md=meta.md   # Both
```

```ts
const result = await Bun.build({
  entrypoints: ["./index.ts"],
  outdir: "./dist",
  metafile: true,  // or { json: "meta.json", markdown: "meta.md" }
});

for (const [path, meta] of Object.entries(result.metafile.outputs)) {
  console.log(`${path}: ${meta.bytes} bytes`);
}
```

## Virtual Files

Bundle with in-memory files:

```ts
await Bun.build({
  entrypoints: ["./src/index.ts"],
  files: {
    "./src/config.ts": `export const API_URL = "https://api.prod.com";`,
    "./src/generated.ts": `export const BUILD_ID = "${crypto.randomUUID()}";`,
  },
  outdir: "./dist",
});
```

## Compile-Time Feature Flags

```ts
import { feature } from "bun:bundle";

if (feature("PREMIUM")) {
  initPremiumFeatures(); // Removed when flag disabled
}
```

```sh
bun build --feature=PREMIUM --feature=DEBUG ./app.ts
bun run --feature=DEBUG ./app.ts
bun test --feature=MOCK_API
```

```ts
// Type safety (env.d.ts)
declare module "bun:bundle" {
  interface Registry {
    features: "DEBUG" | "PREMIUM" | "BETA";
  }
}
```

## Common Options

```sh
bun build --format=cjs app.ts            # CommonJS output
bun build --env="PUBLIC_*" app.ts        # Inject env vars
bun build --drop=console app.ts          # Remove function calls
bun build --packages=external app.ts     # Externalize packages
bun build --minify --keep-names app.ts   # Preserve fn/class names
```

## Plugin Hooks

```ts
await Bun.build({
  entrypoints: ["./index.ts"],
  plugins: [{
    name: "notify",
    setup(build) {
      build.onEnd((result) => {
        console.log(result.success ? "Build succeeded" : "Build failed");
      });
    },
  }],
});
```

## JSX Configuration

```ts
await Bun.build({
  entrypoints: ["./app.jsx"],
  jsx: {
    runtime: "automatic",
    importSource: "preact",
    factory: "h",
    fragment: "Fragment",
    development: false,
    sideEffects: false,
  },
});
```

Prevent JSX tree-shaking with side effects:

```json
// tsconfig.json
{ "compilerOptions": { "jsxSideEffects": true } }
```

## CSS Modules

Files with `.module.css` have locally-scoped class names:

```ts
import styles from './styles.module.css';
element.className = styles.button;
```

## `sideEffects` Glob Patterns

```json
{ "sideEffects": ["**/*.css", "./src/setup.js"] }
```

## `import.meta` in CommonJS

When building `--format=cjs`:

| ESM | CommonJS |
|-----|----------|
| `import.meta.url` | (inlined) |
| `import.meta.path` | `__filename` |
| `import.meta.dirname` | `__dirname` |

## NODE_PATH Support

```sh
NODE_PATH=./src bun build ./entry.js --outdir ./out
```
