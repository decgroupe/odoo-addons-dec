from . import models


def set_mrp_production_request(env):
    for ref in env['ref.reference'].search([]):
        ref.product_id.mrp_production_request = True


def post_init(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    set_mrp_production_request(env)
