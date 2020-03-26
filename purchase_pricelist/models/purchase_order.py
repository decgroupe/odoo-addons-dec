from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=False,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        domain=[('type', '=', 'purchase')],
        help="Pricelist for current purchase order."
    )

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if self.partner_id:
            values = {
                'pricelist_id':
                    self.partner_id.property_product_pricelist_purchase and
                    self.partner_id.property_product_pricelist_purchase.id
                    or False,
            }

        self.update(values)