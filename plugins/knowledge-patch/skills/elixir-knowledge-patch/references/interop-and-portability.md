# Interoperability and Portability

Batch attribution: `interop-and-portability`.

## Run Elixir-facing code in browsers

### Use Popcorn on AtomVM WebAssembly

Popcorn runs an extensive Elixir subset in the browser on AtomVM's WebAssembly target. Register a process through `Popcorn.Wasm` and invoke JavaScript directly:

```elixir
def init(_) do
  Popcorn.Wasm.register(:main)
  Popcorn.Wasm.run_js("""() => { document.body.textContent = "Hello"; }""")
  :ignore
end
```

Choose it when the AtomVM-compatible subset and direct process-to-JavaScript bridge fit the application.

### Build isomorphic Phoenix interfaces with Hologram

Hologram transpiles Elixir syntax trees to JavaScript and supplies Phoenix-based components, routing, templates, and client/server communication. Use `~HOLO` templates and handle browser events in client-side `action/3` callbacks:

```elixir
def template, do: ~HOLO"""<svg $pointer_down="start_drawing"></svg>"""

def action(:start_drawing, _params, component) do
  put_state(component, :drawing?, true)
end
```

## Implement native functions

### Wrap C++ NIFs with Fine

Fine derives NIF argument and return conversion from a C++ function signature. It supports Elixir structs and converts C++ exceptions into Elixir exceptions:

```cpp
#include <fine.hpp>

int64_t add(ErlNifEnv *env, int64_t a, int64_t b) { return a + b; }
FINE_NIF(add, 0);
FINE_INIT("Elixir.Example");
```

### Embed Zig with Zigler

Zigler compiles embedded Zig during the Elixir build without separate build scripts or glue. The resulting functions are exposed on the Elixir module. `mix format` formats the Zig, and IEx's `h` helper displays its documentation:

```elixir
Mix.install([:zigler])

defmodule Example do
  use Zig, otp_app: :zigler

  ~Z"""
  pub fn add(a: i64, b: i64) i64 { return a + b; }
  """
end
```

## Embed other language runtimes

### Run Python in-process with Pythonx

Pythonx embeds Python in the same operating-system process, converts values between Python and Elixir, and provisions Python plus packages from a `uv` project declaration:

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

Ordinary Python execution remains serialized by the GIL across Elixir processes. Native packages can release the GIL during CPU-intensive work or I/O.

### Connect Swift as a distributed node

Use the Swift Erlang Actor System to let Swift programs communicate with Erlang and Elixir as distributed nodes. It is a newer alternative to implementing the distribution protocol directly.
