# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def action_view_base(self):
        return self.env.ref(
            'purchase_action_view.action_purchase_order_line_tree'
        ).read()[0]

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action['domain'] = [('id', 'in', self.ids)]
        else:
            form = self.env.ref('purchase.purchase_order_line_form2')
            action['views'] = [(form.id, 'form')]
            action['res_id'] = self.ids[0]
        return action
