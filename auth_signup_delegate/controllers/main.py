import logging
import werkzeug

from odoo import http, _
# from odoo.addons.auth_signup.models.res_users import SignupError
# from odoo.addons.web.controllers.main import ensure_db, Home
# from odoo.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard as Dashboard
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class DelegateAuthSignup(http.Controller):

    #########################################################################

    def _get_partner_from_token(self, token):
        partner_id = request.env['res.partner'].sudo().search(
            [('delegate_signup_token', '=', token)], limit=1
        )
        if not partner_id:
            raise werkzeug.exceptions.NotFound()
        return partner_id

    @http.route(
        '/signup/delegate/<string:token>',
        type="http",
        auth="public",
        website=True,
        csrf=True
    )
    def delegate_create_contact(self, token, message=False, **kw):
        error = False
        partner_id = False
        Partner = request.env['res.partner'].sudo()
        try:
            partner_id = self._get_partner_from_token(token)
            if http.request.httprequest.method == 'POST':
                contact_id = Partner.search([('email', '=', kw.get('email'))])
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
                                ('id', '=', contact_id.id),
                                ('id', 'child_of', partner_id.id)
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
                    already_in_portal = request.env.ref(
                        'base.group_portal'
                    ) in contact_id.user_ids[0].groups_id
                    if already_in_portal:
                        raise UserError(
                            _(
                                "Contact %s (%s) already have an access "
                                "to the Portal."
                            ) % (contact_id.name, contact_id.email)
                        )
                else:
                    vals = {
                        'parent_id': partner_id.id,
                        'company_id': partner_id.company_id.id,
                        'name': kw.get('name'),
                        'email': kw.get('email'),
                        'function': kw.get('function'),
                    }
                    contact_id = Partner.delegate_create_contact(vals)
                contact_id.give_portal_access()
                message = _(
                    "Contact %s has been created and a "
                    "confirmation e-mail has been sent to %s"
                ) % (contact_id.name, contact_id.email)
                kw['name'] = False
                kw['email'] = ''.join(kw.get('email').partition('@')[1:])
        except UserError as e:
            error = plaintext2html(e.name)
        except werkzeug.exceptions.NotFound:
            error = _('Invalid Token')
        except Exception as e:
            error = str(e)

        return http.request.render(
            'auth_signup_delegate.create_contact', {
                'partner_id': partner_id,
                'name': kw.get('name', False),
                'email': kw.get('email', False),
                'function': kw.get('function', False),
                'token': token,
                'message': message,
                'error': error,
            }
        )
