# Matkahuolto Interface Hub and access

## XML label requests

Submit XML requests with HTTP POST over HTTPS. The server rejects unencrypted
HTTP. A successful request returns XML containing both the reply and an
address-label PDF to print and attach to the consignment. The request format
includes optional fields.

## Pickup-point integration

Pickup points can be integrated through either:

- the real-time search API; or
- periodic downloads of the pickup-point dataset into the store's own
  database, such as once daily.

## Shipment EDI and notification contacts

Shipment information can be sent through an API call or file transfer. EDI
messages are accepted in XML or CSV and include sender and recipient details.
The recipient's mobile number or email address is required when it is needed
for arrival notifications.

## Tracking in a store

Matkahuolto tracking data can be displayed directly in an online store in
addition to the recipient-facing Track & Trace service.

## Test and production behavior

The test environment returns correctly formatted responses but does not
process submitted consignments. Moving the integration to production only
requires changing the contact address.

## Agreements and credentials

A valid agreement is required to use the open APIs. Free API credentials are
required for testing and implementation. Existing customers without
credentials must request them through the designated form. Customer IDs are
also requested through that form rather than technical-support email.
