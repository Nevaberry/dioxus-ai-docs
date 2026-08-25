# Tooling and Platforms

## Diagnose work with React Performance Tracks

Since `19.2.0`, React adds Scheduler and Components tracks to Chrome DevTools
performance profiles. The Scheduler track shows update priorities and
scheduling delays. The Components track relates component render, mount, and
Effect work to the component tree. Use both to attribute blocked or expensive
work before adding custom instrumentation.

## Use Canary Fragment refs without wrapper elements

The `react-conf-2025` Canary guidance adds refs for Fragments. Fragment refs
provide a way to interact with the DOM nodes wrapped by a Fragment without
introducing an extra host element.

## Plan React Native 0.82 migrations

According to `react-conf-2025`, React Native 0.82 supports only the New
Architecture. Applications upgrading to it cannot remain on the legacy
architecture.

React Native 0.82 also adds experimental Hermes V1 support. Treat the runtime
as available for evaluation, not as a stable runtime recommendation.

## Use the expanded React Native platform surface

The `react-conf-2025` platform guidance adds web-aligned DOM APIs to React
Native, improving compatibility for code and libraries shared with React DOM.
It also adds Performance APIs, a network panel, and a desktop app, expanding
the built-in performance inspection surface.

## Manage list visibility with Virtual View

The `react-conf-2025` guidance introduces Virtual View as a React Native list
primitive. It manages item visibility through three rendering modes:

- `hidden`
- `pre-render`
- `visible`
