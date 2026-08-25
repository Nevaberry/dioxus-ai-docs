# Subscriptions and Checkout

## Subscription history

The subscription history API provides a chronological record of changes over a
subscription's lifetime, including when each change occurred, why it occurred,
and who made it.

## Paid and cardless trials

Paid trials can charge a reduced amount for the trial period while keeping the
trial and recurring amounts on the same price. Cardless trials let a customer
start without providing a payment method.

## Scheduled changes, retries, and resumption

Subscriptions with a scheduled pause or cancellation can still be updated.
Resuming a paused subscription can either start a new billing period or
continue the existing one.

Failed automatically collected subscription payments are retried even when
Paddle Retain is not enabled.

## Immediate-charge and proration behavior

A subscription permits at most 20 chargeable updates per hour and 100 per day.
Proration is represented on a transaction rather than as separate adjustments,
so transaction quantities, amounts, and totals may be negative.

Pausing cancels past-due renewal transactions so they are not collected on
resume.

## Subscription checkout consent

Subscription checkout requires explicit consent before saving a payment
method. California customers see a confirmation for subsequent recurring
charges.

South Korean subscriptions expose renewal consent state through
`consent_requirements` in API and webhook data.

## Customer portal sessions and cancellation

Customer portal sessions generate authenticated links that log a customer in
automatically. Legacy subscription management-link responses now return
customer portal links.

Cancellation Flows can run inside the portal as the subscription offboarding
experience.

## Express, upsell, and recovery checkout

Express checkout prioritizes Apple Pay on mobile and Google Pay on Android and
Chrome.

The early-access post-purchase upsell checkout supports reduced-friction
one-click purchases. Automated abandoned-checkout emails may include an
optional recovery discount.

## Checkout domains

Four API operations list and inspect approved checkout domains and trigger
Apple Pay verification.

Hosted checkout can use branded custom subdomains, announced as early access.
