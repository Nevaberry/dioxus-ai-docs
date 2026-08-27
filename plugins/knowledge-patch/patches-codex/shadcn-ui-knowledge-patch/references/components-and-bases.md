# Components and Primitive Bases

## React 19 wrappers and slots

Updated components replace `React.forwardRef` wrappers with functions typed by
`React.ComponentProps<typeof Primitive>`. Pass refs with the remaining props,
add a `data-slot` attribute to every primitive, and remove the former wrapper
`displayName` assignment.

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

## Changed defaults

For the established component set, `toast` is deprecated in favor of `sonner`,
the `default` style is deprecated in favor of `new-york`, and buttons retain
the browser's default cursor.

## Base UI projects

New projects can use Base UI while retaining the shadcn/ui abstraction, imports,
appearance, and behavior; only the underlying primitives change. The CLI
detects the project's component library when adding built-in or remote-registry
components and performs the matching transforms. Base UI implementations remain
compatible with existing components.

```tsx
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
```

Base UI is the default for new projects. Scripts and CI that require Radix must
select it explicitly. Registry authors that need to pin a primitive base should
provide a `registry:base` item; a registry without one initializes as Base UI.

```sh
pnpm dlx shadcn init -b radix
```

## Base UI Toast

The Base UI Toast supports actions, status types, promises, stacking, and swipe
dismissal. Install its source through the CLI:

```sh
pnpm dlx shadcn@latest add toast
```

This Base UI component is distinct from the deprecated older `toast` component.

## React Aria isolation

The React Aria base works with Vega, Nova, Maia, Lyra, Mira, Luma, Rhea, and
Sera. Its state selectors and dependencies come from the Aria-specific registry,
so existing Base UI and Radix components are not changed.

## Progressive Radix-to-Base-UI migration

The shadcn skill can migrate one customized component and its usages at a time
while Radix and Base UI coexist, or migrate the whole project. It performs
mechanical changes such as converting `asChild` to `render`, identifies behavior
differences for review, typechecks and builds, writes a per-component report in
`.migration/`, and creates one commit per component on a branch.

```text
migrate accordion to base-ui
```

Install the supporting skill when that workflow is needed:

```sh
pnpm dlx skills add shadcn/ui
```

It also supplies current primitive APIs, component patterns, registry workflows,
and CLI guidance matching the project's design system.

## Deterministic chat helpers

`@shadcn/helpers` can drive AI SDK or TanStack AI chat interfaces without a
model, API route, network request, or API key. The AI SDK adapter supplies native
messages and a `useChat` transport. `@shadcn/helpers/tanstack-ai` supplies a
TanStack AI `useChat` connection with real AG-UI events. Scripted conversations
can emit delays, reasoning, tool calls and outputs, sources, and streaming text.

```tsx
import { useChat } from "@ai-sdk/react"
import { createChat } from "@shadcn/helpers/ai-sdk"

const chat = createChat()
  .user("What changed?")
  .assistant("Keyboard shortcuts and faster search.")

export function useDemoChat() {
  return useChat({
    messages: chat.get(0),
    transport: chat.transport(),
  })
}
```

## Typeset

`shadcn/typeset` is a one-file CSS system for HTML and rendered Markdown. Apply
the `typeset` class to inherit theme and container sizing. It is safe for
streaming content, and each context can tune size, leading, and flow.

```css
.typeset-chat {
  --typeset-leading: 1.6;
  --typeset-flow: 1em;
}

.typeset-docs {
  --typeset-size: 15px;
  --typeset-leading: 1.75;
  --typeset-flow: 1.5em;
}
```

```tsx
<div className="typeset typeset-chat">{message}</div>
<article className="typeset typeset-docs">{page}</article>
```
