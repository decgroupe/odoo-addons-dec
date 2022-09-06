# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging
import random

from datetime import datetime

from odoo import _, api, fields, models
from odoo.tools import html2plaintext, ormcache
from odoo.tools.float_utils import float_compare

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.tools_miscellaneous.tools.html_helper import (
    div, ul, li, small, b, format_hd
)
from odoo.addons.tools_miscellaneous.tools.material_design_colors import *

_logger = logging.getLogger(__name__)


def stockmove_state_to_emoji(state):
    res = state
    if res == 'draft':
        res = '🏳️'
    elif res == 'waiting':
        res = '⛓️'
    elif res == 'confirmed':
        res = '⏳'
    elif res == 'partially_available':
        res = '✴️'
    elif res == 'assigned':
        res = '✳️'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res


INDEX_1 = '50'
INDEX_2 = '100'
INDEX_3 = '200'

TREE_COLORS = [
    RED[INDEX_1],
    LIGHTBLUE[INDEX_1],
    YELLOW[INDEX_1],
    BLUEGREY[INDEX_1],
    PINK[INDEX_1],
    CYAN[INDEX_1],
    AMBER[INDEX_1],
    PURPLE[INDEX_1],
    TEAL[INDEX_1],
    ORANGE[INDEX_1],
    DEEPPURPLE[INDEX_1],
    GREEN[INDEX_1],
    DEEPORANGE[INDEX_1],
    INDIGO[INDEX_1],
    LIGHTGREEN[INDEX_1],
    BROWN[INDEX_1],
    BLUE[INDEX_1],
    LIME[INDEX_1],
    GREY[INDEX_1],
    RED[INDEX_2],
    LIGHTBLUE[INDEX_2],
    YELLOW[INDEX_2],
    BLUEGREY[INDEX_2],
    PINK[INDEX_2],
    CYAN[INDEX_2],
    AMBER[INDEX_2],
    PURPLE[INDEX_2],
    TEAL[INDEX_2],
    ORANGE[INDEX_2],
    DEEPPURPLE[INDEX_2],
    GREEN[INDEX_2],
    DEEPORANGE[INDEX_2],
    INDIGO[INDEX_2],
    LIGHTGREEN[INDEX_2],
    BROWN[INDEX_2],
    BLUE[INDEX_2],
    LIME[INDEX_2],
    GREY[INDEX_2],
    RED[INDEX_3],
    LIGHTBLUE[INDEX_3],
    YELLOW[INDEX_3],
    BLUEGREY[INDEX_3],
    PINK[INDEX_3],
    CYAN[INDEX_3],
    AMBER[INDEX_3],
    PURPLE[INDEX_3],
    TEAL[INDEX_3],
    ORANGE[INDEX_3],
    DEEPPURPLE[INDEX_3],
    GREEN[INDEX_3],
    DEEPORANGE[INDEX_3],
    INDIGO[INDEX_3],
    LIGHTGREEN[INDEX_3],
    BROWN[INDEX_3],
    BLUE[INDEX_3],
    LIME[INDEX_3],
    GREY[INDEX_3],
]


class StockMove(models.Model):
    _inherit = "stock.move"

    final_location = fields.Char(
        'Final location',
        compute='_compute_final_location',
        help='Get final location name',
        readonly=True,
    )
    action_view_created_item_visible = fields.Boolean(
        "Show Link to Created Item",
        compute='_compute_action_view_created_item_visible',
        readonly=True,
    )
    created_purchase_line_archive = fields.Integer(
        readonly=True,
        copy=False,
    )
    created_production_archive = fields.Integer(
        readonly=True,
        copy=False,
    )
    product_activity_id = fields.Many2one(
        'mail.activity',
        string="Related Activity",
        compute='_compute_product_activity_id',
    )
    state_emoji = fields.Char(compute='_compute_state_emoji')
    tree_fg_color = fields.Char(compute="_compute_colors", store=False)
    tree_bg_color = fields.Char(compute="_compute_colors", store=False)

    @api.multi
    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = stockmove_state_to_emoji(rec.state)

    @api.multi
    @api.depends("group_id")
    def _compute_colors(self):
        move_group = self.read_group(
            [('id', 'in', self.ids)], ['group_id'], ['group_id'], lazy=False
        )
        if len(move_group) > 1:
            colors = {}
            for i, group in enumerate(move_group):
                if group['group_id']:
                    group_id = group['group_id'][0]
                    if i < len(TREE_COLORS):
                        colors[group_id] = TREE_COLORS[i]
                    else:
                        colors[group_id] = '#FFFFFFFF'
            # Apply group colors per record
            for record in self:
                if record.group_id.id in colors:
                    record.tree_bg_color = colors[record.group_id.id][0]
                    record.tree_fg_color = colors[record.group_id.id][1]

    def _archive_purchase_line(self, values):
        if 'created_purchase_line_id' in values:
            if values['created_purchase_line_id']:
                values['created_purchase_line_archive'] = values[
                    'created_purchase_line_id']

    def _archive_production(self, values):
        if 'created_production_id' in values:
            if values['created_production_id']:
                values['created_production_archive'] = values[
                    'created_production_id']

    @api.model
    def create(self, values):
        self._archive_purchase_line(values)
        self._archive_production(values)
        stock_move = super().create(values)
        return stock_move

    @api.multi
    def write(self, values):
        self._archive_purchase_line(values)
        self._archive_production(values)
        if values.get('procure_method'):
            for move in self:
                _logger.info(
                    'Procure method of move %d for product %s set to %s',
                    move.id,
                    move.product_id.display_name,
                    values.get('procure_method'),
                )
        if values.get('state'):
            for move in self:
                _logger.info(
                    'State of move %d for product %s set to %s',
                    move.id,
                    move.product_id.display_name,
                    values.get('state'),
                )

        return super(StockMove, self).write(values)

    @api.depends('move_dest_ids', 'location_dest_id', 'product_id')
    def _compute_final_location(self):
        admin = self.user_has_groups('base.group_system')
        for rec in self:
            rec.final_location = rec.location_dest_id.name
            move_dest_id = rec.move_dest_ids and rec.move_dest_ids[0] or False
            if move_dest_id and rec.product_id.id == move_dest_id.product_id.id:
                if not move_dest_id.final_location:
                    # Force recompute since Odoo framework does not
                    # seems to do it properly ...
                    move_dest_id._compute_final_location()
                final_location = move_dest_id.final_location
                if final_location:
                    if admin:
                        rec.final_location += ' > ' + final_location
                    else:
                        rec.final_location = final_location

    @api.model
    @ormcache()
    def _get_product_template_ir_model_id(self):
        """This method returns an ID so it can be cached."""
        ir_model = self.env['ir.model'].sudo().search(
            [('model', '=', self.product_id.product_tmpl_id._name)]
        )
        return ir_model.id

    @api.model
    @ormcache()
    def _get_warning_activity_type_id(self):
        """This method returns an ID so it can be cached."""
        activity_type_id = self.env.ref('mail.mail_activity_data_warning')
        return activity_type_id.id

    @api.multi
    @api.depends('product_id')
    def _compute_product_activity_id(self):
        for move in self:
            domain = [
                ('res_id', '=', move.product_id.product_tmpl_id.id),
                (
                    'res_model_id',
                    '=',
                    move._get_product_template_ir_model_id(),
                ),
                (
                    'activity_type_id',
                    '=',
                    move._get_warning_activity_type_id(),
                ),
            ]
            activity = move.env['mail.activity'].search(domain, limit=1)
            move.product_activity_id = activity

    def action_view_created_item(self):
        """ Generate an action that will match the nearest object linked
        to this move. It is used to open a Purchase, Sale, etc.
        """
        self.ensure_one()
        action = False
        if self.created_purchase_line_id:
            action = self.created_purchase_line_id.order_id.action_view()
        elif self.purchase_line_id:
            action = self.purchase_line_id.order_id.action_view()
        elif action.created_production_id:
            action = self.created_production_id.action_view()
        elif self.production_id:
            action = self.production_id.action_view()
        elif self.product_activity_id:
            action = self.product_activity_id.action_view()
        return action

    def _compute_action_view_created_item_visible(self):
        for move in self:
            move.action_view_created_item_visible = \
                move.is_action_view_created_item_visible()

    def is_action_view_created_item_visible(self):
        self.ensure_one()
        return self.created_purchase_line_id \
            or self.purchase_line_id \
            or self.created_production_id \
            or self.production_id \
            or self.product_activity_id

    def action_open_stock_move_form(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Open Advanced Stock Move Form View',
            'display_name': ' Stock Move Advanced View',
            'res_model': 'stock.move',
            'context': '{}',
            'domain': '[]',
            'filter': False,
            'target': 'new',
            'view_id': self.env.ref('stock.view_move_form').id,
            'view_mode': 'form',
            'view_type': 'form',
        }
        action['res_id'] = self.id
        return action

    def get_head_desc(self):
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)
        head = '📦{0}'.format('Stock')
        if self.procure_method == 'make_to_order':
            head = '❓{0}'.format(_(self.procure_method))
        desc = '{0}{1}'.format(self.state_emoji, state)
        return head, desc

    def _get_stock_location(self, html=False):
        def try_append_loc(location, loc):
            if loc:
                if html:
                    loc = b(loc)
                location.append(loc)

        location = []
        try_append_loc(location, self.product_id.loc_rack)
        try_append_loc(location, self.product_id.loc_row)
        try_append_loc(location, self.product_id.loc_case)
        if not location:
            location = [_('Not Set')]
        head = '🗺️{0}'.format(_('Location'))
        desc = ' . '.join(location)
        return head, desc

    def _get_mto_status(self, html=False):
        res = []
        if self.created_purchase_line_id:
            head, desc = self.created_purchase_line_id.get_head_desc()
            res.append(format_hd(head, desc, html))
        elif self.purchase_line_id:
            head, desc = self.purchase_line_id.get_head_desc()
            res.append(format_hd(head, desc, html))
        elif self.created_production_id:
            head, desc = self.created_production_id.get_head_desc()
            res.append(format_hd(head, desc, html))
        elif self.production_id:
            head, desc = self.production_id.get_head_desc()
            res.append(format_hd(head, desc, html))
        elif self.product_activity_id:
            head, desc = self.product_activity_id.get_head_desc(self.product_id)
            res.append(format_hd(head, desc, html))
        else:
            res.append('❓(???)[{0}]'.format(self.state))
            # Since the current status is unknown, fallback using mts status
            # to print archive when exists
            res.extend(self._get_mts_status(html))

        # Add parent picking informations
        if len(self.move_orig_ids.ids) == 1:
            picking_id = self.move_orig_ids.picking_id
            if picking_id:
                head = '🚚 {0}'.format(self.move_orig_ids.picking_id.name)
                desc = datetime.strftime(
                    picking_id.scheduled_date, DEFAULT_SERVER_DATE_FORMAT
                )
                res.append(format_hd(head, desc, html))

        return res

    def _get_mts_status(self, html=False):
        res = []

        head, desc = self.get_head_desc()
        res.append(format_hd(head, desc, html))

        stock_location = self.env.ref('stock.stock_location_stock')

        # Print location only when destination moves are for stock
        # or if this move is the final one to stock
        if self.move_dest_ids:
            same_destination = all(
                x.id == stock_location.id
                for x in self.move_dest_ids.mapped('location_dest_id')
            )
            different_product = any(
                x.id != self.product_id.id
                for x in self.move_dest_ids.mapped('product_id')
            )
        else:
            same_destination = self.location_dest_id.id == stock_location.id
            different_product = False

        if same_destination or different_product:
            head, desc = self._get_stock_location(html)
            res.append(format_hd(head, desc, html=False))

        pre = False
        if self.created_purchase_line_archive and not self.created_purchase_line_id:
            pre = '♻️PO/'
        elif self.created_production_archive and not self.created_production_id:
            pre = '♻️MO/'
        if pre:
            res.append('{0}{1}'.format(pre, _('canceled')))

        if self.state not in (
            'assigned', 'done', 'cancel'
        ) and self.product_activity_id:
            head, desc = self.product_activity_id.get_head_desc()
            res.append(format_hd(head, desc, html))

        return res

    def _get_assignable_status(self, html=False):
        Quant = self.env['stock.quant']
        res = []
        if self.state in ('waiting', 'confirmed') and self.move_orig_ids \
            and all(
            orig.state in ('done', 'cancel') for orig in self.move_orig_ids
        ):
            rounding = self.product_id.uom_id.rounding
            needed_quantity = self.product_qty - sum(
                self.move_line_ids.mapped('product_qty')
            )
            available_quantity = Quant._get_available_quantity(
                self.product_id,
                self.location_id,
                strict=True,
                allow_negative=True,
            )
            if float_compare(
                needed_quantity,
                available_quantity,
                precision_rounding=rounding
            ) > 0:
                head = '⚠️{0}'.format(_('Reservation issue'))
                desc = '\n' + _('{0} needed but {1} available'
                               ).format(needed_quantity, available_quantity)
                hd = format_hd(head, desc, html)
                if html:
                    hd = div(hd, 'alert-warning')
                res.append(hd)
        return res

    def _get_upstreams(self, ensure_same_product=True):
        res = self.env['stock.move']
        if self.move_orig_ids:
            for move in self.move_orig_ids:
                if ensure_same_product:
                    if (move.product_id == self.product_id):
                        res += move
                else:
                    res += move
        return res

    def _format_status_header(self, status, html=False):
        product_type = dict(
            self._fields['product_type']._description_selection(self.env)
        ).get(self.product_type)

        # Add support for 'product_small_supply' module
        if 'small_supply' in self.product_id._fields and \
            self.product_type == 'product' and self.product_id.small_supply:
            # Translate field name to display string
            head = '{0}{1}'.format(
                '⛽', self.env['ir.translation'].get_field_string(
                    self.product_id._name
                )['small_supply']
            )
        else:
            head = '{0}{1}'.format(self.product_id.type_emoji, product_type)

        if self.user_has_groups('base.group_no_one'):
            head = '{0} ({1})'.format(head, self.id)
        status.insert(0, head)
        if html:
            list_as_html = ''.join(list(map(li, status)))
            return div(ul(list_as_html), 'd_move d_move_' + self.state)
        else:
            return '\n'.join(status)

    @api.multi
    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
