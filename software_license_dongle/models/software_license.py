# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class SoftwareLicense(models.Model):
    _inherit = "software.license"

    dongle_product_id = fields.Integer(
        related="application_id.dongle_product_id",
        string="Dongle Product ID",
        store=True,
    )

    def _prepare_hardware_activation_vals(self, hardware):
        res = super()._prepare_hardware_activation_vals(hardware)
        dongle_identifier = self.env["software.license.hardware"].get_dongle_identifier(
            hardware
        )
        # A not zero value means that the hardware identifier comes from
        # a dongle, that means that we can increase the valididty
        if dongle_identifier > 0:
            res["dongle_identifier"] = dongle_identifier
        return res
