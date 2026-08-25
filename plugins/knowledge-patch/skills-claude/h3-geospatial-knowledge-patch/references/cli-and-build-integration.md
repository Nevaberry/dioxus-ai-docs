# CLI and native build integration

## Scriptable `h3` command

The `h3` binary (since 4.2.0) is intended for shell automation.

Region commands include:

- `polygonToCells`;
- `maxPolygonToCellsSize`;
- `cellsToMultiPolygon`.

Polygon input can come from:

| Source | Option |
| --- | --- |
| Inline argument | `-p '<polygon>'` |
| File | `-i <path>` |
| Standard input | `-i --` |

Example:

```sh
h3 polygonToCells \
  -r 7 \
  -p '[[37.813319,-122.408987],[37.719806,-122.354474],[37.815157,-122.479877]]' \
  -f newline
```

`polygonToCells` requires a resolution from 0 through 15. It supports JSON and
newline output formats.

The experimental polygon conversion functions are not exposed through this
CLI. Use an appropriate language binding when a non-center containment mode or
the experimental conversion algorithm is required.

Other relevant commands are:

```sh
h3 gridRing -c <cell> -k <distance>
h3 getIndexDigit -c <index> -r <res>
h3 constructCell -b <base> -d <digits> [-r <resolution>]
h3 reverseDirectedEdge -e <edge>
```

## Configurable CMake install directory

H3 honors `CMAKE_INSTALL_LIBDIR` for the installed library directory (since
4.2.0). Packagers can select a platform-appropriate path such as `lib64`:

```sh
cmake -S . -B build -DCMAKE_INSTALL_LIBDIR=lib64
```

## pkg-config discovery

H3 installs `h3.pc` (since 4.5.0). Native builds can retrieve the compiler and
linker flags through pkg-config:

```sh
pkg-config --cflags --libs h3
```
