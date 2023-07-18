# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import fields, models


class ResPartnerTraining(models.Model):
    _description = "Educational Training"
    _name = "res.partner.training"
    _order = "name"

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
        translate=False,
    )
    title = fields.Char(
        string="Title",
        translate=False,
    )
    specialty_ids = fields.One2many(
        comodel_name="res.partner.training.specialty",
        inverse_name="training_id",
        string="Specialties",
    )

    _sql_constraints = [
        ("name", "unique(name)", "Name must be unique !"),
    ]
