# Activity Component

*Added in React 19.2 (2025-10-01)*

## Overview

`<Activity>` is a new built-in component for pre-rendering and preserving hidden UI. It replaces conditional rendering patterns (`{show && <Component />}`) when state must survive visibility toggles or when offscreen content should be pre-rendered.

## Import

```jsx
import { Activity } from 'react';
```

## API

```jsx
<Activity mode="visible" | "hidden">
  {children}
</Activity>
```

### Props

| Prop | Type | Description |
|---|---|---|
| `mode` | `'visible' \| 'hidden'` | Controls child visibility and behavior |
| `children` | `ReactNode` | Content to render |

### Mode behavior

| Behavior | `visible` | `hidden` |
|---|---|---|
| Rendering | Normal | Hidden via CSS (`display: none` or equivalent) |
| Effects | Active | Unmounted (cleanup runs, re-mounts on visible) |
| State | Preserved | Preserved |
| Updates | Normal priority | Deferred (lower priority) |
| DOM | In document | In document but hidden |

## Usage Patterns

### Tab container with preserved state

```jsx
function TabContainer({ tabs, activeTab }) {
  return (
    <div>
      {tabs.map((tab) => (
        <Activity
          key={tab.id}
          mode={tab.id === activeTab ? 'visible' : 'hidden'}
        >
          <TabContent tab={tab} />
        </Activity>
      ))}
    </div>
  );
}
```

Hidden tabs retain their state — form inputs, scroll position, local component state all survive tab switches without remounting.

### Route pre-rendering

```jsx
function Router({ currentPath }) {
  return (
    <>
      <Activity mode={currentPath === '/' ? 'visible' : 'hidden'}>
        <HomePage />
      </Activity>
      <Activity mode={currentPath === '/dashboard' ? 'visible' : 'hidden'}>
        <Dashboard />
      </Activity>
    </>
  );
}
```

Pre-render routes so navigation feels instant. Hidden routes have their effects unmounted but DOM and state preserved.

### Preserving state during dialogs

```jsx
function FormWithConfirmation() {
  const [confirming, setConfirming] = useState(false);

  return (
    <>
      <Activity mode={confirming ? 'hidden' : 'visible'}>
        <ExpensiveForm onSubmit={() => setConfirming(true)} />
      </Activity>
      {confirming && (
        <ConfirmDialog
          onConfirm={handleSubmit}
          onCancel={() => setConfirming(false)}
        />
      )}
    </>
  );
}
```

## Key Details

- **Effects lifecycle**: When mode changes to `hidden`, effect cleanup functions run. When mode returns to `visible`, effects re-run. This matches the behavior of unmounting/remounting but without losing state.
- **State preservation**: All React state (`useState`, `useReducer`), refs, and DOM state (input values, scroll positions) survive hidden/visible transitions.
- **Deferred updates**: Updates to hidden Activity trees are processed at lower priority, avoiding unnecessary work for offscreen content.
- **Not the same as `display: none`**: While hidden content is visually hidden, React also optimizes by deferring updates and unmounting effects, which plain CSS hiding does not do.
