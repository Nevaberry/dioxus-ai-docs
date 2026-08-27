# Upgrade and Styling

## Project Stack and Upgrade Boundary

The CLI can initialize Tailwind v4 and React 19 projects. Existing Tailwind v3
and React 18 applications, including components later added to them, stay on
their current stack until explicitly upgraded. Before an upgrade, check
Tailwind v4 browser compatibility and run the preview upgrade codemod.

```sh
npx @tailwindcss/upgrade@next
```

## Tailwind v4 CSS Variable Layout

Move `:root` and `.dark` outside `@layer base`. Variables must contain complete
color expressions. Map them through `@theme inline` without another color
function wrapper. New palettes use OKLCH. Chart configuration likewise uses a
complete variable directly, for example `color: "var(--chart-1)"`.

```css
:root {
  --background: hsl(0 0% 100%);
}

.dark {
  --background: hsl(0 0% 3.9%);
}

@theme inline {
  --color-background: var(--background);
}
```

## React 19 Wrappers and Slots

Updated component source replaces `React.forwardRef` wrappers with functions
typed from `React.ComponentProps`. The ref is passed with the remaining props,
each primitive receives a `data-slot` attribute for styling, and the old
wrapper `displayName` assignment can be removed.

```tsx
function AccordionItem({
  className,
  ...props
}: React.ComponentProps<typeof AccordionPrimitive.Item>) {
  return (
    <AccordionPrimitive.Item
      data-slot="accordion-item"
      className={cn("border-b last:border-b-0", className)}
      {...props}
    />
  )
}
```

## Changed Component Defaults

The legacy `toast` component is deprecated in favor of `sonner`; do not
confuse that deprecation with the supported Toast implementation available to
Base UI projects. The `default` style is deprecated and new projects use
`new-york`. Buttons now retain the browser's default cursor.

## Animation Package Replacement

`tailwindcss-animate` is deprecated. For an existing project, remove the old
dependency and its `@plugin` directive, install `tw-animate-css` as a
development dependency, and import it from global CSS.

```css
@import "tw-animate-css";
```

## Opt-in Dark-mode Palette Refresh

The refreshed dark palette applies automatically to projects created on
Tailwind v4, not to projects upgraded from v3. To opt in safely:

1. Commit local component changes.
2. Overwrite the components.
3. Replace dark variables in `globals.css` with the new OKLCH colors.
4. Review the diff and reapply project customizations.

```sh
pnpm dlx shadcn@latest add --all --overwrite
```

## Shared Tailwind CSS and Ejection

New initialization imports `shadcn/tailwind.css`, which supplies shared
Tailwind v4 variants, utilities, and animations. `eject` irreversibly inlines
that stylesheet and removes the `shadcn` dependency. Once ejected, later CLI
updates to the shared stylesheet no longer reach the project automatically.

```sh
pnpm dlx shadcn@latest eject
```
