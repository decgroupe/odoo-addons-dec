# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import json

from odoo import api, fields, models


class SoftwareLicenseHardware(models.Model):
    _name = "software.license.hardware"
    _description = "License Hardware"
    _order = "id desc"

    license_id = fields.Many2one(
        comodel_name="software.license",
        string="License",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        required=True,
        string="Identifier",
    )
    info = fields.Text(
        string="Informations",
    )
    device_name = fields.Char(
        string="Device Name",
        compute="_compute_device_info",
        store=True,
    )
    device_domain = fields.Char(
        string="Device Domain",
        compute="_compute_device_info",
        store=True,
    )
    device_fqdn = fields.Char(
        string="Device FQDN",
        help="Fully Qualified Domain Name",
        compute="_compute_device_info",
        store=True,
    )

    def _prepare_export_vals(self, include_license_data=True):
        if include_license_data:
            res = self.license_id._prepare_export_vals()
        else:
            res = {}
        res["hardware_identifier"] = self.name
        return res

    @api.depends("info")
    def _compute_device_info(self):
        self.device_name = False
        self.device_domain = False
        self.device_fqdn = False
        for rec in self.filtered("info"):
            data = json.loads(rec.info)
            # get telemetry node (fallback to params for older data)
            telemetry = data.get("telemetry", data.get("params"))
            if telemetry:
                network_information = telemetry.get("NetworkInformation")
                if network_information:
                    rec.device_name = network_information.get("HostName")
                    rec.device_domain = network_information.get("DomainName")
                if not rec.device_name:
                    system_info = telemetry.get("SystemInfo")
                    if system_info:
                        rec.device_name = system_info.get("deviceName")
                if rec.device_domain:
                    rec.device_fqdn = f"{rec.device_name}.{rec.device_domain}"
                else:
                    rec.device_fqdn = rec.device_name
