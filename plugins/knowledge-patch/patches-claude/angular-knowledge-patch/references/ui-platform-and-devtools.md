# UI Libraries, Platform Data, and DevTools

## Material 3 theme mixins

Angular Material 19 can emit a Material 3 theme through one `mat.theme` Sass mixin instead of separate core and component mixins (`19.0.0`). Component-specific `*-overrides` mixins replace selected design tokens without disturbing the rest of the configured theme.

```scss
html {
  @include mat.theme((
    color: (primary: mat.$violet-palette),
    density: 0,
  ));
}

@include mat.sidenav-overrides((
  'content-background-color': purple,
));
```

## Material time picker

Angular Material 19 includes an accessible time-picker component (`19.0.0`). Prefer it over carrying a third-party picker solely to supply this capability.

## Material context menus

`MatMenu` can serve as a right-click context menu through `matContextMenuTriggerFor` (`20.0.0`):

```html
<div [matContextMenuTriggerFor]="menu">Right-click here</div>
<mat-menu #menu="matMenu">...</mat-menu>
```

## Motion and imports

Angular Material automatically honors `prefers-reduced-motion` and provides dependency-injection control for disabling animation (`20.0.0`). Do not duplicate reduced-motion behavior with conflicting application rules.

`MatButton` and `MatAnchor` are combined, so consumers do not need to import both separately.

## Angular Aria (`21-platform-guides`)

`@angular/aria` provides unstyled accessible interaction directives while the application owns markup, styling, and business logic. It implements keyboard interaction, ARIA attributes, focus management, screen-reader behavior, and right-to-left navigation for:

- autocomplete, listbox, select, multiselect, and combobox;
- menu, menubar, and toolbar;
- accordion and tabs; and
- tree and grid.

Install the package explicitly:

```sh
npm install @angular/aria
```

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

Angular Aria is stable in v22 and includes test harnesses for its interaction patterns (`22.0.0`). Signal Forms integrates with Angular Aria and Material.

## Material system-token utilities

Angular Material supplies utility classes that apply Material Design system tokens directly in templates (`21.0.0`). They provide an alternative to wiring every token through application CSS variables.

## CDK drag and drop

CDK Drag and Drop can copy items between lists, not only move them (`21.0.0`). Choose the copy or move behavior explicitly so the data-model update agrees with the visual interaction.

## CDK overlay margins

CDK overlays can use a different viewport margin for each side (`21.0.0`). Use per-side margins when one edge needs clearance that should not constrain the other three.

## Material bottom-sheet injectors

`MatBottomSheetConfig` accepts an injector (`21.0.0`), allowing bottom-sheet content to resolve dependencies from the caller's selected provider scope.

## Locale data

Angular 21 moves its CLDR support from v41 to v47 (`21.0.0`). Currency, date, number, and other locale-sensitive output can change after upgrade; run locale-focused regression tests rather than assuming formatting is byte-identical.

## Chrome performance tracks

Call `ng.enableProfiling()` before recording a Chrome DevTools performance profile (`20.0.0`). Angular adds a track for component and provider creation, change-detection work, and event-listener execution alongside the browser timeline.

## Signals debugger formatter

Angular 21 includes a debugger formatter that makes signal values easier to inspect (`21.0.0`). Enable custom formatters in Chrome or Firefox to use it.

## Angular DevTools visualizations

Angular DevTools in v21 adds:

- route visualization;
- a signal graph for reactive dependencies; and
- a Transfer State tab showing the `TransferState` passed from SSR to the client.

Use the signal graph to distinguish a missing dependency edge from a change-detection scheduling problem, and the Transfer State tab to verify what hydration actually received.
