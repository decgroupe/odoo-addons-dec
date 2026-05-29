This module adds a merge wizard for units of measure (UoM), allowing
authorized users to consolidate duplicate or redundant UoM records into a
single destination record.

- **Merge wizard**: select multiple UoM records from the list view and merge
  them into one, redirecting all related documents to the destination record.
- **Access control**: only users who belong to the "Show Unit of Measure Wizard
  Merge Action" group can perform the merge operation.
- **Category validation bypass**: the merge action disables the UoM category
  reference uniqueness check during the operation, so UoMs can be freely
  merged without triggering category integrity errors.

## Technical details

**Merge wizard**

Extends `merge.object.wizard` (provided by `base_merge`) with a new transient
model `merge.uom.uom.wizard` that targets the `uom.uom` model. The action is
bound to the UoM list view and restricted to members of the
`uom_merge.res_group_do_merge` security group.

**Access control**

`_merge()` is overridden to raise `AccessDenied` if the current user does not
belong to `uom_merge.res_group_do_merge`, regardless of how the wizard is
invoked.

**Category validation bypass**

`uom.uom._check_category_reference_uniqueness()` is overridden to skip its
logic when the `skip_uom_category_validation` key is present and truthy in
the context. The merge action sets this context key automatically.
The source records are deleted via `sudo()` to ensure the deletion succeeds
even if the current user lacks the necessary unlink rights on UoM records.
