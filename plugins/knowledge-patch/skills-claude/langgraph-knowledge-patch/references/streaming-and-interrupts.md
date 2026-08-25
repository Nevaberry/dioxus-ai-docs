# Streaming and interrupts

## Private state in value streams

A node's input schema limits reads, not the graph channels it may update.
Node-declared schemas can add private channels to the graph-state union. Input,
output, and private schemas do not redact `values` streams. When private
channels must not appear in emitted snapshots, filter v3 event streams with
`output_keys` in Python or `outputKeys` in JavaScript.

```python
stream = graph.stream_events(
    {"user_input": "My"},
    version="v3",
    output_keys=["graph_output"],
)
```

## Typed JavaScript interrupts

The `StateGraph` constructor accepts an `interrupts` map of named interrupt
definitions. `interrupt<Input, Resume>()` types both the payload passed through
`runtime.interrupt.<name>()` and the value returned on resume.
`graph.isInterrupted(result)` detects an interrupted result.

```typescript
import { StateGraph, interrupt } from "@langchain/langgraph";
import * as z from "zod";

const State = z.object({ messages: z.array(z.string()) });

const graph = new StateGraph(State, {
  interrupts: {
    approve: interrupt<{ reason: string }, { messages: string[] }>(),
  },
})
  .addNode("review", (_state, runtime) => {
    const response = runtime.interrupt.approve({ reason: "review" });
    return { messages: response.messages };
  })
  .compile();
```

## Typed v3 Python event streams

`graph.stream_events(..., version="v3")` provides typed projections for
message chunks, state snapshots, pending interrupts, interruption status, and
final output. Drive the stream to completion, inspect `stream.interrupted` and
`stream.interrupts`, and resume with a new v3 stream using
`Command(resume=...)`. Repeat until it finishes without interruption.

```python
stream = graph.stream_events(inputs, config=config, version="v3")
result = stream.output

if stream.interrupted:
    stream = graph.stream_events(
        Command(resume=review(stream.interrupts)),
        config=config,
        version="v3",
    )
```

Token chunks are in `stream.messages`, full per-step snapshots in
`stream.values`, and nested-child token chunks in
`stream.subgraphs[*].messages`.

## Resume parallel interrupts by ID

Parallel branches may pause on multiple interrupts. Pair every pending
interrupt `id` with its response and pass the complete mapping as `resume`, so
each branch receives the right answer.

```typescript
import { Command, INTERRUPT, isInterrupted } from "@langchain/langgraph";

const paused = await graph.invoke(input, config);
const responses: Record<string, string> = {};

if (isInterrupted(paused)) {
  for (const item of paused[INTERRUPT]) {
    if (item.id != null) responses[item.id] = answer(item.value);
  }
}

await graph.invoke(new Command({ resume: responses }), config);
```

## Validate with one interrupt per invocation

Do not put `interrupt()` inside a re-prompting `while` loop. Every resume
restarts the node and replays earlier iterations, making the loop body's work
grow exponentially. Save the next prompt in state, invoke `interrupt()` once,
and use a conditional edge to revisit the node after invalid input.

```typescript
builder
  .addNode("collectAge", (state) => {
    const answer = interrupt(state.pendingQuestion ?? "What is your age?");
    return typeof answer === "number" && answer > 0
      ? { age: answer, pendingQuestion: null }
      : { pendingQuestion: `'${answer}' is not a valid age.` };
  })
  .addConditionalEdges(
    "collectAge",
    (state) => state.age !== null ? END : "collectAge",
  );
```

## Stream wire encoding

The low-level `toLangGraphEventStream` helper is removed. Request wire encoding
through `graph.stream` and return the stream directly.

```typescript
const stream = await graph.stream(input, {
  encoding: "text/event-stream",
  streamMode: ["values", "messages"],
});

return new Response(stream, {
  headers: { "Content-Type": "text/event-stream" },
});
```

## Custom `useStream` transports

React `useStream` accepts a custom `transport`, allowing the network layer to
change without replacing UI stream handling.

```typescript
const stream = useStream({
  transport: new FetchStreamTransport({
    apiUrl: "http://localhost:2024",
  }),
});
```
