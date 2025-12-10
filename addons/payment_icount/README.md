# iCount Payment Provider

This module integrates the iCount payment gateway with Odoo's payment framework. It performs an immediate card charge, stores the card for future off-session billing, and issues a receipt document after every successful payment.

## Configuration
- Set environment variables `ICOUNT_CID`, `ICOUNT_USER`, and `ICOUNT_PASS` for authentication (kept out of logs and source code).
- Enable the *iCount* provider in **Accounting → Configuration → Payment Providers** and publish it on the website.
- Receipts are emailed automatically after successful payments.

## Flow
1. Charge card via `/cc/bill` (with optional `is_test` when the provider is in test mode).
2. Tokenize the card via `/cc_storage/store` for future charges.
3. Create a receipt document via `/doc/create` (`doctype=receipt`, `tax_exempt=1`) and email it to the customer.
4. Odoo processes the transaction result and stores the token.

A checkout notice informs customers that paying the deposit authorizes secure storage of their card for future balances.
