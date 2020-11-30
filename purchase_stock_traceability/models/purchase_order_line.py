# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import models, api, fields

from odoo.addons.tools_miscellaneous.tools.html_helper import (
    div, ul, li, small, b, format_hd
)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    procurement_origin = fields.Html(
        compute='_compute_procurement_origin',
        default='',
        store=False,
    )

    @api.multi
    @api.depends(
        'move_dest_ids',
    )
    def _compute_procurement_origin(self):
        for line in self:
            line.procurement_origin = line.get_origin(html=True)

    def get_origin(self, html=False):
        status = []
        main_state = ''
        if self.orderpoint_ids:
            head, desc = self.orderpoint_ids[0].get_head_desc()
            status.append(format_hd(head, desc, html))
        if self.procurement_group_id:
            production_ids = self.move_dest_ids.mapped(
                'raw_material_production_id'
            )
            if not production_ids:
                production_ids = self.procurement_group_id.mapped(
                    'mrp_production_ids'
                )
            if production_ids:
                head, desc = production_ids[0].get_head_desc()
                status.append(format_hd(head, desc, html))

            sale_line_ids = self.move_dest_ids.mapped('sale_line_id')
            if sale_line_ids:
                head, desc = sale_line_ids[0].get_head_desc()
                status.append(format_hd(head, desc, html))

            head, desc = self.procurement_group_id.get_head_desc()
            status.append(format_hd(head, desc, html))

        return self._format_status_header(status, main_state, html)

    def _format_status_header(self, status, state, html=False):
        if html:
            list_as_html = ''.join(list(map(li, status)))
            return div(ul(list_as_html), 'd_move d_move_' + state)
        else:
            return '\n'.join(status)
