# iCount API Documentation Summary

## Coverage overview
- Authentication session lifecycle: start, inspect, and close (`auth/login`, session detail, and logout) described under `authentication_schemas`.
- Payment charge flow via `cc/bill` with test-mode flag (`is_test`) that simulates issuer success when card number is structurally valid.
- Card validation endpoints for number, expiration, and CVV checks, plus issuer/type detection helpers.
- Tokenization and stored card management (`cc_storage/store`, retrieval, update, and delete endpoints).
- Pre-authorization and card check flow (J5 preapproval transaction) and validation-only authorization transaction.
- Document operations including creation, close, cancellation with refund fields, and retrieval.
- Webhook management (add, list, get, delete) and event schemas located in `webhook_schemas`.
- Search and outbound communication helpers (document search, email, and SMS senders).

## Webhooks and signatures
- Webhook payload schemas and fields are provided in `icount_payment/webhook_schemas`, covering event structure and data payloads for reconciliation.

## Refund/cancellation details
- Document cancellation includes refund-related response fields described in the cancellation documentation, enabling mapping for refund outcomes.

## Test transactions
- Test mode is enabled by passing `"is_test": true` to `cc/bill`; any card number with a valid expiry yields a success response without contacting issuers.

## Next steps
- Documentation now includes response payload fields, authentication schemas, and webhook schemas. This is sufficient to proceed with implementing the iCount payment provider when required.
