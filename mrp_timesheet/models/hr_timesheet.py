# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

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
    production_partner_name = fields.Char(
        related='production_partner_id.name',
        store=True,
    )
    production_product_id = fields.Many2one(
        comodel_name='product.product',
        related="production_id.product_id",
        string="Production product",
        store=True,
        compute_sudo=True,
        groups="mrp.group_mrp_user",
    )
    production_product_name = fields.Char(
        related='production_product_id.name',
        store=True,
        compute_sudo=True,
    )
    production_identification = fields.Char(
        string="Production Identification",
        compute="_compute_production_identification",
    )

    @api.depends('production_id')
    def _compute_production_identification(self):
        self.production_identification = False
        for rec in self.filtered('production_id'):
            identifications = rec.production_id._get_name_identifications()
            rec.production_identification = ' / '.join(identifications)

    @api.onchange("production_id")
    def onchange_production_id(self):
        if not self.production_id:
            return
        self.product_id = self.production_id.product_id
        if not self.project_id and self.production_id.project_id:
            self.project_id = self.production_id.project_id

    @api.onchange('project_id')
    def onchange_project_id(self):
        res = super().onchange_project_id()
        if 'domain' in res:
            filter = []
            if self.project_id:
                filter = [('project_id', '=', self.project_id.id)]
            res['domain']['production_id'] = filter
        return res
