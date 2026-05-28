This module redirects procurement exception activities to the right recipients
based on configurable redirection rules.

- It helps route exception follow-up to the right team without manual
	reassignment.
- It keeps exception handling aligned with your company workflow for
	procurement-related activities.

## Technical details

**Procurement exception redirection**

The module extends procurement exception handling so generated activities can
be reassigned through module-specific redirection logic instead of default
recipient assignment.

**Rule-based recipient resolution**

Recipient selection is computed from configured redirection rules and applied
at activity creation/update time so exception notifications reach the intended
users.

**Compatibility note**

The behavior should be reviewed when deployed together with modules that also
alter activity recipients, such as mail_activity_redirection, to ensure there
is no overlap or conflicting redirection chain.
