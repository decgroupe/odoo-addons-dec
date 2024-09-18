# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SoftwareLicenseHardwareGroup(models.Model):
    """Group of all identical hardwares (by name)"""

    _name = "software.license.hardware.group"

    pass_id = fields.Many2one(
        comodel_name="software.license.pass",
        string="Pass",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        required=True,
        string="Identifier",
    )
    device_fqdn = fields.Char(
        string="Device FQDN",
        help="Fully Qualified Domain Name",
    )
    hardware_ids = fields.One2many(
        comodel_name="software.license.hardware",
        string="Hardware Identifiers",
        compute="_compute_hardwares",
    )
    hardware_count = fields.Integer(
        string="Number of Hardwares",
        compute="_compute_hardwares",
    )
    last_validation_date = fields.Datetime(
        string="Last Validation Date",
        compute="_compute_hardwares",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _logger.debug("Create hardware group: %s", vals)
        records = super().create(vals_list)
        return records

    def unlink(self):
        for rec in self:
            _logger.debug("Delete hardware group: %s", rec)
        return super().unlink()

    @api.depends(
        "pass_id",
        "pass_id.hardware_ids",
        "pass_id.hardware_ids.validation_date",
    )
    def _compute_hardwares(self):
        self.last_validation_date = False
        self.hardware_ids = False
        self.hardware_count = 0
        for rec in self:
            if rec.pass_id.hardware_ids:
                rec.hardware_ids = rec.pass_id.hardware_ids.filtered(
                    lambda x: x.name == rec.name
                )
                if rec.hardware_ids:
                    rec.hardware_count = len(rec.hardware_ids)
                    rec.last_validation_date = max(
                        rec.hardware_ids.mapped("validation_date")
                    )

    def action_deactivate(self):
        for rec in self:
            rec.hardware_ids.unlink()
