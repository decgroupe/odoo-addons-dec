
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=True,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        domain=[('type', '=', 'sale')],
        help="Pricelist for current sales order."
    )
