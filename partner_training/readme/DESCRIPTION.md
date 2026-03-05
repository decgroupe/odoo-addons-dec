This module helps classify contacts by educational training and specialty.

- Add training specialties directly on partner records using tags.
- Manage a catalog of educational trainings and their specialties.
- Search and group specialties by training to keep your taxonomy consistent.

## Technical details

**Partner extension**

The module extends `res.partner` with a `training_specialty_ids` many2many field
to `res.partner.training.specialty`, and injects this field in the partner form
view before `category_id` with a tags widget.

**Training and specialty models**

The module introduces `res.partner.training` and
`res.partner.training.specialty` models. Training stores the master category,
and specialty links to one training with `training_id`.

`res.partner.training.specialty` computes `complete_name` and `search_name`
from `training_id`, `name`, and `acronym` in `_compute_names` to improve
display and lookup.

SQL constraints enforce uniqueness of:

- `res.partner.training.name`
- (`training_id`, `name`) on specialties
- (`training_id`, `acronym`) on specialties

**UI and navigation**

The module provides dedicated list/form/search views and actions for trainings
and specialties, plus Contacts configuration menus restricted through the
module security groups.
