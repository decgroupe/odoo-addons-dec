# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2024


from odoo import models


class Project(models.Model):
    _inherit = "project.project"

    def _table_get_empty_so_lines(self):
        line_ids, order_ids = super()._table_get_empty_so_lines()
        # exclude lines linked to a pass (TODO: add sol.is_license_pass field)
        line_ids = set(
            self.env["sale.order.line"]
            .browse(line_ids)
            .filtered(lambda sol: not sol.license_pass_ids)
            .ids
        )
        return line_ids, order_ids
