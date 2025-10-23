This module adds an API bridge between IoT devices and manufacturing orders.

- Update the quantity currently being produced on a manufacturing order from an external
  system.
- Send "done" or "cancel" notifications from the shop floor and create follow-up
  activities for responsible users.
- Display a numeric identifier and checksum on manufacturing orders to simplify secure
  remote calls.

## Technical details

**Remote manufacturing API**

The HTTP controller exposes JSON endpoints under `/api/mrp/v1/identifier/<identifier>`
for quantity update and done/cancel notifications. Requests are authenticated with API
keys, and production lookup supports both `identifier` and fallback by `name`.

**Production identifier and checksum**

The `mrp.production` model is extended with computed stored fields `identifier` and
`identifier_checksum`. The identifier strips non-digits from the production name, and a
custom checksum function is used to validate remote requests.

**Traceability and user activities**

Remote actions post chatter messages through `message_post_with_source` using module
templates, including caller IP and value changes. For done/cancel notifications,
module-specific `mail.activity.type` entries are scheduled for the assigned user when
needed.
