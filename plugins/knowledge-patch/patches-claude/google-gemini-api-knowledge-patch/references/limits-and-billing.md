# Limits and Billing

## Separate account billing from project quota

The Cloud Billing account determines the plan, usage tier, and account spend
cap inherited by every linked project. API keys do not have independent
billing settings. Request quotas are enforced per project, and all keys in a
project share its counters.

Tier qualification and monthly account caps are:

| Tier | Qualification | Monthly account cap |
| --- | --- | --- |
| Tier 1 | Paid entry tier | $250 |
| Tier 2 | $100 cumulative paid Cloud usage and 3 days since first successful payment | $2,000 |
| Tier 3 | $1,000 cumulative paid Cloud usage and 30 days | $20,000–$100,000 |

Qualifying spend includes all Cloud services on the billing account, and
upgrades are automatic. Reaching the account cap pauses API access for all
linked projects until the billing cycle resets on the first of the month.
Moving a project changes its inherited tier and limits; unlinking billing
returns it to the Free Tier.

## Treat Prepay and Postpay as account-wide plans

The Prepay/Postpay rollout began March 23, 2026. New users generally default
to Prepay, though rollout accounts can temporarily receive Postpay or a choice.
Prepay purchases range from $10 to $5,000, apply only to API usage, expire
after 12 months, and are non-refundable except during a Postpay transition.

A zero Prepay balance stops every key in every linked project without moving
them to the Free Tier. Billing processing takes roughly ten minutes, so
long-running batches and agents can overrun funds and create a negative
balance. Auto-reload can prevent a stop; its monthly automatic-charge ceiling
does not include manual purchases.

Eligible promotional Cloud credits are used before prepaid funds only while
the Prepay balance remains positive. The $300 Welcome credit issued after
March 2, 2026 is ineligible. A delinquent charge for another Cloud service can
suspend API access even when prepaid funds remain.

Eligible Tier 3 accounts can move the entire billing account to Postpay. The
move refunds unused prepaid credits, switches all linked projects, and cannot
be reversed for that account. The manual switch control is temporarily
disabled.

## Expect project spend caps to lag

Editors, owners, and admins can set an experimental monthly project cap in AI
Studio. The cap survives moving the project to another billing account, while
accumulated spend resets. Both the project cap and a zero prepaid balance can
be exceeded during the roughly ten-minute processing delay; long-running work
can continue adding charges in that window.

## Diagnose quota and spend-rate failures independently

Interactive enforcement separately checks requests per minute, input tokens
per minute, and requests per day. Exceeding any dimension fails the request;
daily counters reset at midnight Pacific time. Limits are per project, not per
key. Preview and experimental endpoints are usually more constrained, and AI
Studio's active values can change with tier and account status.

Paid tiers can also have a rolling ten-minute spend-rate ceiling: $10 for Tier
1 and $200 for Tiers 2 and 3. Crossing it returns
`429 RESOURCE_EXHAUSTED` even with RPM and TPM capacity remaining.

Requests failing with HTTP 400 or 500 are not billed for tokens but still
consume quota. `GetTokens` requests are neither billed nor counted against
inference quota.

## Keep priority and batch traffic in their own pools

Priority inference has a separate default limit equal to 0.3 times the
corresponding endpoint-and-tier limit, while its use also counts toward total
interactive traffic.

Batch requests are isolated from non-batch quotas. They allow 100 concurrent
requests, a 2 GB input file, and 20 GB of stored files. Enqueued-token ceilings
apply per endpoint across all active jobs.

Representative Tier 1 / Tier 2 / Tier 3 ceilings are:

| Endpoint family | Tier 1 | Tier 2 | Tier 3 |
| --- | ---: | ---: | ---: |
| Gemini 3.6 Flash and 3.5 Flash | 3M | 400M | 1B |
| Gemini 3.5 Flash-Lite and 3.1 Flash Lite | 10M | 500M | 1B |
| Gemini 3.1 Pro Preview and 2.5 Pro | 5M | 500M | 1B |
| Gemini 2.5 Pro TTS | 25K | 100K | 1M |
| Gemini 2.5 Flash TTS | 100K | 100K | 4M |
| Gemini Embedding | 500K | 5M | 10M |

Batch processing also supports embedding requests. Event-driven completion is
available for batch jobs and other long-running operations, so integrations
can replace polling workflows.

Batch attribution: `limits-and-billing` and `release-lifecycle`.
