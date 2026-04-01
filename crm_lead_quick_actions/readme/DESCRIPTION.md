Adds a quick-delete button directly in the CRM leads list view, allowing
technical users to remove spam or junk leads without opening each record
individually.

- **Delete button in list view**: a trash-can icon button appears inline on
  each lead row, visible only when no partner is linked to the lead.
- **Restricted to technical users**: the button is only shown to members of
  the *Technical* group (`base.group_no_one`), preventing accidental deletions
  by regular users.

## Technical details

**Inline delete button**

The module inherits `crm.crm_case_tree_view_leads` via XPath and injects a
`<button name="unlink" type="object">` after the `team_id` field column.
The button carries `invisible="partner_id != False"` so it disappears as soon
as a partner is associated with the lead, ensuring only unqualified, orphaned
leads can be removed directly from the list.
