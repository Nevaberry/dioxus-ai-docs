# Streaming and Interrupts

Relevant source topics: `langgraph-v1`, `graph-api-overview`, and
`human-in-the-loop`.

## Typed JavaScript interrupts

The `StateGraph` constructor accepts an `interrupts` map containing named
interrupt definitions. `interrupt<Input, Resume>()` types both the payload sent
through `runtime.interrupt.<name>()` and the value returned on resume.
`graph.isInterrupted(result)` identifies an interrupted result.

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

## Stream wire encoding

The low-level `toLangGraphEventStream` helper is removed. Low-level clients
should request the wire format with `graph.stream`'s `encoding` option and
return the stream directly.

```typescript
const stream = await graph.stream(input, {
  encoding: "text/event-stream",
  streamMode: ["values", "messages"],
});

return new Response(stream, {
  headers: { "Content-Type": "text/event-stream" },
});
```

## Pluggable React stream transports

The React `useStream` hook accepts a custom `transport`. Swap the network layer
without changing the component's stream handling.

```typescript
const stream = useStream({
  transport: new FetchStreamTransport({
    apiUrl: "http://localhost:2024",
  }),
});
```

## Filtering private channels

Input, output, and private state schemas do not redact `values` streams. Filter
v3 events with Python `output_keys` or JavaScript `outputKeys` when state
snapshots must omit private channels.

```python
stream = graph.stream_events(
    {"user_input": "My"},
    version="v3",
    output_keys=["graph_output"],
)
```

## Typed Python v3 event projections

`graph.stream_events(..., version="v3")` exposes typed projections for message
chunks, state snapshots, pending interrupts, interruption status, and final
output. After consuming the stream, inspect `stream.interrupted` and
`stream.interrupts`. Resume with a new v3 stream using `Command(resume=...)` and
repeat until the stream completes without interrupting.

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

Use `stream.messages` for token chunks and `stream.values` for full per-step
snapshots. Nested-subgraph token chunks are in
`stream.subgraphs[*].messages`.

## Resuming parallel interrupts by ID

Parallel branches can pause on several interrupts simultaneously. Pair every
pending interrupt's `id` with its response, then pass the complete mapping as
the `resume` value so each branch receives the right answer.

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

## Validation with one interrupt per invocation

Do not put `interrupt()` in a validation `while` loop. Every resume restarts the
node and replays earlier loop iterations, making the loop body's work grow
exponentially. Store the next prompt in state, call `interrupt()` exactly once,
and use a conditional edge to return after invalid input.

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
