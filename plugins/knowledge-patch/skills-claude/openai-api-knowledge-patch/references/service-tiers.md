# Service Tiers

Source batches: `service-tiers` and `2026-08-04-2026-08-13`.

## Flex

### Timeouts, retries, and pricing

Flex applies to Responses and Chat Completions at Batch API token rates, while
retaining prompt-cache discounts. Official SDK requests default to a ten-minute
timeout and automatically retry `408 Request Timeout` twice. Long-running Flex
work may need a larger client-level or per-request timeout.

```python
response = client.with_options(timeout=900.0).responses.create(
    model="<supported-model>",
    input="<long-running task>",
    service_tier="flex",
)
```

### Capacity failures

A Flex capacity shortage returns `429 Resource Unavailable` and does not charge
the request. Retry with exponential backoff to preserve Flex pricing. To use
the project's default processing mode instead, retry with
`service_tier="auto"` or omit the field.

## Priority

### Project defaults and effective tier

Set `service_tier="priority"` per request, or configure a project to make
Priority the default when requests omit the field. The project-level
transition occurs gradually. Inspect the response's `service_tier` field to
learn which tier actually processed a request.

```json
{
  "model": "<supported-model>",
  "input": "Latency-sensitive request",
  "service_tier": "priority"
}
```

### Rate and ramp limits

Standard and Priority traffic share the same per-model rate limit. At one
million TPM or more, raising TPM by over 50 percent within 15 minutes may
trigger the ramp limit. Affected Priority requests are processed with
`service_tier="default"` and billed at Standard rates. Shift sustained traffic
gradually.

### Compatibility and intended use

Priority retains prompt-cache discounts and supports multimodal image inputs.
It does not support long-context requests, fine-tuned models, or embeddings.
It carries a per-token premium and suits steady latency-sensitive traffic,
rather than erratic batch or evaluation workloads.

## Other processing modes

### Ultrafast limited preview

Ultrafast is a service tier for `gpt-5.6-sol` available only in limited preview
to selected customers. Do not assume it is enabled without separate access.

### Fast mode and long context

Fast mode accepts inputs longer than 272K tokens for `gpt-5.6-sol`,
`gpt-5.6-terra`, and `gpt-5.6-luna`.
