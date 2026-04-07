This module adds a **Consumed Value** monetary field to manufacturing orders
(`mrp.production`). The value is computed from the purchase price history of
each raw material at the time its stock move was completed.

When a manufacturing order is marked as done, a chatter message is
automatically posted with the total consumed value formatted in the company
currency.

## Technical details

- `MrpProduction._compute_consumed_value` iterates over all done raw material
  moves and retrieves the latest `product.prices.history` record of type
  `purchase` whose `datetime` is on or before the move date. The unit price is
  multiplied by the moved quantity and accumulated into `consumed_value`.
- `MrpProduction.button_mark_done` detects newly-completed moves and calls
  `_message_post_consumed_value` to log the formatted total in the chatter.
- The `consumed_value` and `company_currency_id` fields are added to the
  manufacturing form view under the `base.group_no_one` debug group.
