This module lets you prevent selected contacts from inheriting access to their
company's business documents.

- Keep the usual behavior for most contacts by inheriting the company as the
	commercial partner.
- Disable inheritance on specific child contacts when they must not see all
	documents linked to the parent company in the portal.
- Keep portal visibility consistent with this setting so each contact only sees
	allowed records.

## Technical details

**Commercial partner fencing**

The module extends `res.partner` with `inherit_commercial_partner` (Boolean,
default True). In `_compute_commercial_partner`, when this flag is disabled on
a non-company contact, `commercial_partner_id` is forced to the contact itself
instead of the parent company.

**Unfenced traversal for domains**

`unfenced_commercial_partner_id` is a stored computed field that always follows
the parent chain independently from the fencing flag. This gives a stable
commercial tree anchor for security domains.

**Portal security rule update**

The module updates `base.res_partner_portal_public_rule` so the portal domain
uses `user.unfenced_commercial_partner_id`, which enforces contact-level
fencing for business document access.

**Partner synchronization adjustment**

In `_commercial_sync_from_company`, if a fenced child contact would keep the
same VAT as its parent, the VAT value is cleared to avoid inheriting company
identification data unintentionally.
