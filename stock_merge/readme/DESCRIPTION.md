This module adds a merge wizard for stock moves.

- Select multiple stock moves and merge them into one destination move.
- Automatically redirects linked references from source moves to the destination move.
- Cancels source moves before cleanup to allow safe deletion at the end of the merge flow.

## Technical details

**Wizard model**

The module provides `merge.stock.move.wizard`, inheriting `merge.object.wizard` from `base_merge`, with `_model_merge = "stock.move"` and `_table_merge = "stock_move"`.

**Merge behavior**

The `_merge` override forwards to `base_merge` using the 18.0 signature (`unique_xmlid`) and injects `mail_auto_subscribe_no_notify=True` on the destination move context to avoid auto-subscribe notifications during merge operations.

**Source record cleanup**

The `_log_merge_operation` override keeps base logging and then writes `{"state": "cancel"}` on source stock moves so they can be unlinked cleanly by the generic merge workflow.
