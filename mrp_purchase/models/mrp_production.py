# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    purchase_line_ids = fields.Many2many(
        'purchase.order.line',
        'purchase_order_line_mrp_rel',
        'production_id',
        'purchase_line_id',
        string="Subcontracted Services",
        readonly=True,
        copy=False,
        help="Purchase line generated by this Production Order",
    )

    def _post_bom_line_procurement_fail(self, bom_line):
        if not self.env.context.get('procurement_fail_no_notify'):
            message = _(
                "The procurement workflow for this line is not supported: "
                "<a href=# data-oe-model=mrp.bom.line "
                "data-oe-id=%d>%s</a>"
            ) % (bom_line.id, bom_line.display_name)
            self.message_post(body=message)

    def _action_launch_procurement_rule(self, bom_line, dict):
        self.ensure_one()
        if bom_line.product_id.purchase_ok:
            res = super()._action_launch_procurement_rule(bom_line, dict)
        else:
            self._post_bom_line_procurement_fail(bom_line)
            res = False
        return res

    def action_cancel(self):
        result = super().action_cancel()
        self.sudo()._activity_cancel_on_purchase()
        return result

    def _activity_cancel_on_purchase(self):
        """ If some MO are cancelled, we need to put an activity on their
            generated purchase. If sale lines of differents production orders
            impact different purchase, we only want one activity to be
            attached.
        """
        purchase_to_notify_map = {
        }  # map PO -> recordset of POL as {purchase.order: set(mrp.production)}

        purchase_order_lines = self.env['purchase.order.line'].search(
            [
                ('id', 'in', self.mapped('purchase_line_ids').ids),
                ('state', '!=', 'cancel')
            ]
        )
        for purchase_line in purchase_order_lines:
            purchase_to_notify_map.setdefault(
                purchase_line.order_id, self.env['purchase.order.line']
            )
            purchase_to_notify_map[purchase_line.order_id] |= purchase_line

        for purchase_order, purchase_lines in purchase_to_notify_map.items():
            purchase_order.activity_schedule_with_view(
                'mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid=
                'mrp_purchase.exception_purchase_on_mrp_cancellation',
                render_context={
                    'production_orders': purchase_lines.mapped('production_id'),
                    'purchase_order_lines': purchase_lines,
                }
            )
