# Components & Templates (v21)

## Angular Aria (developer preview, v21)

Headless accessible components in `@angular/aria`.

```bash
npm i @angular/aria
```

### Available patterns

Accordion, Combobox, Grid, Listbox, Menu, Tabs, Toolbar, Tree.

Unstyled — you provide all CSS. Components handle ARIA attributes, keyboard navigation, and focus management.

---

## Minor template additions (v21)

### Regex in templates

```html
@let isValid = /\d+/.test(someValue);
```

### `@defer` viewport options

```html
@defer (on viewport({trigger, rootMargin: '100px'})) {
  ...
}
```

### Generic SimpleChanges

Better type checking for `ngOnChanges` — `SimpleChanges` is now generic.
