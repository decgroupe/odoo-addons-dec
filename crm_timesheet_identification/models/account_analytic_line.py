# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    lead_identification = fields.Char(
        string="CRM Identification",
        compute="_compute_lead_identification",
    )

    @api.depends('lead_id')
    def _compute_lead_identification(self):
        for rec in self.filtered('lead_id'):
            identifications = rec.lead_id._get_name_identifications()
            rec.lead_identification = ' / '.join(identifications)
