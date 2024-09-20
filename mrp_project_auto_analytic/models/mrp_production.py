# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _create_project(self, data):
        project_id = super()._create_project(data)
        # Set a default analytic parent account but only for projects created
        # from this function
        project_id.analytic_account_id.write(
            {"parent_id": self.env.ref("mrp_project.analytic_production").id}
        )
        return project_id
