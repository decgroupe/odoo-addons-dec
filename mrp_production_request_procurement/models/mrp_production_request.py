# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import api, fields, models, _


class MrpProductionRequest(models.Model):
    _inherit = 'mrp.production.request'

    production_name = fields.Char(
        string='Prefix',
        readonly=True,
    )
    use_common_procurement_group = fields.Boolean(
        string='Use Common Procurement Group',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
        help='If checked, when the first manufacturing order is created '
        'a procurement order is first created based on the MO sequence. '
    )
    common_procurement_group_id = fields.Many2one(
        string='Common Procurement Group',
        comodel_name='procurement.group',
        copy=False,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
    )

    @api.model
    def _create_sequence(self, vals):
        # Generate and store a unique name as base for all production orders
        if not vals.get('name') or vals.get('name') == '/':
            if vals.get('picking_type_id'):
                picking_type_id = self.env['stock.picking.type'].browse(
                    vals['picking_type_id']
                )
            else:
                picking_type_id = False
            vals['production_name'] = self._get_production_name(picking_type_id)
            vals['name'] = vals['production_name'].replace('MO', 'MR')
        vals = super()._create_sequence(vals)
        return vals

    @api.multi
    def button_approved(self):
        res = super().button_approved()
        for mr in self:
            if mr.use_common_procurement_group and not mr.common_procurement_group_id:
                mr.common_procurement_group_id = mr._create_procurement_group()
        return res

    @api.model
    def _get_production_name(self, picking_type_id):
        """This function helps to get a production name like it is done in the
        original code: addons/mrp/models/mrp_production.py
        Returns:
            [string]: Production name
        """
        if picking_type_id:
            res = picking_type_id.sequence_id.next_by_id()
        else:
            res = self.env['ir.sequence'].next_by_code('mrp.production')
        return res

    def _create_procurement_group(self):
        """This function helps to create a procurement group like it's done
        in the original code: addons/mrp/models/mrp_production.py
        Returns:
            [procurement.group]: [description]
        """
        self.ensure_one()
        procurement_group_id = self.env["procurement.group"].create(
            {'name': self.production_name}
        )
        return procurement_group_id
