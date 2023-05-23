# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2023

from odoo import api, fields, models


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    res_model_model = fields.Char(
        related="res_model_id.model",
        string="Model Technical Name",
        readonly=True,
    )

    production_stage_ids = fields.One2many(
        comodel_name="mrp.production.stage",
        inverse_name="activity_type_id",
        string="Production Stages",
    )

    production_stage_id = fields.Many2one(
        comodel_name="mrp.production.stage",
        string="Production Stage",
        compute="_compute_production_stage_id",
    )

    @api.depends("production_stage_ids")
    def _compute_production_stage_id(self):
        for rec in self:
            rec.production_stage_id = rec.production_stage_ids[:1].id
