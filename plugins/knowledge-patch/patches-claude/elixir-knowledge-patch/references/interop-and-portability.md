# Interoperability and Portability

## Browser Elixir (`interop-and-portability`)

### Popcorn on AtomVM WebAssembly

Popcorn runs an extensive Elixir subset in the browser on AtomVM's WebAssembly
target. A process can register with `Popcorn.Wasm` and call JavaScript directly.

```elixir
def init(_) do
  Popcorn.Wasm.register(:main)
  Popcorn.Wasm.run_js("""() => { document.body.textContent = "Hello"; }""")
  :ignore
end
```

Choose Popcorn when the AtomVM-compatible subset is sufficient and direct
browser execution is the goal.

### Hologram client-side components

Hologram is a Phoenix-based isomorphic framework. It transpiles Elixir syntax
trees to JavaScript and supplies components, routing, templates, and
client-server communication. Components render `~HOLO` templates and dispatch
browser events to `action/3` entirely on the client.

```elixir
def template, do: ~HOLO"""<svg $pointer_down="start_drawing"></svg>"""

def action(:start_drawing, _params, component) do
  put_state(component, :drawing?, true)
end
```

Choose Hologram when Phoenix integration and isomorphic components matter more
than an embedded VM subset.

## Native extensions (`interop-and-portability`)

### Fine for C++ NIFs

Fine wraps the C++ NIF API and derives argument and return conversion from the
function signature. It supports Elixir structs and turns C++ exceptions into
Elixir exceptions.

```cpp
#include <fine.hpp>

int64_t add(ErlNifEnv *env, int64_t a, int64_t b) { return a + b; }
FINE_NIF(add, 0);
FINE_INIT("Elixir.Example");
```

### Zigler for inline Zig NIFs

Zigler compiles embedded Zig at build time without separate build scripts or
glue. `mix format` formats the Zig, its documentation appears through IEx `h`,
and generated functions are exposed directly on the Elixir module.

```elixir
Mix.install([:zigler])

defmodule Example do
  use Zig, otp_app: :zigler

  ~Z"""
  pub fn add(a: i64, b: i64) i64 { return a + b; }
  """
end
```

## Embedded Python (`interop-and-portability`)

Pythonx embeds Python in the Elixir OS process, converts Python and Elixir data,
and provisions Python and packages from a `uv` project declaration.

```elixir
Mix.install([{:pythonx, "~> 0.4.0"}])
Pythonx.uv_init("""
[project]
name = "myapp"
version = "0.0.0"
requires-python = "==3.13.*"
dependencies = ["numpy==2.2.2"]
""")

import Pythonx, only: :sigils
x = 1
~PY"""
import numpy as np
np.int64(x) + np.int64(2)
"""
```

Ordinary Python execution remains serialized by the GIL across Elixir
processes. Native packages may release the GIL during CPU-intensive work or I/O.

## Swift distributed nodes (`interop-and-portability`)

The Swift Erlang Actor System lets Swift programs communicate with Erlang and
Elixir as distributed nodes. Prefer it over implementing the distribution
protocol directly when a Swift program must join the cluster.
