# Events, notifications, and files

## Events

### Cart customer-transfer event (since 2.8.0)

The cart transfer flow now emits an event when a cart is transferred to another customer, so subscribers can react to the ownership change.

### Cart-updated events after line-item deletion (since 2.13.0)

`deleteLineItemsWorkflow` now emits the cart-updated event after it removes line items, so subscribers are notified of this cart mutation.

### Order-edit events (since 2.8.0)

Core Flows and utilities now expose versioned Order Edit events, allowing subscribers to react to order-edit lifecycle changes.

### Priority-based event processing (since 2.13.0)

Event processing now uses numeric priorities, with lower numbers processed first. Critical business events such as order placement use priority `10`, ordinary events default to `100`, and internal system events receive the lowest processing priority; priority can be overridden at the message, emit, or module level.

### Queued events are cleared during workflow compensation (since 2.10.0)

When a workflow is compensated, `emitEventsStep` now removes events it queued instead of emitting them during rollback. Workflows that intentionally need the old behavior must use a custom event-emitting step without a compensation step.

## Files and uploads

### Direct file uploads (since 2.8.0)

The File Module and its providers now expose the operations needed to support direct file uploads.

### Upload payloads use base64 encoding (since 2.11.0)

Files received through `/admin/uploads` are now base64-encoded rather than binary. The built-in Local and S3 providers handle the change, but custom file providers should accept both encodings for compatibility.

## Notifications

### Custom SendGrid notification arguments (since 2.14.0)

Twilio SendGrid email notifications now accept custom arguments, allowing provider-specific values to be attached to outgoing messages.

### Delivery workflow notification suppression (since 2.14.0)

`markOrderFulfillmentAsDeliveredWorkflow` now accepts `no_notification`, allowing delivery marking to preserve the same notification-suppression intent already available in shipment flows.

### Notification addressing and provider data (since 2.12.0)

Notifications now carry `from`, `to`, and provider-data fields, making addressing and provider-specific context part of the notification model.

### Shipment notification suppression in events (since 2.7.0)

The shipment-created event now carries `no_notification`, allowing event consumers to preserve the caller's notification-suppression choice.
