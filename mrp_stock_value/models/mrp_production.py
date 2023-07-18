# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from odoo import _, api, fields, models
from odoo.tools import formatLang


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    company_currency_id = fields.Many2one(
        string="Currency",
        related="company_id.currency_id",
        readonly=True,
        relation="res.currency",
    )
    consumed_value = fields.Monetary(
        string="Consumed Value",
        currency_field="company_currency_id",
        compute="_compute_consumed_value",
        store=False,
    )

    @api.depends("move_raw_ids")
    def _compute_consumed_value(self):
        PricesHistory = self.env["product.prices.history"]
        PRICE_TYPE = "purchase"
        self.consumed_value = 0
        for rec in self:
            all_move_ids = rec.move_raw_ids.filtered(lambda x: x.state == "done")
            for move_id in all_move_ids:
                history = PricesHistory.search(
                    [
                        ("company_id", "=", rec.company_id.id),
                        ("product_id", "=", move_id.product_id.id),
                        ("datetime", "<=", move_id.date),
                        ("type", "=", PRICE_TYPE),
                    ],
                    order="datetime desc, id desc",
                    limit=1,
                )
                if history:
                    price = history.get_price(PRICE_TYPE)
                    rec.consumed_value += price * move_id.quantity_done
                else:
                    print(move_id)

    def button_mark_done(self):
        moves_done = {}
        for rec in self:
            all_move_ids = rec.move_raw_ids.filtered(lambda x: x.state == "done")
            moves_done[rec.id] = len(all_move_ids)
        res = super().button_mark_done()
        for rec in self:
            all_move_ids = rec.move_raw_ids.filtered(lambda x: x.state == "done")
            if len(all_move_ids) != moves_done[rec.id]:
                rec._message_post_consumed_value()
        return res

    def _message_post_consumed_value(self):
        self.ensure_one()
        formatted_price = formatLang(
            self.env,
            self.consumed_value,
            currency_obj=self.company_currency_id,
        )
        message = _("Consumed value = %s") % (formatted_price)
        # Use message log to post a message without notifications
        self._message_log(body=message)
