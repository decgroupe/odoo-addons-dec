# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, models

from odoo.addons.tools_miscellaneous.tools.html_helper import format_hd


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_mto_status(self, html=False):
        """Return the MTO status using the production request head/desc when one
        is linked, otherwise fall back to the parent implementation.
        """
        super_res = super()._get_mto_status(html)
        res = []
        if self.created_mrp_production_request_id:
            head, desc = self.created_mrp_production_request_id.get_head_desc()
            res.append(format_hd(head, desc, html))
        else:
            res.extend(super_res)
        return res

    def action_view_created_item(self):
        """Open the production request form, or its manufacturing orders when
        some exist, when a production request is linked to this move.
        """
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

    @api.depends("created_mrp_production_request_id")
    def _compute_action_view_created_item_visible(self):
        """Extend dependency to recompute visibility when the production request
        link changes.
        """
        return super()._compute_action_view_created_item_visible()

    def _get_mto_created_items(self):
        """Also include the linked production request so that visibility
        of the `action_view_created_item` button is computed correctly.
        """
        res = super()._get_mto_created_items()
        if self.created_mrp_production_request_id:
            action = self.created_mrp_production_request_id.action_view()
            res["stock_traceability_mrp_production_request"] = {
                "priority": 35,
                "record": self.created_mrp_production_request_id,
                "action": action,
            }
        return res
