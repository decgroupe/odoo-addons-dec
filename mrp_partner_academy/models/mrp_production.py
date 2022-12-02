# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    partner_academy_id = fields.Many2one(
        comodel_name='res.partner.academy',
        related='commercial_partner_id.academy_id',
        string="Partner's Academy",
        store=True,
    )
