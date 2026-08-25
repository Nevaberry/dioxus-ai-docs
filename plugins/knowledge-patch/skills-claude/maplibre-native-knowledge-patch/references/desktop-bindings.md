# Desktop bindings

Use this reference for the Node native package and Qt 3 integration,
rendering, resource loading, logging, linking, and deployment.

## Node runtime and renderer

### Runtime support (`node-6.1.0`, `desktop-bindings`)

The Node 6.1 package line moved back to `@mapbox/node-pre-gyp`, which requires
Node.js 18 or newer; Node.js 16 is unsupported. The stable 6.4.1 binding
explicitly supports Node.js 20, 22, and 24. Node.js 26 support is associated
with the 6.5 prerelease line and must not be assumed for the stable package.

### Drawable renderer (`node-6.1.0`)

Linux and Windows Node builds use the drawable renderer. The legacy renderer
has been removed.

## Node data and sprite support

### PMTiles (`node-6.1.0`)

Node 6.1 supports PMTiles-backed map data. A custom request hook still needs to
understand every URL scheme used by the style.

### Sprite text-fit metadata (`node-6.1.0`)

Sprites may define `textFitWidth` and `textFitHeight`, exposing text-fit
metadata to Node rendering code.

## Node rendering

### Render options and buffer lifetime (`desktop-bindings`)

`Map.render` accepts optional `zoom`, `width`, `height`, `[longitude, latitude]`
`center`, counter-clockwise-from-north `bearing`, `pitch`, and style `classes`.
Defaults are zoom 0, 512×512 pixels, center `[0, 0]`, and zero bearing and
pitch. Rendering completes asynchronously with a raw four-channel pixel
buffer.

`release()` permanently prevents further rendering. It is safe to call inside
the render callback because the returned buffer remains retained for that
callback.

```js
const mbgl = require('@maplibre/maplibre-gl-native');
const map = new mbgl.Map();

map.load(require('./style.json'));
map.render({ width: 256, height: 256, center: [24.94, 60.17], zoom: 10 },
  (error, rgba) => {
    if (error) throw error;
    map.release();
    // rgba contains raw four-channel pixel data.
  });
```

### Resource request hook (`desktop-bindings`)

The `Map` constructor's `request({ url, kind }, callback)` hook routes every
style resource through application code. `kind` values are:

| Value | Kind |
| ---: | --- |
| 0 | `Unknown` |
| 1 | `Style` |
| 2 | `Source` |
| 3 | `Tile` |
| 4 | `Glyphs` |
| 5 | `SpriteImage` |
| 6 | `SpriteJSON` |

The hook must handle any custom scheme used by the style. A successful
response requires uncompressed byte `data` and may include `modified` and
`expires` dates and an `etag`. Invoke the callback with no arguments for a
no-content result. Constructor `ratio` controls high-density rendering scale.

```js
const fs = require('node:fs');
const path = require('node:path');
const mbgl = require('@maplibre/maplibre-gl-native');

const map = new mbgl.Map({
  request({ url }, callback) {
    fs.readFile(path.join('base/path', url), (error, data) => {
      if (error) return callback(error);
      callback(null, { data });
    });
  },
  ratio: 2
});
```

### Log events (`desktop-bindings`)

The imported module is an `EventEmitter`. Its `message` events may contain
`class`, `severity`, `code`, and `text`, exposing native style and resource
failures directly.

```js
const mbgl = require('@maplibre/maplibre-gl-native');

mbgl.on('message', (message) => {
  console.error(message.class, message.severity, message.code, message.text);
});
```

## Qt 3 linking and discovery

### Libraries and CMake targets (`desktop-bindings`)

Qt 3 places the API in `QMapLibre` and splits installation into `QMapLibre`,
`QMapLibreLocation`, and `QMapLibreWidgets`. The CMake package exposes `Core`,
`Location`, and `Widgets` components and matching `QMapLibre::*` targets. The
release supports static builds and use as a CMake subproject.

It was built with Qt 6.5–6.7 on every supported platform and Qt 5.15.2 on
macOS, Linux, and Windows. Point `QMapLibre_DIR` at
`<install>/lib/cmake/QMapLibre`, or put the installation prefix in
`CMAKE_PREFIX_PATH`. Widgets deployments require both the `QMapLibre` and
`QMapLibreWidgets` libraries.

```cmake
find_package(QMapLibre COMPONENTS Widgets REQUIRED)
target_link_libraries(MyApplication PRIVATE QMapLibre::Widgets)
```

## Qt QML and deployment

### QML import and plugin trees (`desktop-bindings`)

Qt 3 QML applications use `import MapLibre 3.0` and configure styles through
`maplibre.map.styles`. Deploy both `plugins/geoservices` and `qml/MapLibre`
together with the core and Location libraries.

Linking `Location` provides `qmaplibre_location_setup_plugins`, which installs
both plugin trees:

```cmake
find_package(QMapLibre COMPONENTS Location REQUIRED)
target_link_libraries(MyApplication PRIVATE QMapLibre::Location)
qmaplibre_location_setup_plugins(MyApplication)
```

For undeployed development runs, set `QML_IMPORT_PATH=<install>/qml` and
`QT_PLUGIN_PATH=<install>/plugins` when Qt cannot find them. Use
`QSG_RHI_BACKEND=opengl` to force Qt 3's supported renderer.

### Android multi-ABI packages (`desktop-bindings`)

For a Qt Android multi-ABI build, resolve the ABI-specific package below a
common `QMapLibre_Android_DIR`; do not reuse one architecture's
`QMapLibre_DIR`.

```cmake
if(ANDROID AND DEFINED ENV{QMapLibre_Android_DIR})
    set(QMapLibre_DIR
        "$ENV{QMapLibre_Android_DIR}/${ANDROID_ABI}/lib/cmake/QMapLibre")
endif()
```

### Empty styles (`desktop-bindings`)

Qt 3 allows construction of a `Style` with an empty URL. Do not add a
placeholder URL solely to construct the object.
