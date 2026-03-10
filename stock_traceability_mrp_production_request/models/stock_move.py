# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import models

from odoo.addons.tools_miscellaneous.tools.html_helper import format_hd


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_mto_status(self, html=False):
        super_res = super()._get_mto_status(html)
        res = []
        if self.created_mrp_production_request_id:
            head, desc = self.created_mrp_production_request_id.get_head_desc()
            res.append(format_hd(head, desc, html))
        else:
            res.extend(super_res)
        return res

    def action_view_created_item(self):
        super_action = super().action_view_created_item()
        if self.created_mrp_production_request_id:
            if self.created_mrp_production_request_id.mrp_production_ids:
                action = (
                    self.created_mrp_production_request_id.action_view_mrp_productions()
                )
            else:
                action = self.created_mrp_production_request_id.action_view()
        else:
            action = super_action
        return action

    def is_action_view_created_item_visible(self):
        # called to compute `action_view_created_item_visible` field
        self.ensure_one()
        res = super().is_action_view_created_item_visible() or (
            self.created_mrp_production_request_id
        )
        return res
