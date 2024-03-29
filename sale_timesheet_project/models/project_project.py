# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import models, api, fields


class Project(models.Model):
    _inherit = "project.project"

    contract_confirmation_date = fields.Datetime(
        string='Contract Confirmation Date',
        help="Date on which the contract was confirmed.",
        compute="_compute_contract_confirmation_date",
        store=True,
    )
    contract_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="project_id",
        string="Contract",
    )
    contract_count = fields.Integer(
        compute='_compute_contract_count',
        string='Contract Count',
        default=0,
        store=False,
    )

    @api.multi
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids)

    @api.multi
    @api.depends("contract_ids", "contract_ids.confirmation_date")
    def _compute_contract_confirmation_date(self):
        for rec in self:
            if rec.contract_ids:
                contract_id = rec.contract_ids[0]
                rec.contract_confirmation_date = contract_id.confirmation_date
            else:
                rec.contract_confirmation_date = False

    @api.multi
    def action_view_contracts(self):
        action = self.mapped('contract_ids').action_view()
        action['context'] = {}
        return action
