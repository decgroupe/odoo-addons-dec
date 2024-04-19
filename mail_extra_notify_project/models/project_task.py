# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _get_assigned_extra_values(self, type):
        self.ensure_one()
        res = {}

        if self.sale_line_id:
            key, value = self._get_assigned_extra_field_value(
                self,
                "sale_line_id",
            )
            res[key] = value
            key, value = self._get_assigned_extra_field_value(
                self.sale_line_id.order_id,
                "partner_shipping_id",
            )
            res[key] = value
        # Zip
        key, value = self._get_assigned_extra_field_value(
            self,
            "partner_shipping_zip_id",
        )
        res[key] = value
        return res
