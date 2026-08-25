# Component Testing

## Story-and-gallery workflow

Component testing uses stories for concrete component scenarios and a served
gallery that renders those stories on demand (since 1.62.0). Define reusable
story states instead of arranging each scenario entirely inside the test.

The `mount` fixture opens a story by id and returns a locator scoped to that
story's root:

```ts
test('click should expand', async ({ mount }) => {
  const component = await mount('components/Expandable/Stateful');
  await component.getByRole('button').click();
  await expect(component.getByTestId('expanded')).toHaveValue('true');
});
```

Because the mounted component is a scoped locator, use its normal locator APIs
for interactions and assertions. It additionally exposes `update(props)` for
changing the mounted story's props and `unmount()` for explicit teardown.
Supply a story type as a type argument when the compiler should check props.
