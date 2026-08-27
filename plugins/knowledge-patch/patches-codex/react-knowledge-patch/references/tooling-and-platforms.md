# Tooling and Platforms

React Performance Tracks are attributed to `19.2.0`; the platform additions are attributed to `react-conf-2025`.

## Diagnose work with React Performance Tracks

React adds custom Scheduler and Components tracks to Chrome DevTools performance profiles. They align update priorities and scheduling delays with component render, mount, and Effect work.

Use these tracks to attribute blocked or unexpectedly expensive work before adding custom instrumentation.

## Use Canary Fragment refs without wrapper DOM

Canary React adds refs for Fragments. A Fragment ref can interact with the DOM nodes wrapped by the Fragment without introducing an extra host element.

## Migrate React Native 0.82 to the New Architecture

React Native 0.82 is New Architecture only. An application upgrading to 0.82 cannot remain on the legacy architecture.

## Treat Hermes V1 as experimental

React Native 0.82 adds experimental Hermes V1 support. It is available for evaluation, but should not be presented as a stable runtime recommendation.

## Use web-aligned React Native APIs

React Native adds DOM APIs aligned with the web. These APIs improve compatibility for application code and libraries shared with React DOM.

## Inspect React Native performance with built-in tools

React Native adds Performance APIs, a network panel, and a desktop app. Together they expand the platform's built-in performance inspection surface.

## Model list visibility with Virtual View

Virtual View is a React Native primitive for list rendering. It manages each item's visibility through three rendering modes:

- `hidden`
- `pre-render`
- `visible`
