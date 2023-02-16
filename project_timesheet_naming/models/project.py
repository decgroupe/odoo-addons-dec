# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models


class Project(models.Model):
    _inherit = "project.project"

    def write(self, vals):
        if 'name' in vals:
            for rec in self.filtered('analytic_account_id'):
                if rec.name == rec.analytic_account_id.name:
                    rec.analytic_account_id.name = vals.get('name')
        return super().write(vals)
