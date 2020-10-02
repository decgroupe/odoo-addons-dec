from . import models


def post_init(cr, registry):
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.users'].map_user_partner_to_calendar_event()
