This module allows merging duplicate city and zip/postal-code records directly
from the list views of `res.city` and `res.city.zip`.

- **Merge cities**: select multiple city records and merge them into one
  destination city. All zip codes belonging to the merged cities are
  automatically reassigned to the destination city; zip codes with the same
  name are themselves merged beforehand to avoid duplicates.
- **Merge zip codes**: select multiple `res.city.zip` records and merge them
  into one destination zip code. All documents referencing the merged zip
  codes are transparently redirected to the destination record.

## Technical details

**Merge city wizard (`merge.res.city.wizard`)**

Inherits `merge.object.wizard` from `base_merge`. Overrides `_merge` to
pre-process zip codes: before merging the cities it groups all zip records
of the source cities by name and merges each group using
`merge.res.city.zip.wizard._merge`, so that the destination city ends up
with at most one zip record per postal code.

**Merge zip wizard (`merge.res.city.zip.wizard`)**

Inherits `merge.object.wizard` from `base_merge` and delegates entirely
to the parent `_merge` implementation, which rewrites all foreign-key
references pointing to the discarded records.

Both wizards are registered as server actions bound to the `list` view of
their respective models and are restricted to users who belong to the
`res_group_base_location_do_merge` security group.
