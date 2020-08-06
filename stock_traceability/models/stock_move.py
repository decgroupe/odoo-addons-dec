# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import logging

from odoo import _, api, fields, models
from odoo.tools import html2plaintext, ormcache

from .emoji_helper import (
    production_state_to_emoji,
    purchase_state_to_emoji,
    stockmove_state_to_emoji,
    activity_state_to_emoji,
    product_type_to_emoji,
)
from .html_helper import (div, ul, li, small, format_hd)

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    final_location = fields.Char(
        'Final location',
        compute='_compute_final_location',
        help='Get final location name',
        readonly=True,
    )
    action_view_created_item_visible = fields.Boolean(
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
        compute='_compute_product_activity_id',
    )

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
        for move in self:
            move.final_location = move.location_dest_id.name
            move_dest_id = move.move_dest_ids and move.move_dest_ids[0] or False
            if move_dest_id and move.product_id.id == move_dest_id.product_id.id:
                final_location = move_dest_id.final_location
                if final_location:
                    if admin:
                        move.final_location += ' > ' + final_location
                    else:
                        move.final_location = final_location

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
            move.product_activity_id = move.env['mail.activity'].search(
                [
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
                ],
                limit=1
            )

    def action_view_created_item(self):
        """ Generate an action that will match the nearest object linked
        to this move. It is used to open a Purchase, Sale, etc.
        """
        self.ensure_one()
        view = False
        if self.created_purchase_line_id:
            view = self.action_view_purchase(
                self.created_purchase_line_id.order_id.id
            )
        elif self.created_production_id:
            view = self.action_view_production(self.created_production_id.id)
        elif self.production_id:
            view = self.action_view_production(self.production_id.id)
        elif self.product_activity_id:
            view = self.action_view_activity(self.product_activity_id.id)
        return view

    def _compute_action_view_created_item_visible(self):
        for move in self:
            move.action_view_created_item_visible = \
                move.is_action_view_created_item_visible()

    def is_action_view_created_item_visible(self):
        self.ensure_one()
        return self.created_purchase_line_id \
            or self.created_production_id \
            or self.production_id \
            or self.product_activity_id

    def action_view_purchase(self, id):
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        form = self.env.ref('purchase.purchase_order_form')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = id
        return action

    def action_view_production(self, id):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        form = self.env.ref('mrp.mrp_production_form_view')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = id
        return action

    def action_view_activity(self, id):
        #action = self.env.ref('mail.mail_activity_action').read()[0]
        action = {
            'type': 'ir.actions.act_window',
            'name': 'My Action Name',
            'display_name': 'Activities',
            'res_model': 'mail.activity',
            'context': '{}',
            'domain': '[]',
            'filter': False,
            'target': 'current',
            'view_mode': 'form',
            'view_type': 'form',
        }
        form = self.env.ref('mail.mail_activity_view_form_popup')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = id
        return action

    def _get_production_status(self, production_id):
        p = production_id
        state = dict(p._fields['state']._description_selection(self.env)).get(
            p.state
        )
        head = '⚙️{0}'.format(p.name)
        desc = '{0}{1}'.format(production_state_to_emoji(p.state), state)
        return head, desc

    def _get_purchase_status(self, purchase_line_id):
        p = purchase_line_id
        state = dict(p._fields['state']._description_selection(self.env)).get(
            p.state
        )
        head = '🛒{0}'.format(p.order_id.name)
        desc = '{0}{1}'.format(purchase_state_to_emoji(p.state), state)
        return head, desc

    def _get_stock_status(self):
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)
        head = '📦{0}'.format('Stock')
        if self.procure_method == 'make_to_order':
            head = '❓{0}'.format(_(self.procure_method))
        desc = '{0}{1}'.format(stockmove_state_to_emoji(self.state), state)
        return head, desc

    def _get_activity_status(self, activity_id):
        a = activity_id
        state = dict(a._fields['state']._description_selection(self.env)).get(
            a.state
        )
        product_name = self.product_id.product_tmpl_id.display_name
        activity_text = html2plaintext(a.summary or a.note)
        activity_text = activity_text.replace(product_name, '')
        head = '⚠️{0}'.format(activity_text)
        desc = '{0}{1}'.format(activity_state_to_emoji(a.state), state)
        return head, desc

    def _get_mto_status(self, html=False):
        res = []
        if self.created_purchase_line_id:
            head, desc = self._get_purchase_status(
                self.created_purchase_line_id
            )
            res.append(format_hd(head, desc, html))
        elif self.created_production_id:
            head, desc = self._get_production_status(self.created_production_id)
            res.append(format_hd(head, desc, html))
        elif self.production_id:
            head, desc = self._get_production_status(self.production_id)
            res.append(format_hd(head, desc, html))
        elif self.product_activity_id:
            head, desc = self._get_activity_status(self.product_activity_id)
            res.append(format_hd(head, desc, html))
        else:
            res.append('❓(???)[{0}]'.format(self.state))
            # Since the current status is unknown, fallback using mts status
            # to print archive when exists
            res.extend(self._get_mts_status(html))
        return res

    def _get_mts_status(self, html=False):
        res = []

        head, desc = self._get_stock_status()
        res.append(format_hd(head, desc, html))

        pre = False
        if self.created_purchase_line_archive and not self.created_purchase_line_id:
            pre = '♻️PO/'
        elif self.created_production_archive and not self.created_production_id:
            pre = '♻️MO/'
        if pre:
            res.append('{0}{1}'.format(pre, _('canceled')))

        return res

    def _get_upstream(self, ensure_same_product=True):
        res = self.env['stock.move']
        if self.move_orig_ids:
            for move in self.move_orig_ids:
                if ensure_same_product:
                    if (move.product_id == self.product_id):
                        res = move
                        break
                else:
                    res = move
                    break
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

        head = '{0}{1}'.format(
            product_type_to_emoji(self.product_type),
            product_type,
        )
        if self.user_has_groups('base.group_no_one'):
            head = '{0} ({1})'.format(head, self.id)
        status.insert(0, head)
        if html:
            list_as_html = ''.join(list(map(li, status)))
            return div(ul(list_as_html), 'd_move d_move_' + self.state)
        else:
            return '\n'.join(status)
