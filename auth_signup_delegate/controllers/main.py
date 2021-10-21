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

    @http.route(
        '/signup/delegate/<string:token>',
        type="http",
        auth="public",
        website=True
    )
    def delegate_new_contact(self, token, **kw):
        partner_id = request.env['res.partner'].sudo().search(
            [('delegate_signup_token', '=', token)], limit=1
        )
        if not partner_id:
            raise werkzeug.exceptions.NotFound()
        # categories = [
        # ]  #http.request.env['helpdesk.ticket.category'].search([('active', '=', True)])
        # email = ''  #http.request.env.user.email
        # name = ''  #http.request.env.user.name
        return http.request.render(
            'auth_signup_delegate.create_contact', {
                'partner_id': partner_id,
                'token': token,
                # 'categories': categories,
                # 'email': email,
                # 'name': name
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
        vals = {
            'parent_id': kw.get('partner_id'),
            'name': kw.get('name'),
            'email': kw.get('email'),
            'function': kw.get('function'),
            # 'company_id': http.request.env.user.company_id.id,
        }
        partner_id = request.env['res.partner'].sudo().create(vals)
        return werkzeug.utils.redirect(
            "/signup/delegate/%s" % (kw.get('token'))
        )
