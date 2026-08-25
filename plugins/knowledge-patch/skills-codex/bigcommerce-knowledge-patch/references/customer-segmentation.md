# Customer Segmentation REST responses

## Delete and remove operations

Segment and Shopper Profile delete and remove operations return `200` with a
batch envelope. Invalid input returns `422`.

This replaces the formerly documented empty `204` response.

## Create and update validation

Create and update validation failures return `422`, not `400`.

## Response envelopes

Create, update, add, and remove responses contain:

- `data`;
- `errors`;
- `meta` with `total`, `success`, and `failed`.

Paginated lists include `links`.
