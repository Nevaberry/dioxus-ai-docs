# Component Bases and Content

## Base UI Component Base

New projects can use Base UI instead of Radix while retaining the shadcn/ui
component abstraction, imports, appearance, and intended behavior. Only the
underlying primitives change. When adding components, the CLI detects the
project's library and applies corresponding transformations, including for
remote-registry components. The Base UI implementation remains compatible
with existing components.

```tsx
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
```

## Base UI Default

New projects default to Base UI. Non-interactive scripts and CI that expect
Radix must request it explicitly. A registry that needs to pin its component
base should supply a `registry:base` item; without one, initialization uses
Base UI.

```sh
pnpm dlx shadcn init -b radix
```

## Progressive Radix Migration

The shadcn skill can migrate a customized Radix component and its usages one
at a time while Radix and Base UI coexist, or migrate the full project. It
performs mechanical changes such as converting `asChild` to `render`, flags
behavior differences for review, typechecks and builds, writes a component
report below `.migration/`, and creates one commit per component on a branch.

```text
migrate accordion to base-ui
```

## React Aria Style and Isolation

The React Aria base supports all eight styles: Vega, Nova, Maia, Lyra, Mira,
Luma, Rhea, and Sera. Aria state selectors and dependencies come from its own
registry, so existing Base UI and Radix components remain unchanged.

## Base UI Toast

Base UI projects have a Toast component with actions, status types, promises,
stacking, and swipe dismissal. Install its source through the CLI.

```sh
pnpm dlx shadcn@latest add toast
```

This is distinct from the deprecated legacy toast component for which Sonner
is the recommended replacement.

## Deterministic Chat Helpers

`@shadcn/helpers` can drive AI SDK or TanStack AI chat interfaces without a
model, API route, network request, or API key. The AI SDK adapter supplies
native messages and a `useChat` transport. `@shadcn/helpers/tanstack-ai`
supplies a TanStack AI `useChat` connection with real AG-UI events. Scripted
conversations can emit delays, reasoning, tool calls and outputs, sources, and
streaming text.

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

`shadcn/typeset` is a one-file CSS system for styling HTML and rendered
Markdown with the `typeset` class. It inherits the theme and container size,
is safe for streaming content, and lets each context tune size, line height,
and flow through CSS variables.

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
