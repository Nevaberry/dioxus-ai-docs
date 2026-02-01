# Runtime & CLI

## Spawn Options

### Timeout

```ts
const result = Bun.spawnSync({
  cmd: ["sleep", "1000"],
  timeout: 1000, // ms
});
result.exitedDueToTimeout; // true
```

### maxBuffer

```ts
Bun.spawnSync({
  cmd: ["yes"],
  maxBuffer: 1024, // Kill if output exceeds 1KB
});
```

### Socket Properties

```ts
Bun.connect({
  hostname: "example.com",
  port: 443,
  socket: {
    open(socket) {
      socket.localAddress;   // "10.0.0.53"
      socket.localFamily;    // "IPv4"
      socket.remoteAddress;  // "93.184.216.34"
      socket.remotePort;     // 443
    },
    data() {},
  },
});
```

## UDP Sockets

```ts
const socket = await Bun.udpSocket({
  socket: { data(socket, data, port, addr) { } },
});
socket.send("Hello", port, "127.0.0.1");
socket.sendMany([["msg1", port1, addr1], ["msg2", port2, addr2]]);
```

## C Compilation

Compile and run C code using embedded TinyCC:

```ts
import { cc } from "bun:ffi";

const { symbols: { add } } = cc({
  source: "./math.c",
  symbols: { add: { args: ["int", "int"], returns: "int" } },
});
add(1, 2); // 3
```

## child_process.fork with execArgv

```ts
import { fork } from "child_process";

const child = fork("./child.js", {
  execArgv: ["--smol", "--hot"],
});
```

## Profiling

```sh
bun --cpu-prof script.js                    # Chrome DevTools .cpuprofile
bun --cpu-prof-md script.js                 # Markdown report
bun --cpu-prof --cpu-prof-dir ./profiles script.js

bun --heap-prof script.js                   # .heapsnapshot
bun --heap-prof-md script.js                # Markdown report
```

## Fetch Proxy

```ts
fetch(url, {
  proxy: {
    url: "http://proxy.example.com:8080",
    headers: { "Proxy-Authorization": "Bearer token" },
  },
});
```

## Environment Variables

```sh
BUN_OPTIONS="--bun --config='./config.toml'" bun run dev.ts
```

## CLI Flags

| Flag | Purpose |
|------|---------|
| `--unhandled-rejections=throw\|strict\|warn\|none` | Promise rejection handling |
| `--console-depth=N` | console.log inspection depth |
| `--no-env-file` | Disable .env loading |
| `--no-addons` | Disable Node.js native addons |
| `--user-agent "MyApp/1.0"` | Set fetch User-Agent |
| `--use-system-ca` | Use OS trusted certificates |

## bunfig.toml

```toml
[run]
console.depth = 4

env = false  # Disable .env autoload
```

## bunx

```sh
bunx --package renovate renovate-config-validator
bunx -p @angular/cli ng new my-app
```

## bun init

```sh
bun init --react
bun init --react=tailwind
bun init --react=shadcn
```

## Async Stack Traces

Stack traces now include async call frames:

```
error: oops
      at baz (async.js:11:13)
      at async bar (async.js:6:16)
      at async foo (async.js:2:16)
```
