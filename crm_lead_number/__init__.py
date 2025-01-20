from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, dict())
    lead_ids = env["crm.lead"].search([("type", "=", "opportunity")], order="id")
    for lead_id in lead_ids:
        lead_id._init_number()
