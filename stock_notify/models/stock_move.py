# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    notify_assigned = fields.Boolean(
        help="If checked, the picking owner will receive a notification "
        "when this move becomes assigned",
    )

    def write(self, vals):
        if vals.get('state') == 'assigned':
            for rec in self.filtered('notify_assigned').filtered('picking_id'):
                product_name = rec.product_id.name_get()[0][1]
                group_id = rec.group_id and rec.group_id.name or ''
                rec.picking_id.message_post(
                    body=_(
                        'Product <small><b>%s</b></small> was reserved and is '
                        'now ready to be picked up for <small><b>%s</b></small>.'
                        '<br>Please open and validate %s.'
                    ) %
                    (product_name, rec.picking_id.origin, rec.picking_id.name),
                    subject=_('⏱️ %s picking ready') % (group_id),
                    subtype_id=self.env.ref('mail.mt_note').id,
                )
        return super(StockMove, self).write(vals)
