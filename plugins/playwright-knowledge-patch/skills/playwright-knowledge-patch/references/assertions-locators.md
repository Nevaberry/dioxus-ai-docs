# Assertions & Locators

## toHaveAccessibleErrorMessage (1.50)

```js
await expect(page.getByRole('textbox')).toHaveAccessibleErrorMessage('Required field');
```

## toContainClass (1.52)

Assert individual class names without matching the full class attribute:
```js
await expect(page.getByRole('listitem', { name: 'Task' })).toContainClass('done');
```

## toHaveURL with Predicate (1.51)

```js
await expect(page).toHaveURL(url => url.searchParams.has('token'));
```

## locator.filter({ visible }) (1.51)

Filter to only visible elements:
```js
const items = page.getByTestId('item').filter({ visible: true });
await expect(items).toHaveCount(3);
```

## locator.describe() (1.53)

Annotate locators for trace viewer and reports:
```js
const btn = page.getByTestId('btn-sub').describe('Subscribe button');
await btn.click();
```

## locator.normalize() (1.59)

Converts locator to best-practice form (test ids, aria roles).

## ARIA Snapshots

### Separate YAML Files (1.50)

`toMatchAriaSnapshot()` can now reference external YAML files for snapshot storage.

### /children and /url (1.52)

Strict child matching with `/children: equal` and link URL matching with `/url`:
```yaml
- list
  - /children: equal
  - listitem: Feature A
  - listitem:
    - link "Feature B":
      - /url: "https://example.com"
```

### page.ariaSnapshot() (1.59)

Shorthand for `page.locator('body').ariaSnapshot()`.

### locator.ariaSnapshot({ depth, mode }) (1.59)

Control snapshot depth and mode.

## Interactive Locator Picking (1.59)

`page.pickLocator()` / `page.cancelPickLocator()` — interactive locator picking in headed mode.
