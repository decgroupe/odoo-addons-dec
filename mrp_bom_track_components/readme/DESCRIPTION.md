Track changes to Bill of Materials lines automatically.

Every `write()` on a BoM that touches `bom_line_ids` is instrumented:
additions, removals, and field-level edits (product, quantity, supplier,
unit of measure, prices, etc.) are detected and posted as a formatted
chatter message on the BoM record, giving a full audit trail of component
changes.

## Technical details

`MrpBom.write()` captures a snapshot of all BoM lines before the write
using `get_track_state()`.  After the write, `set_track_state()` compares
the two snapshots, classifies differences as added / removed / edited lines,
and posts a note via `message_post_with_source()` using the QWeb template
`track_bom_template` defined in `views/bom_template.xml`.

Float fields (e.g. `product_qty`) are compared with `float_compare` to
avoid spurious change detection caused by floating-point rounding.
