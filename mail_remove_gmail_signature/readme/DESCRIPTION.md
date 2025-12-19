This module removes automatic Gmail signatures from incoming emails sent by your own company users.

- keeps internal discussions clean by removing repeated signature blocks in message bodies.
- applies only to emails coming from your configured company mail domains.
- leaves messages from external domains unchanged.

## Technical details

**Mail parsing hook**

The module extends `mail.thread` and overrides
`_message_parse_process_body_before_sanitize` to post-process inbound email
HTML before sanitization.

**Domain filtering**

The helper `_message_belong_to_us` checks the sender domain from the `From`
header against `mail.catchall.domain` and optional
`mail.catchall.domain.allowed` values in `ir.config_parameter`.

**Signature removal logic**

The helper `_remove_gmail_signatures` parses the HTML body and removes nodes
tagged as Gmail signatures (`data-smartmails` or CSS class containing
`gmail_signature`), then serializes the cleaned HTML back to text.
