# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SoftwareLicense(models.Model):
    _inherit = "software.license"

    expiration_date = fields.Datetime(
        string="Expiration Date",
        tracking=True,
        help="If set, then after this date it will not be possible to "
        "proceed or renew any activation.",
    )
    max_allowed_hardware = fields.Integer(
        string="Maximum Activation Count",
        default=1,
        tracking=True,
        help="If more than 0, then the number of registered hardware "
        "identifiers will not be allowed to be greater than this value.",
    )

    @api.constrains("hardware_ids")
    def _check_max_allowed_hardware(self):
        if self.env.context.get("install_mode"):
            # Ignore constraint when loading XML data
            return
        for rec in self:
            if (
                rec.max_allowed_hardware > 0
                and len(rec.hardware_ids) > rec.max_allowed_hardware
            ):
                raise ValidationError(
                    _("Maximum hardware identifier count reached for license %s")
                    % (rec.display_name)
                )

    @api.constrains("hardware_ids", "expiration_date")
    def _check_expiration_date(self):
        if self.env.context.get("install_mode"):
            # Ignore constraint when loading XML data
            return
        for rec in self.filtered("expiration_date"):
            for hardware_id in rec.hardware_ids:
                if hardware_id.validation_date > rec.expiration_date:
                    raise ValidationError(_("Expiration date reached"))

    def check_expired(self):
        self.ensure_one()
        now = fields.Datetime.now()
        if self.expiration_date and now > self.expiration_date:
            return True
        return False

    def get_remaining_activation(self):
        self.ensure_one()
        if self.max_allowed_hardware <= 0:
            return -1
        else:
            return self.max_allowed_hardware - len(self.hardware_ids)

    def check_max_activation_reached(self, hardware_name):
        res = super().check_max_activation_reached(hardware_name)
        if self.max_allowed_hardware > 0:
            if hardware_name not in self.hardware_ids.mapped("name"):
                # If an hardware is already in our list, that means that
                # we don't care about max activation. Otherwise check for
                # already used slots count
                if len(self.hardware_ids) >= self.max_allowed_hardware:
                    res = True
        return res

    def get_hardwares_dict(self, filter_names):
        self.ensure_one()
        res = {}
        hardware_ids = self.hardware_ids
        # Apply filtering to select only wanted hardware identifiers
        if filter_names:
            hardware_ids = hardware_ids.filtered(lambda l: l.name in filter_names)
        for hardware_id in hardware_ids:
            hardware_data = hardware_id._prepare_export_vals(include_license_data=False)
            res[hardware_id.name] = hardware_data
        return res

    def _prepare_export_vals(self, include_activation_identifier=True):
        res = super()._prepare_export_vals(include_activation_identifier)
        res["expiration_date"] = fields.Datetime.to_string(self.expiration_date)
        return res
