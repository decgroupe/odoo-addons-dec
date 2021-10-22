import logging
import werkzeug

from odoo import http, _
# from odoo.addons.auth_signup.models.res_users import SignupError
# from odoo.addons.web.controllers.main import ensure_db, Home
# from odoo.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard as Dashboard
from odoo.exceptions import UserError
from odoo.http import request

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
        website=True
    )
    def delegate_new_contact(self, token, message=False, **kw):
        return http.request.render(
            'auth_signup_delegate.create_contact', {
                'partner_id': self._get_partner_from_token(token),
                'token': token,
                'message': message,
            }
        )

    @http.route(
        '/signup/delegate/create',
        type="http",
        auth="public",
        website=True,
        csrf=True
    )
    def delegate_create_contact(self, **kw):
        message = False
        token = kw.get('token')
        if http.request.httprequest.method == 'POST':
            partner_id = self._get_partner_from_token(token)
            vals = {
                'parent_id': partner_id.id,
                'name': kw.get('name'),
                'email': kw.get('email'),
                'function': kw.get('function'),
                # 'company_id': http.request.env.user.company_id.id,
            }
            partner_id = request.env['res.partner'].sudo().create(vals)
            partner_id.give_portal_access()
            message = _(
                "Contact %s has been created and a "
                "confirmation e-mail has been sent to %s"
            ) % (partner_id.name, partner_id.email)
        # res =  werkzeug.utils.redirect(
        #     "/signup/delegate/%s" % (kw.get('token'))
        # )
        return self.delegate_new_contact(token, message)
