# Interoperability and Portability

## Run Elixir in the browser

### Popcorn on AtomVM WebAssembly

Popcorn runs an extensive Elixir subset in a browser on AtomVM's WebAssembly
target. A process can register through `Popcorn.Wasm` and invoke JavaScript
directly (`interop-and-portability`):

```elixir
def init(_) do
  Popcorn.Wasm.register(:main)
  Popcorn.Wasm.run_js("""() => { document.body.textContent = "Hello"; }""")
  :ignore
end
```

Choose it when an AtomVM-compatible subset and direct JavaScript calls fit the
application.

### Hologram client-side components

Hologram is a Phoenix-based isomorphic framework that transpiles Elixir syntax
trees to JavaScript. It provides components, routing, templates, and
client-server communication. Components use `~HOLO` templates and can dispatch
browser events to `action/3` entirely on the client:

```elixir
def template, do: ~HOLO"""<svg $pointer_down="start_drawing"></svg>"""

def action(:start_drawing, _params, component) do
  put_state(component, :drawing?, true)
end
```

## Write native functions

### C++ with Fine

Fine wraps the C++ NIF API and converts arguments and return values from the
function signature. It supports Elixir structs and turns C++ exceptions into
Elixir exceptions (`interop-and-portability`):

```cpp
#include <fine.hpp>

int64_t add(ErlNifEnv *env, int64_t a, int64_t b) { return a + b; }
FINE_NIF(add, 0);
FINE_INIT("Elixir.Example");
```

### Inline Zig with Zigler

Zigler compiles embedded Zig at build time without separate build scripts or
glue. `mix format` formats the Zig, IEx `h` exposes its documentation, and the
functions appear directly on the Elixir module:

```elixir
Mix.install([:zigler])

defmodule Example do
  use Zig, otp_app: :zigler

  ~Z"""
  pub fn add(a: i64, b: i64) i64 { return a + b; }
  """
end
```

## Embed Python

Pythonx runs Python in the same OS process, converts Elixir and Python values,
and can provision Python plus packages from a `uv` project declaration
(`interop-and-portability`):

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

Regular Python execution remains serialized by the GIL across Elixir
processes. Native packages may release it during CPU-intensive work or I/O.

## Join the Erlang distribution from Swift

The Swift Erlang Actor System lets a Swift program communicate with Erlang and
Elixir as a distributed node. It is a newer alternative to implementing the
distribution protocol directly (`interop-and-portability`).
