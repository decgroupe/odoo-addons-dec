This module adds an image field to activity teams and displays the team
avatar in the activity widget when no user is individually assigned to the
activity.

- **Team image**: an image field (powered by `image.mixin`) is added to the
  `mail.activity.team` model and exposed in the team form view.
- **Activity sidebar avatar**: when an activity has a team but no assigned
  user, the team image (`image_128`) is displayed in the activity sidebar
  instead of the usual user avatar.

## Technical details

**Team image field**

`mail.activity.team` is extended with `image.mixin`, which adds the
`image_1920`, `image_1024`, `image_512`, `image_256`, and `image_128` fields.
The `image_1920` field is exposed in the team form view via an inherited view
that inserts a standard `widget="image"` field inside the `base` group.

**Activity sidebar avatar**

A QWeb template extension for `mail.Activity` inserts an `<img>` element
in the activity sidebar after the existing user-avatar anchor element. The
image is conditionally rendered only when `props.activity.user_id` is falsy
and `props.activity.team_id` is set, so it never conflicts with the standard
user avatar rendered by `mail_activity_team`.
