# CLI Automation and Native Packaging

## Scriptable `h3` CLI (since 4.2.0)

H3 ships an `h3` binary designed for shell scripts. Region-related commands
include:

- `polygonToCells`
- `maxPolygonToCellsSize`
- `cellsToMultiPolygon`

`polygonToCells` requires a resolution in the inclusive range 0 through 15.
It supports JSON and newline output.

```sh
h3 polygonToCells -r 7 \
  -p '[[37.813319,-122.408987],[37.719806,-122.354474],[37.815157,-122.479877]]' \
  -f newline
```

Polygon input options:

| Source | Option |
| --- | --- |
| Inline argument | `-p <polygon>` |
| File | `-i <path>` |
| Standard input | `-i --` |

The experimental polygon conversion functions are not available through the
CLI.

Additional commands associated with newer core APIs are:

```sh
h3 gridRing -c <cell> -k <distance>
h3 getIndexDigit -c <index> -r <res>
h3 constructCell -b <base> -d <digits> [-r <resolution>]
h3 reverseDirectedEdge -e <edge>
```

## Configurable CMake library directory (since 4.2.0)

The CMake installation honors `CMAKE_INSTALL_LIBDIR` when choosing the
installed library directory. Packagers can select a platform-specific path
such as `lib64` without patching the project:

```sh
cmake -S . -B build -DCMAKE_INSTALL_LIBDIR=lib64
```

## pkg-config metadata (since 4.5.0)

Native installation includes `h3.pc`. Build scripts can obtain compiler and
linker flags through pkg-config:

```sh
pkg-config --cflags --libs h3
```

Prefer this discovery path to hard-coded include and library directories when
the target environment provides pkg-config.
