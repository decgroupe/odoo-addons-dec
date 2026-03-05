# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, fields, models


class ResPartnerTrainingSpecialty(models.Model):
    _description = "Educational Training Specialty"
    _name = "res.partner.training.specialty"
    _order = "name"
    _rec_name = "complete_name"
    _rec_names_search = ["complete_name", "search_name"]

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
        translate=False,
    )
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_names",
        store=True,
    )
    search_name = fields.Char(
        string="Search Name",
        compute="_compute_names",
        store=True,
    )
    acronym = fields.Char(
        string="Acronym",
        translate=False,
    )
    training_id = fields.Many2one(
        comodel_name="res.partner.training",
        string="Educational Training",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "train_name_uniq",
            "unique(training_id, name)",
            "Name must be unique !",
        ),
        (
            "train_acro_uniq",
            "unique(training_id, acronym)",
            "Acronym must be unique !",
        ),
    ]

    @api.depends("name", "acronym", "training_id", "training_id.name")
    def _compute_names(self):
        for rec in self:
            if rec.acronym:
                suffix = rec.acronym
            else:
                suffix = rec.name
            rec.complete_name = f"{rec.training_id.name} {suffix}"
            rec.search_name = f"{rec.training_id.name} {rec.acronym} {rec.name}"
