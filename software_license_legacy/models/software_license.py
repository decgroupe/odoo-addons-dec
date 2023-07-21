# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import logging

from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)

SYSTEM = "software_license_legacy.feature_property_system"

CLASSIC = "software_license_legacy.feature_value_system_classic"
CAVE = "software_license_legacy.feature_value_system_cave"
RIFT = "software_license_legacy.feature_value_system_rift"
VIVE = "software_license_legacy.feature_value_system_vive"


class SoftwareLicense(models.Model):
    _inherit = "software.license"

    main_hardware_id = fields.Many2one(
        comodel_name="software.license.hardware",
        string="Main Hardware",
        compute="_compute_main_hardware",
        store=True,
    )
    main_hardware_name = fields.Char(
        "Main Hardware Identifier",
        related="main_hardware_id.name",
    )
    main_hardware_dongle_identifier = fields.Integer(
        string="Dongle ID",
        help="Unique device ID set and given by then dongle manufacturer",
        related="main_hardware_id.dongle_identifier",
    )
    system_classic = fields.Boolean(
        "System Classic",
        compute="_compute_system",
        store=True,
    )
    system_cave = fields.Boolean(
        "System Cave",
        compute="_compute_system",
        store=True,
    )
    system_rift = fields.Boolean(
        "System Rift",
        compute="_compute_system",
        store=True,
    )
    system_vive = fields.Boolean(
        "System Vive",
        compute="_compute_system",
        store=True,
    )

    @api.depends("hardware_ids")
    def _compute_main_hardware(self):
        for rec in self:
            if rec.hardware_ids:
                rec.main_hardware_id = rec.hardware_ids[0]
            else:
                rec.main_hardware_id = False

    @api.depends("feature_ids")
    def _compute_system(self):
        property_system = self.env.ref(SYSTEM)
        value_system_classic = self.env.ref(CLASSIC)
        value_system_cave = self.env.ref(CAVE)
        value_system_rift = self.env.ref(RIFT)
        value_system_vive = self.env.ref(VIVE)
        self.system_classic = False
        self.system_cave = False
        self.system_rift = False
        self.system_vive = False
        for rec in self:
            for feature in rec.feature_ids:
                if feature.property_id == property_system:
                    if feature.value_id == value_system_classic:
                        rec.system_classic = True
                    elif feature.value_id == value_system_cave:
                        rec.system_cave = True
                    elif feature.value_id == value_system_rift:
                        rec.system_rift = True
                    elif feature.value_id == value_system_vive:
                        rec.system_vive = True
                    else:
                        _logger.info(
                            "Unknown system: %s",
                            feature.value_id.name,
                        )

    @api.model
    def create(self, vals):
        record = super().create(vals)

        def try_create_property_value(field_name, value_ref):
            if vals.get(field_name):
                sequence = len(record.feature_ids) + 1
                feature_vals = {
                    "license_id": record.id,
                    "sequence": sequence,
                    "property_id": self.env.ref(SYSTEM).id,
                    "value_id": self.env.ref(value_ref).id,
                }
                self.env["software.license.feature"].create(feature_vals)

        try_create_property_value("system_classic", CLASSIC)
        try_create_property_value("system_cave", CAVE)
        try_create_property_value("system_rift", RIFT)
        try_create_property_value("system_vive", VIVE)

        if vals.get("main_hardware_name"):
            hardware_vals = {
                "license_id": record.id,
                "name": vals.get("main_hardware_name"),
                "dongle_identifier": vals.get("main_hardware_dongle_identifier"),
            }
            self.env["software.license.hardware"].create(hardware_vals)

        return record

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            pass
        return res
