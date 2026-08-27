# Diagnostics, Charts, and Color

## SwiftUI performance instrument

Instruments 26's SwiftUI template requires a current OS to record a trace
(swiftui-2025). It provides these lanes:

- Update Groups.
- Long View Body Updates.
- Long Representable Updates.
- Other Long Updates.

Orange and red events are progressively more likely to contribute to a hitch
or hang. Open an update in Time Profiler to inspect its CPU work.

Use the Cause & Effect graph when an ordinary SwiftUI call stack does not
explain the work. The graph follows gestures, state changes, creation edges,
and observation dependencies.

## Three-dimensional charts

`Chart3D` hosts `SurfacePlot(x:y:z:)`. The chart-scale pattern extends to the
depth axis through `.chartZScale(domain:)`.

## Resolved HDR color

`Color.ResolvedHDR` contains red, green, blue, and alpha components together
with HDR headroom information for a displayable color.
