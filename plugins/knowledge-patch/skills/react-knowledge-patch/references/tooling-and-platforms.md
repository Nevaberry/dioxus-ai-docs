# Tooling and Platforms

## React Performance Tracks

Chrome DevTools performance profiles now include custom React tracks:

- **Scheduler** shows update priorities and scheduling delays.
- **Components** relates render, mount, and Effect work to the component tree.

Use both tracks to identify blocked or unexpectedly expensive component work without first adding custom instrumentation.

## Canary Fragment refs

Canary React supports refs on Fragments. A Fragment ref provides access to the collection of DOM nodes wrapped by the Fragment without adding a host wrapper solely to obtain a ref.

Treat Fragment refs as Canary functionality.

## React Native 0.82 architecture

React Native 0.82 is New Architecture only. Applications upgrading to it can no longer remain on the legacy architecture.

## Hermes V1

React Native 0.82 includes experimental Hermes V1 support. It is available for evaluation, profiling, and compatibility testing, but its experimental status should remain explicit in release decisions.

## Web-aligned DOM APIs

React Native adds DOM APIs aligned with the web. These APIs improve compatibility for application code and libraries shared between React Native and React DOM.

## Performance APIs and tools

React Native adds:

- new Performance APIs;
- a network panel; and
- a desktop application for performance inspection.

Prefer these built-in surfaces when investigating native scheduling, network, or runtime work before introducing separate instrumentation.

## Virtual View

Virtual View is a React Native primitive for list rendering. It manages each item's visibility through three rendering modes:

- `hidden`;
- `pre-render`; and
- `visible`.

Use the modes to keep list work aligned with whether an item is off-screen, being prepared, or currently visible.
