# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    training_specialty_ids = fields.Many2many(
        comodel_name="res.partner.training.specialty",
        string="Specialties",
        help="Educational Training Specialties related to this order.",
    )
