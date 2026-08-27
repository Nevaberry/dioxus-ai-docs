# UI Libraries, Platform Data, and DevTools

## Angular Aria

`@angular/aria` supplies unstyled directives for keyboard interaction, ARIA
attributes, focus management, screen-reader behavior, and right-to-left
navigation while the application owns markup, styling, and business logic. It
covers autocomplete, listbox, select, multiselect, combobox, menu, menubar,
toolbar, accordion, tabs, tree, and grid. Install it with
`npm install @angular/aria`. (`21-platform-guides`)

```ts
import {Component} from '@angular/core';
import {Toolbar, ToolbarWidget} from '@angular/aria/toolbar';

@Component({
  selector: 'editor-toolbar',
  imports: [Toolbar, ToolbarWidget],
  template: `<div ngToolbar aria-label="Formatting">
    <button ngToolbarWidget value="bold" #bold="ngToolbarWidget"
            [aria-pressed]="bold.selected()">Bold</button>
  </div>`,
})
export class EditorToolbar {}
```

Angular Aria is stable in Angular 22, integrates with Signal Forms, and provides
test harnesses for its interaction patterns (`22.0.0`).

## Material theming and controls

Material 3 themes can be emitted with one `mat.theme` Sass mixin rather than
separate core and component theme mixins. Component-specific `*-overrides`
mixins replace selected design tokens without changing the rest of the theme.
(`19.0.0`)

```scss
html { @include mat.theme((color: (primary: mat.$violet-palette), density: 0)); }
@include mat.sidenav-overrides(('content-background-color': purple));
```

Angular Material v19 includes an accessible time picker (`19.0.0`). `MatMenu`
can serve as a right-click context menu through `matContextMenuTriggerFor`
(`20.0.0`):

```html
<div [matContextMenuTriggerFor]="menu">Right-click here</div>
<mat-menu #menu="matMenu">...</mat-menu>
```

Material honors `prefers-reduced-motion` automatically and exposes dependency
injection control for disabling animations. `MatButton` and `MatAnchor` are
combined, so consumers do not need both imports. (`20.0.0`)

Material system-token utility classes can apply Material Design tokens directly
in templates instead of through CSS variables (`21.0.0`).

`MatBottomSheetConfig` accepts an injector so content resolves dependencies from
a caller-selected provider scope (`21.0.0`). Signal Forms integrates with
Angular Material in Angular 22 (`22.0.0`).

## CDK behavior

CDK Drag and Drop can copy items between lists, not only move them
(`21.0.0`). CDK overlays accept a distinct viewport margin for each side
instead of one shared margin (`21.0.0`).

## Profiling and debugging

Run `ng.enableProfiling()` before recording a Chrome performance profile to add
an Angular track for component and provider creation, change detection, and
event-listener execution alongside the browser timeline (`20.0.0`).

Angular's built-in Signals debugger formatter displays signal values more
clearly. Enable custom formatters in Chrome or Firefox to activate it
(`21.0.0`).

Angular DevTools includes a route visualization and signal graph for routing and
reactive dependency inspection. Its Transfer State tab shows the
`TransferState` passed from SSR to the client. (`21.0.0`)
