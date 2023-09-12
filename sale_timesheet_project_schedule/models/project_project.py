# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from odoo import api, models


class Project(models.Model):
    _inherit = "project.project"

    @api.depends("contract_ids", "contract_ids.state")
    def _compute_schedulable(self):
        super()._compute_schedulable()

    def _is_schedulable(self):
        res = super()._is_schedulable()
        if res and self.contract_ids:
            if all(c.state in ("done", "cancel") for c in self.contract_ids):
                res = False
        return res
