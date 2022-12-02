# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    training_specialty_ids = fields.Many2many(
        comodel_name='res.partner.training.specialty',
        string='Specialties',
        help='Educational Training Specialties of this partner.',
    )
