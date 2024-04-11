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

    _sql_constraints = [
        (
            "hardware_uniq",
            "unique(name,license_id)",
            "Hardware name must be unique per license!",
        ),
    ]

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

    @api.model
    def action_view_base(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "software_license.act_window_software_license_hardware"
        )
        return action

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            form = self.env.ref("software_license.software_license_hardware_form_view")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.id
        return action

    @api.model
    def get_hardware_ids(self, hardware, identifier=False, serial=False, limit=None):
        hardware_ids = self.env["software.license.hardware"]
        if hardware:
            domain = [("name", "=", hardware)]
            if identifier:
                domain += [
                    ("license_id.application_id.identifier", "=", identifier),
                ]
            if serial:
                domain += [("license_id.activation_identifier", "=", serial)]
            hardware_ids = hardware_ids.search(domain, limit=limit)
        return hardware_ids
