from . import models


def post_init_hook(env):
    lead_ids = env["crm.lead"].search([("type", "=", "opportunity")], order="id")
    for lead_id in lead_ids:
        lead_id._init_number()
