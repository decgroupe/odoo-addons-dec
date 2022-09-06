# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import _, models, api, fields

from odoo.addons.tools_miscellaneous.tools.html_helper import (
    div, ul, li, small, b, format_hd
)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    procurement_origin = fields.Html(
        compute='_compute_origin',
        default='',
        store=False,
    )
    action_view_origin_item_visible = fields.Boolean(
        string="Show Link to Origin Item",
        compute='_compute_origin',
        readonly=True,
    )

    @api.multi
    @api.depends('move_dest_ids')
    def _compute_origin(self):
        for line in self:
            origins = line._get_origins_dict()
            line.procurement_origin = line.format_origins_dict(
                origins, html=True
            )
            line.action_view_origin_item_visible = \
                origins.get('orderpoint_ids') \
                or origins.get('production_ids') \
                or origins.get('sale_line_ids') \
                or origins.get('procurement_group_id')

    def _get_origins_dict(self):
        res = {
            'orderpoint_ids': False,
            'production_ids': False,
            'sale_line_ids': False,
            'sale_order_ids': False,
            'picking_ids': False,
            'procurement_group_id': False,
        }
        if self.orderpoint_ids:
            res['orderpoint_ids'] = self.orderpoint_ids

        production_ids = self.move_dest_ids.mapped('raw_material_production_id')
        if not production_ids and self.procurement_group_id:
            production_ids = self.procurement_group_id.mapped(
                'mrp_production_ids'
            )
        if production_ids:
            res['production_ids'] = production_ids

        sale_line_ids = self.move_dest_ids.mapped('sale_line_id')
        if sale_line_ids:
            res['sale_line_ids'] = sale_line_ids
            res['sale_order_ids'] = sale_line_ids.mapped('order_id')

        picking_ids = self.move_dest_ids.mapped('picking_id')
        if picking_ids:
            res['picking_ids'] = picking_ids

        if self.procurement_group_id:
            res['procurement_group_id'] = self.procurement_group_id

        return res

    def format_origins_dict(self, origins, html=False):
        status = []
        main_state = ''
        if origins.get('orderpoint_ids'):
            head, desc = origins.get('orderpoint_ids')[0].get_head_desc()
            status.append(format_hd(head, desc, html))
        if origins.get('production_ids'):
            head, desc = origins.get('production_ids')[0].get_head_desc()
            status.append(format_hd(head, desc, html))
        if origins.get('sale_line_ids'):
            head, desc = origins.get('sale_line_ids')[0].get_head_desc()
            status.append(format_hd(head, desc, html))
        if origins.get('procurement_group_id'):
            head, desc = origins.get('procurement_group_id').get_head_desc()
            status.append(format_hd(head, desc, html))
        if origins.get('picking_ids'):
            head, desc = origins.get('picking_ids')[0].get_head_desc()
            status.append(format_hd(head, desc, html))
            if origins.get('picking_ids')[0].note:
                head, desc = '📝', origins.get('picking_ids')[0].note
                status.append(format_hd(head, desc, html))
        # Return formatted string (plaintext or html)
        return self._format_status_header(status, main_state, html)

    def _format_status_header(self, status, state, html=False):
        if html:
            list_as_html = ''.join(list(map(li, status)))
            return div(ul(list_as_html), 'd_move d_move_' + state)
        else:
            return '\n'.join(status)

    def action_view_origin_item(self):
        self.ensure_one()
        origins = self._get_origins_dict()
        if origins.get('orderpoint_ids'):
            action = origins.get('orderpoint_ids').action_view()
        elif origins.get('production_ids'):
            action = origins.get('production_ids').action_view()
        elif origins.get('sale_order_ids'):
            action = origins.get('sale_order_ids').action_view()
        elif origins.get('procurement_group_id'):
            action = origins.get('procurement_group_id').action_view()
        else:
            action = False
        return action
