This module lets a portal user delegate the creation of new portal contacts
to their colleagues, without requiring any intervention from an internal user.

- A unique sign-up URL is generated for each portal user (token-based).
- Anyone who visits the URL can submit a form to create a new contact under
  the token owner's company.
- The new contact is automatically granted portal access once created.
- If the submitted e-mail already belongs to an existing contact that is a
  child of the company, portal access is granted directly without creating a
  duplicate.

## Technical details

**Token management (`res.partner`)**

A `delegate_signup_token` (Char, restricted to ERP managers) is added to
`res.partner`. The methods `delegate_signup_prepare()` and
`delegate_signup_cancel()` generate and revoke the token respectively.
`get_delegate_signup_url()` builds the full public URL from the token and the
`web.base.url` system parameter.

**Wizard (`res.partner.signup.delegate`)**

A transient wizard opened from the partner form view allows internal users to
generate or revoke the delegation token and copy the resulting URL.

**HTTP controller (`/signup/delegate/<token>`)**

A public route handles the sign-up form. On POST it:
1. Resolves the partner from the token and checks that the linked user is an
   active portal user.
2. Searches for an existing contact with the submitted e-mail; if found,
   verifies it is already a child of the token owner's company before granting
   portal access.
3. If no contact exists, creates a new child contact under the token owner's
   company and then grants portal access via `portal.wizard`.

**Portal access (`give_portal_access`)**

Portal access is granted through the standard `portal.wizard` model, using the
token owner's user context to ensure access-control rules are respected.
