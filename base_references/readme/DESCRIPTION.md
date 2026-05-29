This module adds a wizard that finds all records in the database that reference
a given record, making it easy to audit dependencies before deleting or
archiving data.

- Find references: from any model's form view, open the *Find References*
  action to discover every record that points to the current entry via a
  relational field.
- Filtered results: the result list shows the referencing model, the record
  display name, the field name and label, and the type of relation, with a
  direct *Open* button to navigate to each referencing record.
- Inclusive search: archived records are included in the scan so that no
  hidden dependency is missed.

## Technical details

**Reference search wizard (`base.references.wizard`)**

The wizard is pre-filled with the active model and record ID from the context
when opened via the action binding on `ir.model`. `action_search_references`
iterates over `ir.model.fields` filtered to fields of type `many2one`,
`many2many`, `reference`, and `many2one_reference` whose `relation` column
points to the target model. For each matching field it builds a domain and
searches the owning model with `sudo()` and `active_test=False` so that
archived records are also returned. `one2many` fields are intentionally
excluded to avoid duplicating results already captured by the `many2one`
traversal on the other side.

**Result records (`base.references.result`)**

Each hit is stored as a transient `base.references.result` record linked to the
wizard. The `action_open_record` method returns an `ir.actions.act_window`
action to navigate directly to the referencing record.
