# Zoneless Angular & Testing (v19–v21)

## Zoneless Angular (stable in v20.2, default in v21)

New apps in v21 are zoneless by default — no `zone.js` included.

### Migrating existing apps

```typescript
bootstrapApplication(AppComponent, {
  providers: [
    provideZonelessChangeDetection(),
    provideBrowserGlobalErrorListeners(), // replaces zone.js error capture
  ],
});
```

Remove `zone.js` polyfill from `angular.json` after migration.

---

## Vitest (stable in v21, new default)

Vitest replaces Karma as the default test runner. `ng test` uses Vitest for new projects.

### Migrate existing Jasmine tests to Vitest

```bash
ng g @schematics/angular:refactor-jasmine-vitest
```
