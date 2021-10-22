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
        try:
            partner_id = self._get_partner_from_token(token)
            if http.request.httprequest.method == 'POST':
                vals = {
                    'parent_id': partner_id.id,
                    'company_id': partner_id.company_id.id,
                    'name': kw.get('name'),
                    'email': kw.get('email'),
                    'function': kw.get('function'),
                }
                contact_id = request.env['res.partner'].sudo().create(vals)
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
