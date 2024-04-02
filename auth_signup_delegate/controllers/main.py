import logging

import werkzeug

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class DelegateAuthSignup(http.Controller):
    #########################################################################

    def _get_partner_from_token(self, token):
        partner_id = (
            request.env["res.partner"]
            .sudo()
            .search([("delegate_signup_token", "=", token)], limit=1)
        )
        if not partner_id:
            raise werkzeug.exceptions.NotFound()
        return partner_id

    def _delegate_create_contact(self, token, message=False, **kw):
        error = False
        partner_id = False
        Partner = request.env["res.partner"].sudo()
        try:
            partner_id = self._get_partner_from_token(token)
            user_id = partner_id.user_ids and partner_id.user_ids[0] or False
            # user state is computed from `auth_signup` module
            # when last login date is set then user state is `active` otherwise `new`
            if not user_id or not user_id.active or user_id.state == "new":
                partner_id = False
                error = _(
                    "<b>"
                    "Your portal access must be active before you can create contacts."
                    "</b>"
                    "<div>"
                    "<small>"
                    "Please check your email to enable your account, or request a new "
                    "activation link by resetting your password from the login page."
                    "</small>"
                    "</div>"
                )
            if partner_id and http.request.httprequest.method == "POST":
                contact_id = Partner.search([("email", "=", kw.get("email"))])
                if contact_id:
                    # Having two or more contacts with the same email is
                    # forbidden for a portal access has it it used as a
                    # login identifier.
                    if len(contact_id) > 1:
                        raise UserError(
                            _(
                                "Multiple contacts already exists with "
                                "this email, please contact us."
                            )
                        )
                    # Before giving a portal access, ensure that this existing
                    # contact is a child of our partner.
                    else:
                        contact_id = Partner.search(
                            [
                                ("id", "=", contact_id.id),
                                ("id", "child_of", partner_id.id),
                            ]
                        )
                        if not contact_id:
                            raise UserError(
                                _(
                                    "This email already exists for a contact "
                                    "that is not a member of your company. "
                                    "You cannot grant him a portal access."
                                )
                            )
                    already_in_portal = (
                        request.env.ref("base.group_portal")
                        in contact_id.user_ids[0].groups_id
                    )
                    if already_in_portal:
                        raise UserError(
                            _(
                                "Contact %s (%s) already have an access "
                                "to the Portal."
                            )
                            % (contact_id.name, contact_id.email)
                        )
                else:
                    vals = {
                        "parent_id": partner_id.id,
                        "company_id": partner_id.company_id.id,
                        "name": kw.get("name"),
                        "email": kw.get("email"),
                        "function": kw.get("function"),
                    }
                    contact_id = Partner.delegate_create_contact(vals)
                # Use the partner's user to give portal access
                contact_id.with_user(user_id).give_portal_access()
                message = _(
                    "Contact %s has been created and a "
                    "confirmation e-mail has been sent to %s"
                ) % (contact_id.name, contact_id.email)
                kw["name"] = False
                kw["email"] = "".join(kw.get("email").partition("@")[1:])
        except UserError as e:
            error = plaintext2html(e.name)
        except werkzeug.exceptions.NotFound:
            error = _("Invalid Token")
        except Exception as e:
            error = str(e)

        return (
            "auth_signup_delegate.create_contact",
            {
                "partner_id": partner_id,
                "name": kw.get("name", False),
                "email": kw.get("email", False),
                "function": kw.get("function", False),
                "token": token,
                "message": message,
                "error": error,
            },
        )

    @http.route(
        "/signup/delegate/<string:token>",
        type="http",
        auth="public",
        website=True,
        csrf=True,
    )
    def delegate_create_contact(self, token, message=False, **kw):
        template_name, data = self._delegate_create_contact(token, message, **kw)
        return http.request.render(template_name, data)
