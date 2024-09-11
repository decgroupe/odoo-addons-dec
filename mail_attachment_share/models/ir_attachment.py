# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import uuid

from odoo import api, fields, models


class Attachment(models.Model):
    _inherit = "ir.attachment"

    sharing_token = fields.Char(
        string="Token",
        readonly=True,
    )
    sharing_link = fields.Char(
        string="Link",
        store=True,
        compute="_compute_sharing_link",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Attachment, self).create(vals_list)
        # records._generate_sharing_token()
        return records

    def _generate_sharing_token(self):
        for rec in self:
            rec.sharing_token = uuid.uuid4()

    def action_generate_sharing_token_from_wizard(self):
        self._generate_sharing_token()
        wizard_id = self.env.context.get("wizard_id")
        if wizard_id:
            return self.env["attachment.sharing"]._reopen(wizard_id)

    @api.depends("sharing_token")
    def _compute_sharing_link(self):
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        attachment_url = base_url + "/web/attachments/token/"
        for rec in self:
            if rec.sharing_token:
                rec.sharing_link = attachment_url + rec.sharing_token
            else:
                rec.sharing_link = False
