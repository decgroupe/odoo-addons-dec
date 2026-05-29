This module provides a reusable base wizard for merging duplicate records in
any Odoo model.

- Merge two or more records of any model into a single destination record.
- Foreign-key references and computed fields on the merged records are
  automatically updated to point to the destination.
- External IDs (xmlids) are deduplicated so the destination retains at most
  one stable xmlid after the merge.
- The maximum number of objects that can be merged at once is controlled by
  the system parameter `base_merge.merge_objects_max_number`.

## Technical details

**Base wizard**

`merge.object.wizard` is a transient model that implements the full merge
pipeline in the following steps:

1. `_ensure_unique_externalid` - deduplicates `ir.model.data` entries across
   source and destination records.
2. `_update_foreign_keys` - rewrites every many2one column that points to a
   source record so it points to the destination instead.
3. `_update_reference_fields` - updates `ir.model.fields` reference-type
   columns in the same way.
4. `_update_values` - copies non-empty field values from source records to the
   destination (summable fields are summed).
5. `_update_computed_fields` - triggers recomputation of stored computed fields
   on the destination.
6. `_delete_source_objects` - unlinks the source records.

**Extending the wizard**

Create a concrete wizard by inheriting `merge.object.wizard`, setting
`_model_merge` to the target model name and `_table_merge` to its database
table, and overriding `_get_summable_fields` when numeric fields should be
summed rather than replaced.
