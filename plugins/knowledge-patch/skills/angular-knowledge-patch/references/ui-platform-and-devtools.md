# UI Libraries, Platform Data, and DevTools

Batch attribution: 19.0.0, 20.0.0, 21-platform-guides, 21.0.0, 22.0.0.

## Angular Aria

Angular Aria is the `@angular/aria` package of unstyled directives for accessible interaction patterns. It supplies keyboard interaction, ARIA attributes, focus management, screen-reader behavior, and right-to-left navigation while the application owns markup, styling, and business logic.

Install it with:

```sh
npm install @angular/aria
```

It covers autocomplete, listbox, select, multiselect, combobox, menu, menubar, toolbar, accordion, tabs, tree, and grid patterns.

```ts
import {Component} from '@angular/core';
import {
  Toolbar,
  ToolbarWidget,
} from '@angular/aria/toolbar';

@Component({
  selector: 'editor-toolbar',
  imports: [Toolbar, ToolbarWidget],
  template: `
    <div ngToolbar aria-label="Formatting">
      <button
        ngToolbarWidget
        value="bold"
        #bold="ngToolbarWidget"
        [aria-pressed]="bold.selected()">
        Bold
      </button>
    </div>
  `,
})
export class EditorToolbar {}
```

The package arrived in Angular 21 and is stable in Angular 22. Angular 22 adds test harnesses for its patterns and integrates Angular Aria with Signal Forms.

## Material theming and components

### Material 3 themes and overrides

Angular Material 19 can emit a Material 3 theme through one `mat.theme` Sass mixin rather than separate core and component theme mixins. A component-specific `*-overrides` mixin changes selected design tokens without disturbing the rest of the theme.

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

### Time picker

Angular Material 19 includes an accessible time-picker component, removing the need for a third-party control for that capability.

### Context menus

`MatMenu` can act as a right-click context menu through `matContextMenuTriggerFor`:

```html
<div [matContextMenuTriggerFor]="menu">
  Right-click here
</div>

<mat-menu #menu="matMenu">...</mat-menu>
```

### Motion and imports

Angular Material 20 automatically honors `prefers-reduced-motion` and provides dependency-injection control for disabling animation. `MatButton` and `MatAnchor` are combined, so consumers do not need to import both separately.

### System-token utility classes

Angular Material 21 adds utility classes that apply Material Design system tokens directly in a template as an alternative to CSS variables.

### Bottom-sheet injector

`MatBottomSheetConfig` can receive an injector, allowing bottom-sheet content to resolve dependencies from a provider scope selected by its caller.

### Signal Forms integration

Angular 22 integrates Signal Forms with Angular Material. Use the supported integration instead of manually synchronizing field state and Material controls.

## CDK interaction and overlay changes

Angular 21 CDK Drag and Drop can copy items between lists in addition to moving them.

CDK overlays can configure different viewport margins for each side rather than applying one margin uniformly.

## Locale data changes

Angular 21 updates CLDR support from version 41 to version 47. Currency, date, and other locale-sensitive formatting can therefore change after an upgrade. Snapshot and visual tests around localized output should be reviewed rather than blindly regenerated.

## Chrome performance tracks

Call `ng.enableProfiling()` before recording a profile in Chrome DevTools. Angular then adds a track that shows:

- component creation;
- provider creation;
- change-detection work;
- event-listener execution.

The Angular track appears alongside the browser's own timeline, making it easier to correlate framework work with layout, paint, and scripting.

## Signals debugger formatter

Angular 21 includes a built-in formatter that displays signal values more clearly in the debugger. Enable custom formatters in Chrome or Firefox to use it.

## Angular DevTools visualizations

Angular DevTools adds:

- route visualization for inspecting application routing;
- a signal graph for reactive dependencies;
- a Transfer State tab for inspecting the `TransferState` passed from server rendering to the client.

Use the route and signal views to understand structure and dependency flow; use the Transfer State view when debugging hydration or duplicated client requests.
