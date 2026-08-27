# Linux Build and Rendering Tests

Use this reference for local OpenGL development builds, image rendering on
desktop or headless hosts, and render-fixture investigation.

## OpenGL development build

On Ubuntu 22.04 or later, clone submodules and configure the `linux-opengl`
preset. It builds the GLFW development tools and can produce static libraries
for other C++ projects.

The preset defaults to Wayland and therefore needs `libegl1-mesa-dev`.
`libsqlite3-dev` is optional because the build can supply SQLite itself.

```bash
git clone --recurse-submodules -j8 https://github.com/maplibre/maplibre-native.git
cd maplibre-native
apt install build-essential clang cmake ccache ninja-build pkg-config
apt install libcurl4-openssl-dev libglfw3-dev libuv1-dev libpng-dev libicu-dev libjpeg-turbo8-dev libwebp-dev xvfb libegl1-mesa-dev
cmake --preset linux-opengl
cmake --build build-linux-opengl --target mbgl-render
```

## Render a style to PNG

`mbgl-render` reads a style URL or local style file and writes a PNG:

```bash
./build-linux-opengl/bin/mbgl-render --style style.json --output out.png
```

A local style can address an MBTiles database with an absolute source URL:

```text
mbtiles:///path/to/data.mbtiles
```

## Headless rendering

On a remote or containerized host without an X display, install `xvfb` and
`xauth`, then run the renderer through a virtual display:

```bash
xvfb-run -a ./build-linux-opengl/bin/mbgl-render --style style.json --output out.png
```

## Render-fixture runner

Linux render tests compare each fixture's generated image with
`expected.png`. They retain `actual.png` and `diff.png` beside the fixture and
write an HTML summary next to the manifest.

Run a complete manifest:

```bash
./build-linux-opengl/mbgl-render-test-runner --manifestPath metrics/linux-clang8-release-style.json
```

Narrow the run with `--filter` while investigating one fixture:

```bash
./build-linux-opengl/mbgl-render-test-runner --manifestPath metrics/linux-clang8-release-style.json --filter "render-tests/fill-visibility/visible"
```

Preserve the style, renderer backend, viewport, expected image, actual image,
diff image, and HTML summary together when reporting a visual regression.
