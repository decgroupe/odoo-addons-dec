# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string='Production',
        domain=[("project_id", "!=", False)],
        groups="mrp.group_mrp_user",
    )
    production_partner_id = fields.Many2one(
        comodel_name='res.partner',
        related="production_id.partner_id",
        string="Production partner",
        store=True,
        compute_sudo=True,
        groups="mrp.group_mrp_user",
    )
    production_product_id = fields.Many2one(
        comodel_name='product.product',
        related="production_id.product_id",
        string="Production product",
        store=True,
        compute_sudo=True,
        groups="mrp.group_mrp_user",
    )

    @api.onchange("production_id")
    def onchange_production_id(self):
        for record in self:
            if not record.production_id:
                continue
            if record.production_id.project_id:
                record.project_id = record.production_id.project_id
            record.product_id = record.production_id.product_id
