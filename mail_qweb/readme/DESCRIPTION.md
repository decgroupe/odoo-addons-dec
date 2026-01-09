This module enhances Odoo email notifications rendered with QWeb templates.

- Lets users render and send richer QWeb-based email templates from standard mail features.
- Improves notification emails by exposing recipient and context information to templates.
- Adds helpers for cleaner template expressions and optional control over CSS inlining.

## Technical details

**mail.template integration**

The module extends `mail.template` to pre-render selected fields (including
subject), pass template context data through the rendering flow, and optionally
replace local links in generated HTML when no external layout is used.

**mail.render.mixin rendering context**

The module injects additional rendering helpers into the evaluation context,
including `is_html_empty` and a `remaining_days` helper, and enriches each
record rendering context with pre-rendered values and an access link.

**mail.thread notification context**

The module extends notification classification and email rendering context to
preserve recipient grouping data, expose it to QWeb templates, and compute
message content alignment from message HTML structure.

**mail.mail processing**

The module applies premailer transformation on created outgoing mails,
including a template-level switch to disable CSS inlining when needed.

**ir.qweb rendering traceability**

The module extends `ir.qweb` rendering to inject `env` into template values and
log rendered view identity and context for debugging.
