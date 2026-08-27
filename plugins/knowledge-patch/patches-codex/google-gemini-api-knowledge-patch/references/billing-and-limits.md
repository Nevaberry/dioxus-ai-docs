# Billing, quotas, and traffic pools

## Separate billing-account controls from project quotas

The Cloud Billing account determines the plan, usage tier, and account spend
cap inherited by every linked project. API keys have no independent billing
configuration. Request quotas are per project, so all keys in one project
share counters.

Tier 2 requires $100 cumulative paid Cloud usage and three days after the first
successful payment. Tier 3 requires $1,000 and 30 days. Spend across all Cloud
services on the billing account qualifies, and tier upgrades are automatic.
Monthly account caps are $250 for Tier 1, $2,000 for Tier 2, and
$20,000–$100,000 for Tier 3.

Reaching the account cap pauses the API for every linked project until the
billing cycle restarts on the first day of the month. Moving a project changes
its inherited tier and limits; unlinking billing returns it to Free Tier.

## Treat Prepay and Postpay as account-wide

Prepay/Postpay began taking effect March 23, 2026. New users generally default
to Prepay, though accounts in rollout can temporarily receive Postpay or a
choice. Prepay purchases are $10–$5,000, apply only to API usage, expire after
12 months, and are non-refundable except on transition to Postpay.

A zero Prepay balance stops every key in all linked projects without moving
them to Free Tier. The roughly ten-minute billing pipeline can permit overages
or a negative balance, especially for long-running batches and agents.
Auto-reload can prevent a stop and has a monthly automatic-charge ceiling;
manual purchases do not count against that ceiling.

Eligible promotional Cloud credits are consumed before prepaid funds only
while the Prepay balance is positive. The $300 Welcome credit issued after
March 2, 2026 is ineligible. Delinquency on another Cloud service can suspend
API access even when prepaid funds remain.

Tier 3 accounts can become eligible to move the entire billing account to
Postpay. The move refunds unused prepaid credit, switches every linked project,
and cannot be reversed for that account. The manual switch control is
temporarily disabled.

## Do not use project spend caps as instant breakers

Editors, owners, and admins can set an experimental monthly project cap in AI
Studio. It survives a move between billing accounts while accumulated spend
resets. Both a project cap and zero prepaid balance can be exceeded during the
roughly ten-minute processing delay; long-running work may keep accruing cost.

## Evaluate quota dimensions and spend rate independently

Interactive enforcement separately checks requests per minute, input tokens
per minute, and requests per day. Exceeding any dimension fails the request.
Daily counters reset at midnight Pacific time. Limits are per project, not per
key; preview and experimental models are generally tighter. Active values in
AI Studio can change with tier and account status.

Paid tiers may also have a rolling ten-minute spend-rate limit: $10 for Tier 1
and $200 for Tiers 2 and 3. Crossing it produces `429 RESOURCE_EXHAUSTED` even
when RPM and TPM remain.

HTTP 400 and 500 requests are not billed for tokens, but still consume quota.
`GetTokens` requests are neither billed nor counted against inference quota.

## Capacity-plan Priority and Batch separately

Priority inference has a separate default limit at 0.3 times the corresponding
model-and-tier limit, while also counting toward overall interactive traffic.
Batch is isolated from non-batch quotas and supports 100 concurrent requests,
a 2 GB input file, and 20 GB stored files. Enqueued-token limits apply per
model across all active jobs.

Representative Tier 1 / Tier 2 / Tier 3 ceilings are:

- Gemini 3.6 Flash and 3.5 Flash: 3M / 400M / 1B.
- Gemini 3.5 Flash-Lite and 3.1 Flash Lite: 10M / 500M / 1B.
- Gemini 3.1 Pro Preview and 2.5 Pro: 5M / 500M / 1B.
- Gemini 2.5 Pro TTS: 25K / 100K / 1M.
- Gemini 2.5 Flash TTS: 100K / 100K / 4M.
- Gemini Embedding: 500K / 5M / 10M.
