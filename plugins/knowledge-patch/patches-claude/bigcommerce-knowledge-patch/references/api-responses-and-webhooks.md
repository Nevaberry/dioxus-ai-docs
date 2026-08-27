# API Responses and Webhooks

## B2B quote webhook payload

B2B quote events send `quote_id` and `quote_uuid` in `data`. They do not send
the previously documented `type` and `id` fields.

Webhook consumers must parse the quote-specific fields.

## Customer Segmentation REST responses

### Delete and remove operations

Segment and Shopper Profile delete or remove operations return `200` with a
batch envelope. Invalid input uses `422`. These operations do not return the
formerly documented empty `204` response.

### Create and update validation

Create and update validation failures use `422`, not `400`.

### Response envelopes

Create, update, add, and remove responses contain:

- `data`
- `errors`
- `meta`

The `meta` object contains:

- `total`
- `success`
- `failed`

Paginated lists include `links`.
