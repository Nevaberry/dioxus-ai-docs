# New APIs

## Markdown (`Bun.markdown`)

Native CommonMark-compliant parser:

```ts
// Render to HTML
const html = Bun.markdown.html("# Hello **world**");
Bun.markdown.html("## Hello", { headingIds: true });
```

Custom rendering:

```ts
const html = Bun.markdown.render("# Title\n\nHello **world**", {
  heading: (children, { level }) => `<h${level} class="title">${children}</h${level}>`,
  paragraph: (children) => `<p>${children}</p>`,
  strong: (children) => `<b>${children}</b>`,
  image: () => null, // Return null to omit
});
```

React integration:

```tsx
function Markdown({ text }: { text: string }) {
  return Bun.markdown.react(text);
}

// Custom components
Bun.markdown.react("# Hello", {
  h1: ({ children }) => <h1 className="title">{children}</h1>,
});

// React 18 and older (default targets React 19)
Bun.markdown.react(text, { reactVersion: 18 });
```

GFM extensions enabled by default. Options: `wikiLinks`, `latexMath`, `headingIds`, `autolinkHeadings`.

## YAML (`Bun.YAML`)

```ts
import { YAML } from "bun";

const data = YAML.parse("key: value\nitems:\n  - a\n  - b");
YAML.stringify({ name: "app", version: "1.0" });

// Direct import
import config from "./config.yaml";
```

## JSON5 (`Bun.JSON5`)

Comments, trailing commas, unquoted keys:

```ts
const config = Bun.JSON5.parse(`{
  // Comment
  host: 'localhost',
  port: 5432,
}`);

Bun.JSON5.stringify({ name: "app" });

import settings from "./config.json5";
```

## JSONC (`Bun.JSONC`)

JSON with comments (tsconfig.json, VS Code settings):

```ts
const config = Bun.JSONC.parse(`{
  // Database config
  "host": "localhost",
  "options": { "ssl": true, }  // trailing comma OK
}`);
```

## JSONL (`Bun.JSONL`)

Newline-delimited JSON:

```ts
const records = Bun.JSONL.parse('{"a":1}\n{"b":2}\n');

// Streaming
let buffer = "";
for await (const chunk of stream) {
  buffer += chunk;
  const result = Bun.JSONL.parseChunk(buffer);
  for (const value of result.values) handleRecord(value);
  buffer = buffer.slice(result.read);
}
```

## Archive (`Bun.Archive`)

Create and extract tar archives:

```ts
const archive = new Bun.Archive({
  "hello.txt": "Hello, World!",
  "data.json": JSON.stringify({ foo: "bar" }),
});

await archive.blob();
await archive.bytes();
await archive.extract("./output-dir");

// With compression
const compressed = new Bun.Archive(files, { compress: "gzip", level: 12 });

// Extract existing tarball
const tarball = new Bun.Archive(await Bun.file("package.tar.gz").bytes());
await tarball.extract("./output");

// Write to file or S3
await Bun.write("archive.tar.gz", compressed);
```

## Terminal (`Bun.Terminal`)

PTY support for interactive programs:

```ts
const proc = Bun.spawn(["bash"], {
  terminal: {
    cols: 80,
    rows: 24,
    data(terminal, data) {
      process.stdout.write(data);
      if (data.includes("$")) terminal.write("exit\n");
    },
  },
});
await proc.exited;
proc.terminal.close();

// Reusable terminal
await using terminal = new Bun.Terminal({
  cols: 80,
  rows: 24,
  data(term, data) { process.stdout.write(data); },
});
Bun.spawn(["echo", "hello"], { terminal });
```

Methods: `write()`, `resize(cols, rows)`, `setRawMode()`, `ref()`/`unref()`, `close()`. POSIX only.

## Secrets (`Bun.secrets`)

OS-native credential storage:

```ts
import { secrets } from "bun";

await secrets.set({ service: "my-cli", name: "api-key", value: "secret123" });
const key = await secrets.get({ service: "my-cli", name: "api-key" });
await secrets.delete({ service: "my-cli", name: "api-key" });
```

## Compression

### Zstandard

```ts
const compressed = Bun.zstdCompressSync("hello world", { level: 5 });
const decompressed = Bun.zstdDecompressSync(compressed);

// Async
const compressed = await Bun.zstdCompress("hello world");
```

### CompressionStream with Brotli/Zstd

```ts
// Standard: "gzip", "deflate", "deflate-raw"
// Bun additions: "brotli", "zstd"
const compressed = response.body.pipeThrough(new CompressionStream("zstd"));
const decompressed = compressed.pipeThrough(new DecompressionStream("zstd"));
```

## Text Utilities

### Color

```ts
Bun.color("#ff0000", "css");  // "red"
Bun.color("red", "ansi");     // "\x1b[31m"
Bun.color("red", "{rgba}");   // { r: 255, g: 0, b: 0, a: 1 }
```

### ANSI

```ts
Bun.stripANSI("\u001b[31mRed\u001b[0m text"); // "Red text"

Bun.wrapAnsi(text, 20, {
  hard: false,
  wordWrap: true,
  trim: true,
});
```

### String Width

```ts
Bun.stringWidth("hello 👋"); // Accurate terminal width
```

## Other Utilities

```ts
// UUID v7 (sortable)
Bun.randomUUIDv7(); // "0192ce11-26d5-7dc3-..."

// Table formatting
Bun.inspect.table([{ a: 1 }, { a: 2 }]);

// Hashing
Bun.hash.rapidhash("hello world"); // BigInt
Bun.hash.crc32("data");

// File operations
await Bun.file("./file.txt").delete();
const stat = await Bun.file("./file.txt").stat();

// DNS
import { dns } from "bun";
dns.prefetch("example.com");
dns.getCacheStats();

// Embedded files in compiled executables
for (const file of Bun.embeddedFiles) { console.log(file.name); }
```

## URLPattern

```ts
const pattern = new URLPattern({ pathname: "/users/:id" });
pattern.test("https://example.com/users/123"); // true
pattern.exec("https://example.com/users/123").pathname.groups.id; // "123"
```
