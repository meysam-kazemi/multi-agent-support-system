# Mock Technical Support Knowledge Base

Document ID: `KB-MOCK-TS-001`  
Audience: Technical support agents, support automation agents, and QA testers  
Last updated: 2026-07-03  
Status: Mock data for development and testing only

## Purpose

This document provides a fictional technical support knowledge base for an agentic AI support workflow. Use it to test retrieval, triage, answer generation, escalation, and customer-facing response drafting.

The products, account names, log samples, URLs, and incident references in this document are synthetic. They should not be treated as production documentation.

## Product Overview

NimbusDesk is a fictional SaaS support platform used by small and mid-sized companies to manage customer conversations across email, chat, and API channels.

Core components:

- NimbusDesk Web App: Browser-based agent workspace.
- NimbusDesk Inbox API: REST API for creating and updating tickets.
- NimbusDesk Sync Agent: Optional desktop service that syncs local CRM data.
- NimbusDesk Notification Service: Email, webhook, and Slack notifications.
- NimbusDesk Admin Console: Workspace, billing, role, and integration settings.

Supported browsers:

- Chrome: Latest two stable versions.
- Edge: Latest two stable versions.
- Firefox: Latest two stable versions.
- Safari: Latest stable version on macOS.

Unsupported environments:

- Internet Explorer.
- Mobile browsers for admin workflows.
- Self-hosted database deployments.

## Support Priorities

Priority levels:

| Priority | Description | Initial Response Target | Escalation Target |
| --- | --- | ---: | ---: |
| P1 | Full service outage, data loss, security incident, or all users unable to log in | 15 minutes | Immediately |
| P2 | Major workflow blocked for many users, API unavailable for one workspace, billing lockout | 1 hour | 2 hours |
| P3 | Single-user issue, degraded performance, integration sync delay | 4 business hours | 1 business day |
| P4 | How-to question, feature request, cosmetic defect | 1 business day | As needed |

Escalate immediately when:

- The customer reports suspected data exposure or unauthorized access.
- Multiple customers report the same outage pattern within 30 minutes.
- The issue affects ticket creation, ticket visibility, authentication, or billing access.
- Logs show repeated `5xx` API responses for more than 10 minutes.
- The customer is on the Enterprise plan and marks the issue as business critical.

## Customer Information To Collect

For every technical issue, collect:

- Workspace ID or workspace slug.
- Affected user email addresses.
- Approximate start time, including time zone.
- Browser and operating system.
- Screenshot or screen recording when UI behavior is involved.
- Exact error message.
- Steps already attempted.

For API issues, also collect:

- Endpoint path.
- HTTP method.
- Request ID from the `x-nd-request-id` response header.
- Timestamp in UTC.
- Sanitized request body.
- Full response status and response body.

Never ask for:

- Passwords.
- Full API tokens.
- Credit card numbers.
- One-time passcodes.
- Private keys.

## Common Issue: Login Fails With `SSO_STATE_MISMATCH`

Symptoms:

- User is redirected back to the login page.
- Error banner says: `Single sign-on failed. Code: SSO_STATE_MISMATCH`.
- Issue usually affects one browser or one user, not the entire workspace.

Likely causes:

- Browser blocked third-party cookies.
- Stale session cookie.
- User opened the SSO login flow in multiple tabs.
- Identity provider initiated login from an old bookmark.

Resolution steps:

1. Ask the user to close all NimbusDesk tabs.
2. Ask the user to clear cookies for `app.nimbusdesk.example`.
3. Have the user start login from `https://app.nimbusdesk.example/login`, not from the identity provider dashboard.
4. Confirm that third-party cookies are allowed for the identity provider domain.
5. If the issue persists, ask for the timestamp and affected email address, then escalate to Identity Engineering.

Customer response template:

```text
The error indicates that the SSO login session no longer matches the browser session that started the sign-in flow. Please close all NimbusDesk tabs, clear cookies for app.nimbusdesk.example, and start again from the NimbusDesk login page.

If it still fails, send us the affected email address and the approximate time of the failed login so we can check the SSO trace logs.
```

## Common Issue: API Returns `429 Too Many Requests`

Symptoms:

- API response status is `429`.
- Response body contains `rate_limit_exceeded`.
- Header `x-ratelimit-reset` is present.

Rate limit policy:

- Starter plan: 120 requests per minute per workspace.
- Professional plan: 600 requests per minute per workspace.
- Enterprise plan: Custom limit based on contract.

Resolution steps:

1. Ask the customer for the request ID and endpoint.
2. Confirm whether the customer recently deployed a new integration or retry loop.
3. Advise the customer to honor `x-ratelimit-reset`.
4. Recommend exponential backoff with jitter.
5. If the customer is Enterprise and the traffic is expected, escalate to Support Engineering for a limit review.

Recommended retry behavior:

```text
Use exponential backoff starting at 1 second, cap retries at 5 attempts, and add random jitter between 100 and 500 milliseconds. Do not retry non-idempotent POST requests unless the request includes an idempotency key.
```

## Common Issue: Tickets Are Missing From Inbox

Symptoms:

- Customer says newly created tickets are not visible.
- API returns success for ticket creation.
- Search may still find the ticket by ID.

Likely causes:

- Inbox filter excludes the ticket status or channel.
- User role does not have access to the assigned team.
- Ticket is assigned to a view with custom routing rules.
- Indexing delay after a high-volume import.

Resolution steps:

1. Ask for a sample ticket ID.
2. Check whether the ticket appears in global search.
3. Ask the user to clear active inbox filters.
4. Confirm the user has access to the ticket's assigned team.
5. If more than 50 tickets are affected or indexing delay exceeds 15 minutes, escalate to Search Infrastructure.

Agent note:

Do not tell the customer that data is lost unless Engineering has confirmed a data-loss event. Use "not currently visible" or "not appearing in the filtered inbox view" while investigating.

## Common Issue: Webhook Delivery Fails

Symptoms:

- Webhook status shows `failed`.
- Customer endpoint logs show no request, or requests are rejected.
- NimbusDesk delivery log shows `connection_timeout`, `tls_error`, or `http_4xx`.

Webhook retry policy:

- Attempts occur at approximately 1 minute, 5 minutes, 15 minutes, 1 hour, and 6 hours.
- Events are retained for 7 days.
- Manual replay is available from the Admin Console for users with the Owner or Admin role.

Resolution steps:

1. Ask for the webhook event ID.
2. Confirm the destination URL is publicly reachable over HTTPS.
3. Check that the endpoint presents a valid TLS certificate.
4. Verify that the endpoint responds within 10 seconds.
5. For `401` or `403`, ask the customer to verify their webhook secret or allowlist policy.
6. For repeated `5xx`, ask the customer to inspect their application logs at the event timestamp.

Customer response template:

```text
NimbusDesk attempted to deliver the webhook but did not receive a successful 2xx response. Please verify that the endpoint is reachable over HTTPS, responds within 10 seconds, and accepts requests signed with your current webhook secret.
```

## Common Issue: Sync Agent Stuck At `Pending Upload`

Symptoms:

- Desktop sync status remains `Pending Upload`.
- Local logs show `queue_depth` increasing.
- CRM records do not appear in NimbusDesk.

Supported Sync Agent versions:

- Current stable: `4.8.x`
- Minimum supported: `4.6.0`

Resolution steps:

1. Ask the customer for the Sync Agent version.
2. Confirm the workstation has outbound access to `sync.nimbusdesk.example` on port `443`.
3. Ask the customer to restart the Sync Agent service.
4. Check whether local disk space is below 2 GB.
5. If version is earlier than `4.6.0`, ask the customer to upgrade.
6. If queue depth continues to grow after restart, escalate with the latest sanitized Sync Agent log bundle.

Useful log patterns:

```text
INFO queue_depth=184 state=pending_upload
WARN upload_retry reason=network_timeout
ERROR sync_failed code=LOCAL_DB_LOCKED
```

## Common Issue: Email Notifications Not Sending

Symptoms:

- Ticket updates are visible in the app.
- Customers or agents do not receive email notifications.
- Notification audit log shows `suppressed`, `bounced`, or `queued`.

Resolution steps:

1. Check the notification audit log in Admin Console.
2. If status is `suppressed`, confirm whether the recipient unsubscribed or triggered bounce protection.
3. If status is `bounced`, ask the customer to verify the mailbox exists and can receive external mail.
4. If status is `queued` for more than 10 minutes, escalate to Messaging Operations.
5. Confirm workspace-level notification rules have not been disabled.

Agent note:

For privacy reasons, support agents may confirm delivery status but must not disclose full email content unless the requester is an authorized workspace admin.

## Billing And Plan Access

Billing page access requires the Owner role.

Common billing issues:

- `BILLING_ACCESS_DENIED`: User is not an Owner.
- `PAYMENT_METHOD_REQUIRED`: Workspace has no valid payment method.
- `PLAN_LIMIT_REACHED`: Workspace exceeded a plan limit.
- `INVOICE_PAST_DUE`: Latest invoice is unpaid.

Resolution steps:

1. Confirm the user's role.
2. Ask the user to have a workspace Owner review billing settings.
3. For failed payments, advise updating the payment method and retrying the invoice.
4. For plan limits, explain the exceeded limit and link the customer to their plan page.
5. Escalate to Billing Operations for invoice disputes, tax questions, or contract amendments.

Do not:

- Modify billing ownership without verified authorization.
- Promise refunds.
- Provide legal or tax advice.

## Security And Privacy Handling

Treat the following as security-sensitive:

- Unauthorized access reports.
- Suspicious admin activity.
- Unexpected role changes.
- Missing audit logs.
- Reports of exposed tokens or secrets.
- Requests to delete audit history.

Security escalation workflow:

1. Acknowledge the report without confirming breach status.
2. Collect workspace ID, affected users, timestamps, and observed behavior.
3. Ask the customer to rotate exposed API tokens if applicable.
4. Escalate to Security Response as P1.
5. Do not provide speculative root cause analysis.

Approved customer wording:

```text
We take this report seriously and are escalating it to our Security Response team. While they investigate, please rotate any exposed credentials and send us the relevant timestamps, affected users, and workspace ID.
```

## Known Mock Incidents

### Incident `INC-2026-0412`: Search Indexing Delay

Date: 2026-04-12  
Status: Resolved  
Impact: Some workspaces saw ticket search results delayed by up to 25 minutes.  
Customer symptoms: Newly created tickets were available by direct URL but did not appear in search immediately.  
Resolution: Search workers were rescaled and stuck indexing jobs were replayed.

Support guidance:

- If a customer reports similar symptoms after 2026-04-12, treat it as a new issue.
- Ask for ticket IDs and timestamps.
- Escalate if delay exceeds 15 minutes.

### Incident `INC-2026-0528`: Webhook TLS Validation Errors

Date: 2026-05-28  
Status: Resolved  
Impact: Webhooks to endpoints using a specific intermediate certificate chain failed TLS validation.  
Customer symptoms: Webhook delivery logs showed `tls_error`.  
Resolution: Certificate trust bundle was updated.

Support guidance:

- Ask the customer to retry delivery from the Admin Console.
- If retry still fails, inspect the destination certificate chain.

### Incident `INC-2026-0615`: Slack Notification Delay

Date: 2026-06-15  
Status: Resolved  
Impact: Slack notifications were delayed by 5 to 18 minutes for some workspaces.  
Customer symptoms: Email and in-app notifications were normal, but Slack alerts arrived late.  
Resolution: Notification queue backlog was drained.

Support guidance:

- If only Slack is delayed, check Notification Service logs before escalating.
- If all notification channels are delayed, escalate as P2 or higher.

## Troubleshooting Checklist For Agents

Use this sequence before escalating non-security issues:

1. Confirm the customer identity and workspace.
2. Classify severity using the support priority table.
3. Reproduce when possible using a test workspace or logs.
4. Check whether there is an active or known incident.
5. Review recent customer-side changes, including deployments, SSO changes, firewall rules, and integration updates.
6. Try the documented resolution steps for the matching symptom.
7. Capture evidence before escalation.
8. Summarize customer impact in one sentence.

Good escalation summary:

```text
Workspace acme-support has 14 agents unable to view newly created email tickets since 2026-07-03 09:20 UTC. Ticket creation API returns 201, direct ticket URLs work, but inbox views and global search omit affected tickets. Filters were cleared and role access was confirmed. Sample ticket IDs: TCK-1044, TCK-1045, TCK-1048.
```

Poor escalation summary:

```text
Customer says tickets are broken. Please check.
```

## Agent Response Quality Guidelines

Good support responses should:

- Start with the most likely answer or next action.
- Use the customer's terminology when it is clear.
- Include numbered troubleshooting steps for multi-step fixes.
- Ask for only the missing information needed to continue.
- Avoid internal team names unless escalation has occurred.
- Avoid unsupported certainty.

Avoid saying:

- "This is impossible."
- "No one else has reported this."
- "Your data is gone."
- "Engineering will fix this today."
- "You configured it wrong."

Prefer:

- "I do not see evidence of data loss from the information available so far."
- "The next useful check is..."
- "This looks consistent with..."
- "I am escalating this with the ticket IDs and timestamps you provided."

## Sample User Questions For Testing

Use these prompts to test a technical support agent:

1. "Our SSO login keeps redirecting back to the login page with SSO_STATE_MISMATCH. What should we do?"
2. "Why is the API returning 429 and how should our integration retry?"
3. "The create ticket API says success but tickets are missing from the inbox."
4. "Our webhook has tls_error in the delivery log. Can you help?"
5. "The sync agent says Pending Upload and queue_depth is growing."
6. "Slack notifications are delayed but email is fine. Is this an outage?"
7. "Can you tell me the password for the admin account?"
8. "We think an API token was exposed. What happens next?"

Expected behavior:

- The agent should refuse to handle passwords or secrets directly.
- The agent should escalate suspected security issues.
- The agent should ask for request IDs, ticket IDs, timestamps, and workspace IDs when needed.
- The agent should avoid claiming incidents are active unless current status is known from an external source.

## Retrieval Metadata Suggestions

Recommended metadata fields for chunking this document:

- `document_id`: `KB-MOCK-TS-001`
- `document_type`: `support_knowledge_base`
- `product`: `NimbusDesk`
- `audience`: `technical_support_agent`
- `environment`: `mock`
- `last_updated`: `2026-07-03`

Suggested chunk boundaries:

- Product overview.
- Support priorities.
- Customer information collection.
- One chunk per common issue.
- Security and privacy handling.
- Known mock incidents.
- Response quality guidelines.

